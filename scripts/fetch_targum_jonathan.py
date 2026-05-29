#!/usr/bin/env python3
"""
Fetch Targum Jonathan (Aramaic translation of the Prophets) from Sefaria API.

Covers the Former Prophets (Joshua–II Kings) and Latter Prophets
(Isaiah, Jeremiah, Ezekiel, and the Twelve) — ~21 books.
Source: Sefaria API (CC-BY-SA)
Text is in Hebrew square script with vocalized Aramaic vocabulary.

Mirrors scripts/fetch_targum_onkelos.py. Chapters are fetched until an
empty chapter is returned, so we don't hardcode chapter counts (the
Hebrew-Bible numbering of Joel and Malachi differs from the Christian
numbering, and fetch-until-empty sidesteps that entirely).
"""

import csv
import json
import re
import ssl
import sys
import time
import urllib.request

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

SEFARIA_API = "https://www.sefaria.org/api/texts"

# Prophets in canonical Nevi'im order: (display book, Sefaria index name, book_order)
PROPHETS = [
    ("Joshua",       "Targum_Jonathan_on_Joshua",       1),
    ("Judges",       "Targum_Jonathan_on_Judges",       2),
    # Display names use Arabic numerals to match Peshitta OT ("1 Samuel"),
    # so books align cross-corpus in the parallel viewer / diachronic views.
    # Sefaria index names keep Roman numerals.
    ("1 Samuel",     "Targum_Jonathan_on_I_Samuel",     3),
    ("2 Samuel",     "Targum_Jonathan_on_II_Samuel",    4),
    ("1 Kings",      "Targum_Jonathan_on_I_Kings",      5),
    ("2 Kings",      "Targum_Jonathan_on_II_Kings",     6),
    ("Isaiah",       "Targum_Jonathan_on_Isaiah",       7),
    ("Jeremiah",     "Targum_Jonathan_on_Jeremiah",     8),
    ("Ezekiel",      "Targum_Jonathan_on_Ezekiel",      9),
    ("Hosea",        "Targum_Jonathan_on_Hosea",        10),
    ("Joel",         "Targum_Jonathan_on_Joel",         11),
    ("Amos",         "Targum_Jonathan_on_Amos",         12),
    ("Obadiah",      "Targum_Jonathan_on_Obadiah",      13),
    ("Jonah",        "Targum_Jonathan_on_Jonah",        14),
    ("Micah",        "Targum_Jonathan_on_Micah",        15),
    ("Nahum",        "Targum_Jonathan_on_Nahum",        16),
    ("Habakkuk",     "Targum_Jonathan_on_Habakkuk",     17),
    ("Zephaniah",    "Targum_Jonathan_on_Zephaniah",    18),
    ("Haggai",       "Targum_Jonathan_on_Haggai",       19),
    ("Zechariah",    "Targum_Jonathan_on_Zechariah",    20),
    ("Malachi",      "Targum_Jonathan_on_Malachi",      21),
]

MAX_CHAPTERS = 70  # safety cap; Isaiah (66) is the longest


def clean_text(text):
    """Remove HTML tags, entities, and normalize."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
    text = re.sub(r'\([^)]+\)', '', text)  # Remove ketiv
    text = re.sub(r'[\[\]]', '', text)  # Remove qere brackets
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
    """Fetch a chapter from Sefaria. Returns list of verse strings (he)."""
    url = f"{SEFARIA_API}/{sefaria_name}.{chapter}?language=he"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AramaicRootAtlas/1.0"})
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        he = data.get('he', [])
        return he if isinstance(he, list) else []
    except Exception as e:
        print(f"  ERROR {sefaria_name} ch{chapter}: {e}", file=sys.stderr)
        return []


def main():
    output_path = "data/corpora/targum_jonathan.csv"
    verses = []

    print("=== Fetching Targum Jonathan from Sefaria API ===")

    for book_name, sefaria_name, book_order in PROPHETS:
        print(f"  {book_name}...", end='', flush=True)
        book_verses = 0
        empty_streak = 0

        for ch in range(1, MAX_CHAPTERS + 1):
            chapter_data = fetch_chapter(sefaria_name, ch)
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


if __name__ == '__main__':
    main()
