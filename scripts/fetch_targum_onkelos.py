#!/usr/bin/env python3
"""
Fetch Targum Onkelos (Aramaic translation of the Torah) from Sefaria API.

Covers Genesis through Deuteronomy (~5,845 verses).
Source: Sefaria API (CC-BY-NC)
Text is in Hebrew square script with Aramaic vocabulary.
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

# Torah books with Sefaria Onkelos names and chapter counts
TORAH_BOOKS = [
    ("Genesis", "Onkelos_Genesis", 50, 1),
    ("Exodus", "Onkelos_Exodus", 40, 2),
    ("Leviticus", "Onkelos_Leviticus", 27, 3),
    ("Numbers", "Onkelos_Numbers", 36, 4),
    ("Deuteronomy", "Onkelos_Deuteronomy", 34, 5),
]


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
    """Fetch a chapter from Sefaria."""
    url = f"{SEFARIA_API}/{sefaria_name}.{chapter}?language=he"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AramaicRootAtlas/1.0"})
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data.get('he', [])
    except Exception as e:
        print(f"  ERROR {sefaria_name} ch{chapter}: {e}", file=sys.stderr)
        return []


def main():
    output_path = "data/corpora/targum_onkelos.csv"
    verses = []

    print("=== Fetching Targum Onkelos from Sefaria API ===")

    for book_name, sefaria_name, num_chapters, book_order in TORAH_BOOKS:
        print(f"  {book_name} ({num_chapters} ch)...", end='', flush=True)
        book_verses = 0

        for ch in range(1, num_chapters + 1):
            chapter_data = fetch_chapter(sefaria_name, ch)
            if not chapter_data:
                continue

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

            time.sleep(0.3)

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
