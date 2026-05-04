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

# Roman numeral to integer for hymn title parsing
ROMAN = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
    'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
    'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
    'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20,
    'XXI': 21, 'XXII': 22, 'XXIII': 23, 'XXIV': 24, 'XXV': 25,
    'XXVI': 26, 'XXVII': 27, 'XXVIII': 28, 'XXIX': 29, 'XXX': 30,
    'XXXI': 31, 'XXXII': 32, 'XXXIII': 33, 'XXXIV': 34, 'XXXV': 35,
    'XXXVI': 36, 'XXXVII': 37, 'XXXVIII': 38, 'XXXIX': 39, 'XL': 40,
    'XLI': 41, 'XLII': 42, 'XLIII': 43, 'XLIV': 44, 'XLV': 45,
    'XLVI': 46, 'XLVII': 47, 'XLVIII': 48, 'XLIX': 49, 'L': 50,
    'LI': 51, 'LII': 52, 'LIII': 53, 'LIV': 54, 'LV': 55,
    'LVI': 56, 'LVII': 57, 'LVIII': 58, 'LIX': 59, 'LX': 60,
    'LXI': 61, 'LXII': 62, 'LXIII': 63, 'LXIV': 64, 'LXV': 65,
    'LXVI': 66, 'LXVII': 67, 'LXVIII': 68, 'LXIX': 69, 'LXX': 70,
    'LXXI': 71, 'LXXII': 72, 'LXXIII': 73,
}


def list_nisibis_files() -> list[tuple[str, int]]:
    """Return (download_url, file_number) for Carmen Nisibena TEI files (259-331)."""
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
                results.append((url, num))
        except ValueError:
            pass
    return sorted(results, key=lambda x: x[1])


def get_hymn_number(root_el, file_num: int) -> int:
    """Extract hymn number from TEI. Use title div n= attribute, fallback to file offset."""
    # Try <div type="title" n="N">
    for div in root_el.iter('{http://www.tei-c.org/ns/1.0}div'):
        if div.get('type') == 'title':
            n_attr = div.get('n', '')
            try:
                return int(n_attr)
            except ValueError:
                pass
            # Try parsing the text content "Nisibis XLVI"
            ab = div.find('{http://www.tei-c.org/ns/1.0}ab')
            if ab is not None:
                text = (ab.text or '').strip()
                m = re.match(r'Nisibis\s+([IVXLC]+)$', text)
                if m:
                    roman = m.group(1)
                    if roman in ROMAN:
                        return ROMAN[roman]
                m2 = re.match(r'Nisibis\s+(\d+)$', text)
                if m2:
                    return int(m2.group(1))
    # Fallback: file 259 = hymn 1, 260 = 2, etc.
    return file_num - 258


def parse_tei(xml_bytes: bytes, file_num: int) -> list[dict]:
    """Parse one TEI XML file → list of stanza dicts."""
    rows = []
    try:
        root_el = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as e:
        print(f"  XML error: {e}", file=sys.stderr)
        return rows

    hymn_n = get_hymn_number(root_el, file_num)

    # Find all <div type="section"> elements — these are the stanzas
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    section_divs = []
    for div in root_el.iter(f'{{{tei_ns}}}div'):
        if div.get('type') == 'section':
            section_divs.append(div)

    for sdiv in section_divs:
        raw_sn = sdiv.get('n', '1')
        try:
            stanza_n = int(raw_sn)
        except ValueError:
            stanza_n = 1

        # Collect <l> elements that are direct children (not nested in sub-divs)
        # We skip <head> elements; only <l> elements count as lines
        lines = []
        for child in sdiv:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag == 'l':
                text = ''.join(child.itertext()).strip()
                # Skip lines that are clearly refrains (start with ܥܽܘܢܺܝܬܳܐ:)
                if text and not text.startswith('ܥܽܘܢܺܝܬܳܐ'):
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
    file_list = list_nisibis_files()
    if not file_list:
        print("ERROR: No Nisibis files found (259-331).", file=sys.stderr)
        sys.exit(1)
    print(f"Found {len(file_list)} files (file numbers {file_list[0][1]}-{file_list[-1][1]}).")

    all_rows = []
    for i, (url, file_num) in enumerate(file_list, 1):
        fname = url.split('/')[-1]
        print(f"  [{i}/{len(file_list)}] {fname}", end='', flush=True)
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            print(f" SKIP (download error): {e}", file=sys.stderr)
            continue
        rows = parse_tei(resp.content, file_num)
        print(f" → {len(rows)} stanzas")
        all_rows.extend(rows)
        time.sleep(0.15)

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
