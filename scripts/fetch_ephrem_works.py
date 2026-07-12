#!/usr/bin/env python3
"""Fetch Ephrem's "Other Works" (everything by Ephrem in the srophe/syriac-corpus
TEI collection that is NOT the Carmina Nisibena, which is already ingested as
ephrem_nisibis) and convert to Aramaic Root Atlas corpus CSV format.

Source: https://github.com/srophe/syriac-corpus (CC BY 4.0), data/tei/*.xml
(632 TEI files). Selection: <author ref="http://syriaca.org/person/13"> in the
TEI header (Ephrem the Syrian), EXCLUDING file numbers 259-331 (Carmina
Nisibena, already in ephrem_nisibis.csv).

Output: data/corpora/ephrem_works.csv

TEI structure varies by work:
  - Hymn cycles (e.g. "Nativity N") use the same stanza structure as
    ephrem_nisibis: <div type="section"> = stanza, direct <l> children = lines.
  - Prose works (the five Discourses to Hypatius, and the standalone treatises
    Against Bardaisan's Domnus / Against Marcion / Against Bardaisan /
    On Virginity / Against Mani) have NO <div type="section"> at all. Instead
    they use <p> paragraphs (sometimes flat under <div type="text">, sometimes
    nested inside numbered <div type="part"> subsections). For these, every
    <p> found under a <div type="text"> is treated as one "verse" (a running
    paragraph index) — there is no finer natural subdivision available in the
    source markup.

Acquisition modes (in priority order), to avoid hammering the GitHub API:
  1. --local-dir DIR   : DIR is (or contains) an already-extracted copy of the
                         repo, i.e. DIR/data/tei/*.xml exists, or DIR itself
                         IS the data/tei directory.
  2. --tarball PATH     : PATH is a downloaded copy of
                         https://github.com/srophe/syriac-corpus/archive/refs/heads/main.tar.gz
                         It is extracted to a temp dir and then handled like
                         --local-dir.
  3. (fallback, no local input given): list data/tei/ once via the GitHub
     Contents API (a single request, same pattern as fetch_ephrem_nisibis.py),
     then fetch each candidate file individually from
     https://raw.githubusercontent.com/srophe/syriac-corpus/main/data/tei/NNN.xml
     This mode makes ~632 HTTP requests and should only be used when no local
     copy of the tarball is available.
"""
import argparse
import csv
import os
import re
import sys
import tarfile
import tempfile
import time
import requests
from lxml import etree

GITHUB_CONTENTS = "https://api.github.com/repos/srophe/syriac-corpus/contents/data/tei"
RAW_BASE = "https://raw.githubusercontent.com/srophe/syriac-corpus/main/data/tei"
TARBALL_URL = "https://github.com/srophe/syriac-corpus/archive/refs/heads/main.tar.gz"

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'corpora')
OUT_CSV = os.path.join(OUT_DIR, 'ephrem_works.csv')

# TEI namespace
TEI_NS = 'http://www.tei-c.org/ns/1.0'
NS = {'tei': TEI_NS}

# Syriac Unicode block: U+0700-U+074F
SYRIAC_RE = re.compile(r'[܀-ݏ]')
# Refrain lines start with the word "ܥܽܘܢܝܳܐ"/"ܥܽܘܢܺܝܬܳܐ" ("response") — spelling
# varies across files, so match on the shared stem.
REFRAIN_PREFIX = 'ܥܽܘܢ'
# Bare acrostic-letter markers some rubric-only files use in place of proper
# <div type="section"> stanza breaks, e.g. "ܐ 1", "ܬ 41" — a single Syriac
# token followed by nothing but a number.
MARKER_RE = re.compile(r'^[܀-ݏ]+\s+\d+\s*$')

AUTHOR_REF = 'http://syriaca.org/person/13'
EXCLUDE_START = 259
EXCLUDE_END = 331

ORDINALS = {
    'First': 1, 'Second': 2, 'Third': 3, 'Fourth': 4, 'Fifth': 5,
    'Sixth': 6, 'Seventh': 7, 'Eighth': 8, 'Ninth': 9, 'Tenth': 10,
}
HYPATIUS_RE = re.compile(
    r'^(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth)\s+'
    r'Discourse to Hypatius', re.IGNORECASE)
CYCLE_NUM_RE = re.compile(r'^(.+?)\s+(\d+)$')

FALLBACK_BOOK = 'Ephrem'

