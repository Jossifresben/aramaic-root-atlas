#!/usr/bin/env python3
"""Fetch public domain Bible translations for all OT books and merge into translations JSON.

Sources (all via bible.helloao.org, no rate limits):
- English: World English Bible (eng_web, public domain)
- Spanish: Reina-Valera 1909 (spa_r09, public domain)
- Hebrew: Westminster Leningrad Codex (hbo_wlc, public domain)

Arabic is fetched from quran.ksu.edu.sa / Smith-Van Dyke (public domain).

Usage:
    python scripts/fetch_ot_translations.py                # Fetch all books, all languages
    python scripts/fetch_ot_translations.py --books Psalms  # Single book
    python scripts/fetch_ot_translations.py --langs en       # English only
    python scripts/fetch_ot_translations.py --dry-run       # Preview without saving
"""

import argparse
import json
import os
import sys
import time

import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'translations')

# All 39 canonical OT books: display name -> (helloao book code, chapter count)
OT_BOOKS = {
    'Genesis': ('GEN', 50),
    'Exodus': ('EXO', 40),
    'Leviticus': ('LEV', 27),
    'Numbers': ('NUM', 36),
    'Deuteronomy': ('DEU', 34),
    'Joshua': ('JOS', 24),
    'Judges': ('JDG', 21),
    'Ruth': ('RUT', 4),
    '1 Samuel': ('1SA', 31),
    '2 Samuel': ('2SA', 24),
    '1 Kings': ('1KI', 22),
    '2 Kings': ('2KI', 25),
    '1 Chronicles': ('1CH', 29),
    '2 Chronicles': ('2CH', 36),
    'Ezra': ('EZR', 10),
    'Nehemiah': ('NEH', 13),
    'Esther': ('EST', 10),
    'Job': ('JOB', 42),
    'Psalms': ('PSA', 150),
    'Proverbs': ('PRO', 31),
    'Ecclesiastes': ('ECC', 12),
    'Song of Songs': ('SNG', 8),
    'Isaiah': ('ISA', 66),
    'Jeremiah': ('JER', 52),
    'Lamentations': ('LAM', 5),
    'Ezekiel': ('EZK', 48),
    'Daniel': ('DAN', 12),
    'Hosea': ('HOS', 14),
    'Joel': ('JOL', 3),
    'Amos': ('AMO', 9),
    'Obadiah': ('OBA', 1),
    'Jonah': ('JON', 4),
    'Micah': ('MIC', 7),
    'Nahum': ('NAM', 3),
    'Habakkuk': ('HAB', 3),
    'Zephaniah': ('ZEP', 3),
    'Haggai': ('HAG', 2),
    'Zechariah': ('ZEC', 14),
    'Malachi': ('MAL', 4),
}

# Translation IDs on bible.helloao.org
HELLOAO_TRANSLATIONS = {
    'en': 'eng_web',    # World English Bible
    'es': 'spa_r09',    # Reina-Valera 1909
    'he': 'hbo_wlc',    # Westminster Leningrad Codex (Masoretic Hebrew)
    'ar': 'arb_vdv',    # Arabic Van Dyck Bible
}


def fetch_chapter_helloao(translation_id: str, book_code: str, chapter: int) -> dict:
    """Fetch a chapter from bible.helloao.org. Returns {verse_num: text}."""
    url = f"https://bible.helloao.org/api/{translation_id}/{book_code}/{chapter}.json"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        verses = {}
        for item in data.get('chapter', {}).get('content', []):
            if item.get('type') == 'verse':
                v_num = item['number']
                parts = []
                for part in item.get('content', []):
                    if isinstance(part, str):
                        parts.append(part)
                    elif isinstance(part, dict):
                        parts.append(part.get('text', ''))
                text = ' '.join(parts).strip()
                if text:
                    verses[v_num] = text
        return verses
    except Exception as e:
        print(f"    ERROR fetching {book_code} ch{chapter}: {e}", file=sys.stderr)
        return {}


def fetch_book(book_ref_name: str, book_code: str, max_chapters: int, lang: str,
               dry_run: bool = False) -> dict:
    """Fetch all chapters of a book. Returns {reference: text}."""
    results = {}
    for ch in range(1, max_chapters + 1):
        if dry_run:
            continue

        translation_id = HELLOAO_TRANSLATIONS[lang]
        verses = fetch_chapter_helloao(translation_id, book_code, ch)

        for v_num, text in verses.items():
            ref = f"{book_ref_name} {ch}:{v_num}"
            results[ref] = text

        # Rate limiting — gentle
        time.sleep(0.15)

    return results


def main():
    parser = argparse.ArgumentParser(description='Fetch OT translations from public domain Bibles')
    parser.add_argument('--books', nargs='*', help='Books to fetch (default: all 39)')
    parser.add_argument('--langs', nargs='*', default=['en', 'es', 'he', 'ar'],
                        help='Languages (default: en es he ar)')
    parser.add_argument('--dry-run', action='store_true', help='Preview without fetching')
    parser.add_argument('--skip-existing', action='store_true',
                        help='Skip books that already have translations')
    args = parser.parse_args()

    books = {}
    if args.books:
        for b in args.books:
            if b in OT_BOOKS:
                books[b] = OT_BOOKS[b]
            else:
                print(f"Unknown book: {b}. Available: {list(OT_BOOKS.keys())}", file=sys.stderr)
                sys.exit(1)
    else:
        books = OT_BOOKS

    for lang in args.langs:
        if lang not in HELLOAO_TRANSLATIONS:
            print(f"Unsupported language: {lang}. Use one of: {list(HELLOAO_TRANSLATIONS.keys())}",
                  file=sys.stderr)
            continue

        trans_file = os.path.join(DATA_DIR, f'translations_{lang}.json')

        # Load existing translations
        if os.path.exists(trans_file):
            with open(trans_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        else:
            existing = {}

        source = f"{HELLOAO_TRANSLATIONS[lang]} (bible.helloao.org)"
        print(f"\n=== {lang.upper()} — {source} ===")
        print(f"Existing translations: {len(existing)}")

        total_new = 0
        for book_ref_name, (book_code, max_chapters) in books.items():
            # Check if book already has translations
            if args.skip_existing:
                sample_ref = f"{book_ref_name} 1:1"
                if sample_ref in existing:
                    print(f"  {book_ref_name}: already present, skipping")
                    continue

            print(f"  {book_ref_name} ({max_chapters} ch)...", end=' ', flush=True)

            new_verses = fetch_book(book_ref_name, book_code, max_chapters, lang, args.dry_run)
            if new_verses:
                existing.update(new_verses)
                total_new += len(new_verses)
                print(f"{len(new_verses)} verses")
            else:
                print("0 verses" if not args.dry_run else "dry run")

        if not args.dry_run and total_new > 0:
            with open(trans_file, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False)
            print(f"\nSaved {total_new} new verses to {trans_file}")
            print(f"Total translations now: {len(existing)}")
        elif args.dry_run:
            total_ch = sum(ch for _, ch in books.values())
            print(f"\nDry run: would fetch {total_ch} chapters for {lang}")


if __name__ == '__main__':
    main()
