#!/usr/bin/env python3
"""
Fetch Biblical Aramaic passages from Sefaria API and produce a CSV
compatible with AramaicCorpus.

Biblical Aramaic passages:
  - Daniel 2:4b-7:28 (the main BA section)
  - Ezra 4:8-6:18
  - Ezra 7:12-26
  - Genesis 31:47 (two Aramaic words)
  - Jeremiah 10:11 (single verse)

Source: Westminster Leningrad Codex via Sefaria (CC-BY-SA)
"""

import csv
import json
import re
import ssl
import sys
import time
import urllib.request

# macOS often has SSL cert issues with Python
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

SEFARIA_API = "https://www.sefaria.org/api/texts"

# Biblical Aramaic passages
BA_PASSAGES = [
    # (book, start_chapter, start_verse, end_chapter, end_verse, book_order)
    ("Genesis", 31, 47, 31, 47, 1),
    ("Jeremiah", 10, 11, 10, 11, 24),
    ("Daniel", 2, 4, 7, 28, 27),
    ("Ezra", 4, 8, 6, 18, 15),
    ("Ezra", 7, 12, 7, 26, 15),
]

# Book order for sorting (matching Peshitta OT order)
BOOK_ORDER = {
    "Genesis": 1, "Exodus": 2, "Leviticus": 3, "Numbers": 4,
    "Deuteronomy": 5, "Joshua": 6, "Judges": 7, "Ruth": 8,
    "1 Samuel": 9, "2 Samuel": 10, "1 Kings": 11, "2 Kings": 12,
    "1 Chronicles": 13, "2 Chronicles": 14, "Ezra": 15, "Nehemiah": 16,
    "Esther": 17, "Job": 18, "Psalms": 19, "Proverbs": 20,
    "Ecclesiastes": 21, "Song of Songs": 22, "Isaiah": 23,
    "Jeremiah": 24, "Lamentations": 25, "Ezekiel": 26, "Daniel": 27,
    "Hosea": 28, "Joel": 29, "Amos": 30, "Obadiah": 31,
    "Jonah": 32, "Micah": 33, "Nahum": 34, "Habakkuk": 35,
    "Zephaniah": 36, "Haggai": 37, "Zechariah": 38, "Malachi": 39,
}


def clean_sefaria_text(text):
    """Remove HTML tags, ketiv/qere markers, and normalize whitespace."""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove HTML entities
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
    # Remove ketiv (parenthesized) forms, keep qere (bracketed)
    text = re.sub(r'\([^)]+\)', '', text)
    text = re.sub(r'[\[\]]', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def strip_hebrew_diacritics(text):
    """Remove Hebrew niqqud/cantillation marks, keep consonants."""
    # Hebrew cantillation marks: U+0591-U+05AF
    # Hebrew points (niqqud): U+05B0-U+05BD, U+05BF, U+05C1-U+05C2, U+05C4-U+05C5, U+05C7
    # Maqaf: U+05BE (keep as separator? or strip)
    # Meteg: U+05BD
    result = []
    for ch in text:
        cp = ord(ch)
        # Skip cantillation marks
        if 0x0591 <= cp <= 0x05AF:
            continue
        # Skip niqqud
        if 0x05B0 <= cp <= 0x05BD:
            continue
        if cp in (0x05BF, 0x05C1, 0x05C2, 0x05C4, 0x05C5, 0x05C7):
            continue
        # Convert maqaf to space
        if cp == 0x05BE:
            result.append(' ')
            continue
        # Keep sof pasuq as period equivalent (or strip)
        if cp == 0x05C3:
            continue
        result.append(ch)
    # Normalize whitespace
    return re.sub(r'\s+', ' ', ''.join(result)).strip()


def fetch_chapter(book, chapter):
    """Fetch a single chapter from Sefaria API."""
    # Sefaria uses book names without spaces for some books
    sefaria_book = book.replace(" ", "_")
    # For "1 Samuel" etc, Sefaria uses "I_Samuel"
    sefaria_book = sefaria_book.replace("1_", "I_").replace("2_", "II_")

    url = f"{SEFARIA_API}/{sefaria_book}.{chapter}?language=he"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AramaicRootAtlas/1.0"})
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data.get('he', [])
    except Exception as e:
        print(f"  ERROR fetching {book} {chapter}: {e}", file=sys.stderr)
        return []


def fetch_biblical_aramaic():
    """Fetch all Biblical Aramaic passages and return as list of verse dicts."""
    verses = []

    for book, start_ch, start_v, end_ch, end_v, book_order in BA_PASSAGES:
        print(f"Fetching {book} {start_ch}:{start_v}-{end_ch}:{end_v}...")

        for ch in range(start_ch, end_ch + 1):
            chapter_verses = fetch_chapter(book, ch)
            if not chapter_verses:
                print(f"  WARNING: No data for {book} ch{ch}")
                continue

            # Determine verse range for this chapter
            v_start = start_v if ch == start_ch else 1
            v_end = end_v if ch == end_ch else len(chapter_verses)

            for v_num in range(v_start, min(v_end + 1, len(chapter_verses) + 1)):
                idx = v_num - 1  # 0-based index
                if idx >= len(chapter_verses):
                    break

                raw_text = chapter_verses[idx]
                if not raw_text:
                    continue

                # Clean HTML and ketiv/qere
                cleaned = clean_sefaria_text(raw_text)
                # Strip diacritics to get consonantal text
                consonantal = strip_hebrew_diacritics(cleaned)

                if not consonantal.strip():
                    continue

                reference = f"{book} {ch}:{v_num}"
                verses.append({
                    'book_order': book_order,
                    'book': book,
                    'chapter': ch,
                    'verse': v_num,
                    'reference': reference,
                    'syriac': consonantal,  # Hebrew square script, stored in 'syriac' column for compatibility
                    'script': 'hebrew',  # metadata: this is Hebrew square script
                })

            # Be polite to Sefaria API
            time.sleep(0.3)

        print(f"  Got {sum(1 for v in verses if v['book'] == book)} verses from {book}")

    return verses


def main():
    output_path = "data/corpora/biblical_aramaic.csv"

    print("=== Fetching Biblical Aramaic from Sefaria API ===")
    verses = fetch_biblical_aramaic()

    print(f"\nTotal verses fetched: {len(verses)}")

    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['book_order', 'book', 'chapter', 'verse', 'reference', 'syriac'])
        writer.writeheader()
        for v in verses:
            writer.writerow({
                'book_order': v['book_order'],
                'book': v['book'],
                'chapter': v['chapter'],
                'verse': v['verse'],
                'reference': v['reference'],
                'syriac': v['syriac'],
            })

    print(f"Saved to {output_path}")

    # Print word count
    total_words = sum(len(v['syriac'].split()) for v in verses)
    unique_words = len(set(w for v in verses for w in v['syriac'].split()))
    print(f"Words: {total_words} total, {unique_words} unique")

    # Show sample verses
    print("\n--- Sample verses ---")
    for v in verses[:3]:
        print(f"{v['reference']}: {v['syriac'][:80]}")
    if len(verses) > 3:
        print("...")
        for v in verses[-2:]:
            print(f"{v['reference']}: {v['syriac'][:80]}")


if __name__ == '__main__':
    main()