# The five standalone prose treatises (Mitchell, "Prose Refutations" vol. 2)
# carry no (cycle, number) title pattern; map each explicitly to a short
# single-chapter book name (chapter = 1). Note 535 gets a "(Prose)"
# disambiguator: Ephrem also wrote a *hymn cycle* On Virginity that DSC may
# add someday, and the two must not collapse into one book.
TREATISE_BOOKS = {
    532: 'Against Domnus',
    533: 'Against Marcion',
    534: 'Against Bardaisan',
    535: 'On Virginity (Prose)',
    536: 'Against Mani',
}


# ---------------------------------------------------------------------------
# Acquisition
# ---------------------------------------------------------------------------

def _find_tei_dir(root_dir: str) -> str:
    """Given a directory that is either the tei dir itself, a repo root, or an
    extracted tarball root (with one nested subdir), locate data/tei."""
    candidates = [
        os.path.join(root_dir, 'data', 'tei'),
        root_dir,
    ]
    for c in candidates:
        if os.path.isdir(c):
            digit_xmls = [f for f in os.listdir(c)
                          if f.endswith('.xml') and f[:-4].isdigit()
                          and os.path.isfile(os.path.join(c, f))]
            if len(digit_xmls) > 50:
                return c
    # extracted tarball case: root_dir/syriac-corpus-main/data/tei
    if os.path.isdir(root_dir):
        for entry in os.listdir(root_dir):
            sub = os.path.join(root_dir, entry, 'data', 'tei')
            if os.path.isdir(sub):
                return sub
    raise FileNotFoundError(f"Could not locate data/tei under {root_dir}")


def iter_local_files(tei_dir: str):
    """Yield (num, xml_bytes) for every NNN.xml file in tei_dir, ascending."""
    entries = []
    for fn in os.listdir(tei_dir):
        if not fn.endswith('.xml'):
            continue
        stem = fn[:-4]
        if stem.isdigit():
            entries.append((int(stem), os.path.join(tei_dir, fn)))
    entries.sort(key=lambda x: x[0])
    for num, path in entries:
        with open(path, 'rb') as f:
            yield num, f.read()


def iter_remote_files():
    """Fallback: list data/tei/ once via GitHub API, then fetch each raw file.

    Slow (one HTTP request per candidate file) — only used when neither
    --local-dir nor --tarball is supplied.
    """
    print("No --local-dir/--tarball given; falling back to GitHub Contents API "
          "+ per-file raw.githubusercontent.com fetches (slow).", file=sys.stderr)
    resp = requests.get(GITHUB_CONTENTS, timeout=30)
    resp.raise_for_status()
    items = resp.json()
    nums = []
    for item in items:
        if item['type'] != 'file' or not item['name'].endswith('.xml'):
            continue
        stem = item['name'][:-4]
        if stem.isdigit():
            nums.append(int(stem))
    nums.sort()
    print(f"Found {len(nums)} candidate TEI files.", file=sys.stderr)
    for num in nums:
        url = f"{RAW_BASE}/{num}.xml"
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
        except Exception as e:
            print(f"  SKIP {num}: {e}", file=sys.stderr)
            continue
        time.sleep(0.1)
        yield num, r.content


def get_file_iterator(args):
    if args.local_dir:
        tei_dir = _find_tei_dir(args.local_dir)
        print(f"Using local dir: {tei_dir}", file=sys.stderr)
        return iter_local_files(tei_dir)
    if args.tarball:
        tmp_root = tempfile.mkdtemp(prefix='syriac-corpus-')
        print(f"Extracting {args.tarball} to {tmp_root} ...", file=sys.stderr)
        with tarfile.open(args.tarball, 'r:gz') as tf:
            tf.extractall(tmp_root)
        tei_dir = _find_tei_dir(tmp_root)
        print(f"Using extracted tarball dir: {tei_dir}", file=sys.stderr)
        return iter_local_files(tei_dir)
    return iter_remote_files()


# ---------------------------------------------------------------------------
# Header inspection / selection
# ---------------------------------------------------------------------------

def is_ephrem_authored(root_el, author_ref: str) -> bool:
    authors = root_el.findall('.//tei:teiHeader//tei:titleStmt/tei:author', NS)
    return any(a.get('ref') == author_ref for a in authors)


def get_title(root_el) -> str:
    title_el = root_el.find('.//tei:teiHeader//tei:title[@level="a"]', NS)
    if title_el is None:
        return ''
    text = ''.join(title_el.itertext())
    return re.sub(r'\s+', ' ', text).strip()


