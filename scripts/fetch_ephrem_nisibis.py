#!/usr/bin/env python3
"""Fetch Hymns on Nisibis (Carmen Nisibena) from Digital Syriac Corpus GitHub
and convert to Aramaic Root Atlas corpus CSV format.

Source: https://github.com/srophe/syriac-corpus (CC BY 4.0)
Output: data/corpora/ephrem_nisibis.csv

TEI structure (actual, from inspection):
  <body>
    <div type="title" n="1">...</div>      <!-- hymn number -->
    <div type="melody">...</div>           <!-- skip -->
    <div type="body" xml:lang="syr">      <!-- optional wrapper in some files -->
      <div type="superscript">...</div>   <!-- skip -->
      <div type="section" n="1">          <!-- stanza = verse -->
        <l>...</l>
        <l>...</l>
      </div>
      <div type="response">...</div>      <!-- skip (refrain, not a stanza) -->
      <div type="section" n="2">...
    </div>
  </body>

Each file = one hymn. Files 259-331 in data/tei/ = Nisibis hymns 1-73.
Hymn numbers are assigned sequentially (1-based) from the sorted file list,
which maps directly to the scholarly 1-73 canon.
"""
import csv
import os
import re
import sys
import time
import requests
from lxml import etree

GITHUB_CONTENTS = "https://api.github.com/repos/srophe/syriac-corpus/contents/data/tei"
RAW_BASE = "https://raw.githubusercontent.com/srophe/syriac-corpus/main/data/tei"
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'corpora')
OUT_CSV = os.path.join(OUT_DIR, 'ephrem_nisibis.csv')

# TEI namespace
NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

# Syriac Unicode block: U+0700–U+074F
SYRIAC_RE = re.compile(r'[܀-ݏ]')


def list_nisibis_files() -> list[str]:
    """Return sorted download URLs for Carmen Nisibena TEI files (259-331)."""
    resp = requests.get(GITHUB_CONTENTS, timeout=30)
    resp.raise_for_status()
    items = resp.json()
    results = []
    for item in items:
        if item['type'] != 'file' or not item['name'].endswith('.xml'):
            continue
        try:
            num = int(item['name'].replace('.xml', ''))
            if 259 <= num <= 331:
                url = f"{RAW_BASE}/{item['name']}"
                results.append((num, url))
        except ValueError:
            pass
    # Sort by file number so hymn_num assignment (1-based index) is stable
    results.sort(key=lambda x: x[0])
    return [url for _, url in results]


def _line_text(elem) -> str:
    """Extract visible Syriac text from a <l> element, skipping child element text.

    Uses only direct text and tail nodes so that editorial content inside child
    elements (<note>, <supplied>, <unclear>, sub-line labels, etc.) is excluded.
    """
    parts = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        # skip text inside child elements (notes, supplied, unclear, etc.)
        if child.tail:
            parts.append(child.tail)
    return ''.join(parts).strip()


def parse_tei_file(xml_bytes: bytes, hymn_n: int) -> list[dict]:
    """Parse one TEI XML file → list of stanza dicts.

    hymn_n is the 1-based sequential hymn number assigned from the sorted file
    list; the TEI n= attributes are intentionally ignored to avoid mis-numbering.
    """
    rows = []
    try:
        root_el = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as e:
        print(f"  XML error: {e}", file=sys.stderr)
        return rows

    # Find all <div type="section"> elements — these are the stanzas
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    section_divs = []
    for div in root_el.iter(f'{{{tei_ns}}}div'):
        if div.get('type') == 'section':
            section_divs.append(div)

    for stanza_n, sdiv in enumerate(section_divs, start=1):
        # Collect <l> elements that are direct children (not nested in sub-divs)
        # Use _line_text() to skip editorial content inside child elements.
        # Skip any line that contains no Syriac characters (pure editorial notes).
        lines = []
        for child in sdiv:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag == 'l':
                text = _line_text(child)
                # Skip lines that are clearly refrains (start with ܥܽܘܢܺܝܬܳܐ:)
                # Also skip lines with no Syriac text (e.g. "Line Missing" editorial notes)
                if text and not text.startswith('ܥܽܘܢܺܝܬܳܐ') and SYRIAC_RE.search(text):
                    lines.append(text)

        syriac = ' '.join(lines).strip()
        if not syriac or not SYRIAC_RE.search(syriac):
            continue

        rows.append({
            'book_order': 1,
            'book': 'Nisibis',
            'chapter': hymn_n,
            'verse': stanza_n,
            'reference': f'Nisibis {hymn_n}:{stanza_n}',
            'syriac': syriac,
        })

    return rows


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Fetching file list from DSC GitHub (data/tei/)...")
    urls = list_nisibis_files()
    if not urls:
        print("ERROR: No Nisibis files found (259-331).", file=sys.stderr)
        sys.exit(1)
    print(f"Found {len(urls)} files.")

    all_rows = []
    for hymn_num, url in enumerate(urls, start=1):
        fname = url.split('/')[-1]
        print(f"  [{hymn_num}/{len(urls)}] {fname}", end='', flush=True)
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            print(f" SKIP (download error): {e}", file=sys.stderr)
            continue
        rows = parse_tei_file(resp.content, hymn_n=hymn_num)
        print(f" → {len(rows)} stanzas")
        all_rows.extend(rows)
        time.sleep(0.2)

    # Sort by hymn then stanza
    all_rows.sort(key=lambda r: (r['chapter'], r['verse']))

    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f, fieldnames=['book_order', 'book', 'chapter', 'verse', 'reference', 'syriac'])
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nWrote {len(all_rows)} stanzas to {OUT_CSV}")
    if all_rows:
        print(f"Sample row: {all_rows[0]}")


if __name__ == '__main__':
    main()
