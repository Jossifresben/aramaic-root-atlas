#!/usr/bin/env python3
"""
Fetch Targum Writings (Aramaic translations of the Ketuvim / Writings) from
Sefaria API.

Covers Psalms, Job, Proverbs, Ruth, Lamentations, Ecclesiastes, Song of
Songs, Esther, 1 Chronicles, and 2 Chronicles — ten Sefaria indices.
Source: Sefaria API (per-version license, verified at fetch time — see
LICENSE_REPORT printed at the end of the run).
Text is in Hebrew square script with vocalized Aramaic vocabulary.

Mirrors scripts/fetch_targum_jonathan.py. Chapters are fetched until an
empty chapter is returned, so we don't hardcode chapter counts.

Excludes Targum Sheni on Esther (only Sefaria version has license
"unknown" — see docs/SPEC-v3.3-corpus-expansion.md).
"""

import csv
import json
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

SEFARIA_API = "https://www.sefaria.org/api/texts"

# Writings in Peshitta-OT book order: (display book, Sefaria index title, book_order)
# Display names MUST match data/corpora/peshitta_ot.csv exactly so books align
# cross-corpus in the parallel viewer / diachronic views. book_order values are
# copied from peshitta_ot.csv for the same books.
WRITINGS = [
    ("1 Chronicles",   "Targum of I Chronicles",           13),
    ("2 Chronicles",   "Targum of II Chronicles",          14),
    ("Esther",         "Aramaic Targum to Esther",         17),
    ("Job",            "Aramaic Targum to Job",            18),
    ("Psalms",         "Aramaic Targum to Psalms",         19),
    ("Proverbs",       "Aramaic Targum to Proverbs",       20),
    ("Ecclesiastes",   "Aramaic Targum to Ecclesiastes",   21),
    ("Song of Songs",  "Aramaic Targum to Song of Songs",  22),
    ("Lamentations",   "Aramaic Targum to Lamentations",   25),
    ("Ruth",           "Aramaic Targum to Ruth",            8),
]

MAX_CHAPTERS = 155  # safety cap; Psalms (150) is the longest

# Licenses acceptable for ingestion: exact "Public Domain" or any Creative
# Commons variant (CC0, CC-BY, CC-BY-SA, ...).
ALLOWED_LICENSES = {"Public Domain"}


def is_allowed_license(license_str):
    if not license_str:
        return False
    if license_str in ALLOWED_LICENSES:
        return True
    return license_str.strip().upper().startswith("CC")


def clean_text(text):
    """Remove HTML tags, entities, and normalize."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
    text = re.sub(r'\([^)]+\)', '', text)  # Remove ketiv (balanced, same verse)
    # Strip any orphan brackets/parens left over — e.g. a Sefaria parenthetical
    # that opens in one verse and closes in the next is never balanced within a
    # single verse string, so a lone '(' or ')' would otherwise stay glued to a
    # real word token and corrupt its root extraction.
    text = re.sub(r'[()\[\]]', '', text)  # Remove qere brackets + orphan parens
    # Remove invisible directionality marks (LRM/RLM) — the Mikraot Gedolot
    # Job targum embeds U+200E after each ת״א variant-reading marker, and an
    # invisible control glued to a token would corrupt its root extraction.
    text = re.sub(r'[‎‏]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def strip_diacritics(text):
    """Remove Hebrew niqqud/cantillation, keep consonants."""
    result = []
    for ch in text:
        cp = ord(ch)
        if 0x0591 <= cp <= 0x05AF:
            continue
        if 0x05B0 <= cp <= 0x05BD:
            continue
        if cp in (0x05BF, 0x05C1, 0x05C2, 0x05C4, 0x05C5, 0x05C7):
            continue
        if cp == 0x05BE:  # maqaf -> space
            result.append(' ')
            continue
        if cp == 0x05C3:  # sof pasuq
            continue
        result.append(ch)
    return re.sub(r'\s+', ' ', ''.join(result)).strip()


def fetch_chapter(sefaria_name, chapter):
    """Fetch a chapter from Sefaria. Returns (verses, license, version_title).

    verses is a list of verse strings (he); license/version_title come from
    the heLicense/heVersionTitle fields of the response (the Aramaic-text
    version, since we request language=he). All three are None/[] on error.
    """
    encoded = urllib.parse.quote(sefaria_name)
    url = f"{SEFARIA_API}/{encoded}.{chapter}?language=he"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AramaicRootAtlas/1.0"})
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        he = data.get('he', [])
        he = he if isinstance(he, list) else []
        return he, data.get('heLicense'), data.get('heVersionTitle')
    except Exception as e:
        print(f"  ERROR {sefaria_name} ch{chapter}: {e}", file=sys.stderr)
        return [], None, None


def main():
    output_path = "data/corpora/targum_writings.csv"
    verses = []
    license_report = []  # (index_title, version_title, license)
    errors = []  # (book_name, chapter, reason)

    print("=== Fetching Targum Writings from Sefaria API ===")

    for book_name, sefaria_name, book_order in WRITINGS:
        print(f"  {book_name}...", end='', flush=True)
        book_verses = 0
        empty_streak = 0
        license_checked = False

        for ch in range(1, MAX_CHAPTERS + 1):
            chapter_data, he_license, he_version_title = fetch_chapter(sefaria_name, ch)
            time.sleep(0.3)

            if not chapter_data:
                # Stop at the first empty chapter once we've already got content.
                if book_verses > 0:
                    break
                empty_streak += 1
                if empty_streak >= 2:
                    break
                continue
            empty_streak = 0

            # Verify license on the first chapter that returns content. Abort
            # loudly rather than silently ingesting a text with an unclear
            # or non-open license (e.g. Targum Sheni on Esther, "unknown",
            # which is why it is excluded from this corpus entirely).
            if not license_checked:
                license_checked = True
                if not is_allowed_license(he_license):
                    print()
                    print(
                        f"FATAL: '{sefaria_name}' has license '{he_license}' "
                        f"(version: {he_version_title}) — not Public Domain or CC. "
                        f"Aborting fetch.",
                        file=sys.stderr,
                    )
                    sys.exit(1)
                license_report.append((sefaria_name, he_version_title, he_license))

            for v_num, raw_text in enumerate(chapter_data, 1):
                if not raw_text:
                    continue
                cleaned = clean_text(raw_text)
                consonantal = strip_diacritics(cleaned)
                if not consonantal.strip():
                    continue

                reference = f"{book_name} {ch}:{v_num}"
                verses.append({
                    'book_order': book_order,
                    'book': book_name,
                    'chapter': ch,
                    'verse': v_num,
                    'reference': reference,
                    'syriac': consonantal,
                })
                book_verses += 1

        if not license_checked:
            errors.append((book_name, None, "no content / license never verified"))

        print(f" {book_verses} verses")

    print(f"\nTotal verses: {len(verses)}")

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['book_order', 'book', 'chapter', 'verse', 'reference', 'syriac'])
        writer.writeheader()
        for v in verses:
            writer.writerow(v)

    print(f"Saved to {output_path}")
    total_words = sum(len(v['syriac'].split()) for v in verses)
    unique_words = len(set(w for v in verses for w in v['syriac'].split()))
    print(f"Words: {total_words} total, {unique_words} unique")

    print("\n=== License report ===")
    for index_title, version_title, license_str in license_report:
        print(f"  {index_title} | {version_title} | {license_str}")

    if errors:
        print("\n=== Errors / empty books ===", file=sys.stderr)
        for book_name, ch, reason in errors:
            print(f"  {book_name} ch{ch}: {reason}", file=sys.stderr)


if __name__ == '__main__':
    main()