def clean_title_en(title: str) -> str:
    """Strip trailing ' - <syriac...>' suffix some titles carry."""
    m = SYRIAC_RE.search(title)
    if m:
        title = title[:m.start()]
    return re.sub(r'\s+', ' ', title).rstrip(' -').strip()


def parse_title_to_book_chapter(title_en: str):
    """Return (book, chapter) or (None, None) if the title doesn't parse into
    a recognizable (cycle, number) pattern."""
    title_en = clean_title_en(title_en)

    m = CYCLE_NUM_RE.match(title_en)
    if m:
        return m.group(1).strip(), int(m.group(2))

    m = HYPATIUS_RE.match(title_en)
    if m:
        return 'To Hypatius', ORDINALS[m.group(1).capitalize()]

    return None, None


# ---------------------------------------------------------------------------
# Body text extraction
# ---------------------------------------------------------------------------

def _elem_text(elem) -> str:
    """Extract visible Syriac text from an element, skipping child element
    text but keeping child tails — excludes editorial content inside <note>,
    <supplied>, <unclear>, sub-line labels, etc. while keeping milestone-tail
    text (e.g. around <pb/> page breaks). Whitespace (including the newlines
    / indentation the pretty-printed source XML wraps long <p> text in) is
    collapsed to single spaces, matching the convention of the other corpus
    CSVs (no embedded newlines in the `syriac` field)."""
    parts = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        if child.tail:
            parts.append(child.tail)
    return re.sub(r'\s+', ' ', ''.join(parts)).strip()


def extract_rows(root_el, book: str, chapter: int):
    """Return (rows, kind) where kind is 'stanza' or 'para' (or 'empty')."""
    body = root_el.find(f'.//{{{TEI_NS}}}body')
    if body is None:
        return [], 'empty'

    section_divs = [d for d in body.iter(f'{{{TEI_NS}}}div') if d.get('type') == 'section']

    rows = []
    if section_divs:
        for stanza_n, sdiv in enumerate(section_divs, start=1):
            lines = []
            for child in sdiv:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if tag == 'l':
                    text = _elem_text(child)
                    if text and not text.startswith(REFRAIN_PREFIX) and SYRIAC_RE.search(text):
                        lines.append(text)
            syriac = ' '.join(lines).strip()
            if not syriac or not SYRIAC_RE.search(syriac):
                continue
            rows.append({
                'book': book, 'chapter': chapter, 'verse': stanza_n, 'syriac': syriac,
            })
        return rows, 'stanza'

    # No section divs -> prose. Collect every <p> that lives under a
    # <div type="text"> (this also picks up <p>s nested inside <div
    # type="part"> subsections), skipping headings/rubrics that sit outside
    # the text div.
    text_divs = [d for d in body.iter(f'{{{TEI_NS}}}div') if d.get('type') == 'text']
    if not text_divs:
        text_divs = [body]

    paragraphs = []
    seen = set()
    for td in text_divs:
        for p in td.iter(f'{{{TEI_NS}}}p'):
            if id(p) not in seen:
                seen.add(id(p))
                paragraphs.append(p)

    verse_n = 0
    for p in paragraphs:
        text = _elem_text(p)
        if not text or not SYRIAC_RE.search(text):
            continue
        verse_n += 1
        rows.append({
            'book': book, 'chapter': chapter, 'verse': verse_n, 'syriac': text,
        })
    if rows:
        return rows, 'para'

    # Last resort: some files have neither <div type="section"> stanzas nor
    # <p> paragraphs — just loose <l> lines directly under a rubric/text div
    # (e.g. an acrostic hymn transcribed without stanza markup, only bare
    # Syriac-letter acrostic markers like "ܐ 1", "ܬ 41"). Treat each
    # surviving line as its own verse; skip refrains and bare markers.
    lines = []
    seen_l = set()
    for td in text_divs:
        for l in td.iter(f'{{{TEI_NS}}}l'):
            if id(l) not in seen_l:
                seen_l.add(id(l))
                lines.append(l)

    verse_n = 0
    seen_marker = False
    for l in lines:
        text = _elem_text(l)
        if not text or not SYRIAC_RE.search(text):
            continue
        if text.startswith(REFRAIN_PREFIX):
            continue
        if MARKER_RE.match(text):
            seen_marker = True
            continue
        # Rubric labels (melody directions etc., e.g. "ܫܽܘܚܠܳܦ ܩܳܠܳܐ" "change
        # of melody") precede the acrostic-marked content and are short —
        # skip any very short line that appears before the first marker.
        if not seen_marker and len(text.split()) <= 3:
            continue
        verse_n += 1
        rows.append({
            'book': book, 'chapter': chapter, 'verse': verse_n, 'syriac': text,
        })
    return rows, ('line' if rows else 'empty')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--local-dir', help='Path to an already-extracted syriac-corpus checkout '
                                         '(repo root, data/tei dir, or extracted-tarball root)')
    ap.add_argument('--tarball', help='Path to a downloaded syriac-corpus main.tar.gz to extract')
    ap.add_argument('--out', default=OUT_CSV, help='Output CSV path')
    ap.add_argument('--author-ref', default=AUTHOR_REF)
    ap.add_argument('--exclude-start', type=int, default=EXCLUDE_START)
    ap.add_argument('--exclude-end', type=int, default=EXCLUDE_END)
    ap.add_argument('--report', help='Optional path to write a plain-text selection report')
    args = ap.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    selected_docs = []  # (num, title_en, book, chapter, fell_back)
    licence_ok_count = 0
    licence_checked = 0
    parse_errors = []
    fallback_running_index = 0

    all_rows = []
    book_first_seen_order = {}
    next_book_order = 1

    for num, xml_bytes in get_file_iterator(args):
        if args.exclude_start <= num <= args.exclude_end:
            continue
        try:
            root_el = etree.fromstring(xml_bytes)
        except etree.XMLSyntaxError as e:
            parse_errors.append((num, str(e)))
            continue

        if not is_ephrem_authored(root_el, args.author_ref):
            continue

        title_en = get_title(root_el)
        fell_back = False
        if num in TREATISE_BOOKS:
            book, chapter = TREATISE_BOOKS[num], 1
        else:
            book, chapter = parse_title_to_book_chapter(title_en)
            if book is None:
                fallback_running_index += 1
                book, chapter = FALLBACK_BOOK, fallback_running_index
                fell_back = True

        # licence spot-check (cheap, on every selected doc)
        licence_checked += 1
        licence_text = ''
        lic_el = root_el.find('.//tei:teiHeader//tei:licence', NS)
        if lic_el is not None:
            licence_text = re.sub(r'\s+', ' ', ''.join(lic_el.itertext()))
        if 'CC BY' in licence_text or 'by/4.0' in (lic_el.get('target') if lic_el is not None else ''):
            licence_ok_count += 1

        rows, kind = extract_rows(root_el, book, chapter)

        if book not in book_first_seen_order:
            book_first_seen_order[book] = next_book_order
            next_book_order += 1
        book_order = book_first_seen_order[book]

        for r in rows:
            r['book_order'] = book_order
            r['reference'] = f"{r['book']} {r['chapter']}:{r['verse']}"
        all_rows.extend(rows)

        selected_docs.append({
            'num': num, 'title': title_en, 'book': book, 'chapter': chapter,
            'fell_back': fell_back, 'kind': kind, 'n_rows': len(rows),
        })
        print(f"  [{num}] {title_en!r:60s} -> {book} {chapter} ({kind}, {len(rows)} rows)",
              file=sys.stderr)

    all_rows.sort(key=lambda r: (r['book_order'], r['chapter'], r['verse']))

    with open(args.out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f, fieldnames=['book_order', 'book', 'chapter', 'verse', 'reference', 'syriac'])
        writer.writeheader()
        for r in all_rows:
            writer.writerow({
                'book_order': r['book_order'], 'book': r['book'], 'chapter': r['chapter'],
                'verse': r['verse'], 'reference': r['reference'], 'syriac': r['syriac'],
            })

    print(f"\nSelected {len(selected_docs)} documents, wrote {len(all_rows)} rows to {args.out}",
          file=sys.stderr)
    print(f"Licence check: {licence_ok_count}/{licence_checked} selected docs carry a CC BY licence element",
          file=sys.stderr)
    if parse_errors:
        print(f"Parse errors ({len(parse_errors)}): {parse_errors}", file=sys.stderr)

    degenerate = [d for d in selected_docs if d['kind'] == 'para' and d['n_rows'] < 10]
    if degenerate:
        print("\nFlagged as low-granularity prose (few, large paragraphs):", file=sys.stderr)
        for d in degenerate:
            print(f"  [{d['num']}] {d['title']!r} -> {d['n_rows']} rows", file=sys.stderr)

    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(f"Selected {len(selected_docs)} documents\n\n")
            for d in selected_docs:
                f.write(f"{d['num']}\t{d['title']}\t-> {d['book']} {d['chapter']}"
                        f"\t({d['kind']}, {d['n_rows']} rows{', FALLBACK' if d['fell_back'] else ''})\n")


if __name__ == '__main__':
    main()
