#!/usr/bin/env python3
"""Generate cognate entries for Syriac roots that have no cognates yet.

Sends batches of uncovered roots to Claude, which:
1. Filters out non-roots (particles, proclitic combos, proper nouns, pronouns)
2. For genuine triliteral roots, generates Hebrew & Arabic cognates

Requires ANTHROPIC_API_KEY environment variable.

Usage:
    python scripts/generate_new_cognates.py                    # Process all
    python scripts/generate_new_cognates.py --dry-run          # Preview
    python scripts/generate_new_cognates.py --batch-size 20    # Custom batch size
    python scripts/generate_new_cognates.py --min-occ 5        # Min occurrences
    python scripts/generate_new_cognates.py --max-batches 10   # Limit batches
"""

import argparse
import json
import os
import re
import sys
import time

import anthropic

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ROOTS_DIR = os.path.join(DATA_DIR, 'roots')
COGNATES_PATH = os.path.join(ROOTS_DIR, 'cognates.json')

SYSTEM_PROMPT = """\
You are a Semitic linguistics expert specializing in Syriac (Aramaic), Hebrew, and Arabic. \
You will receive a batch of Syriac three-letter patterns extracted from the Peshitta Bible \
(Old and New Testaments). Many of these are NOT real triliteral roots — they may be:
- Proclitic + particle combos (e.g., ܘܠܐ = w+la "and not", ܕܠܐ = d+la "that not")
- Pronominal suffix patterns (e.g., ܠܘܗ = l+wh "to him", ܒܘܗ = b+wh "in him")
- Proper nouns (e.g., ܡܘܣ = Moses, ܐܝܠ = Israel)
- Function words, conjunctions, particles
- Demonstrative/relative pronoun forms

Your job:
1. FILTER: identify which patterns are genuine Syriac triliteral verbal roots
2. GENERATE: for each real root, provide Hebrew and Arabic cognates

For each real root, provide:
- root_syriac: the Syriac root in Unicode
- gloss_es: Spanish gloss (1-3 words)
- gloss_en: English gloss (1-3 words)
- hebrew: array of 2-4 cognate words with:
  - word: Hebrew script with nikkud
  - transliteration: academic transliteration
  - meaning_es: Spanish meaning
  - meaning_en: English meaning
- arabic: array of 2-4 cognate words with:
  - word: Arabic script with tashkil
  - transliteration: academic transliteration
  - meaning_es: Spanish meaning
  - meaning_en: English meaning

RESPOND WITH ONLY valid JSON. Format:
{
  "roots": {
    "x-y-z": {
      "root_syriac": "ܝܝܝ",
      "gloss_es": "...",
      "gloss_en": "...",
      "hebrew": [{"word": "...", "transliteration": "...", "meaning_es": "...", "meaning_en": "..."}],
      "arabic": [{"word": "...", "transliteration": "...", "meaning_es": "...", "meaning_en": "..."}]
    }
  },
  "skipped": ["pattern1 (reason)", "pattern2 (reason)"]
}

The "skipped" array lists patterns that are NOT real triliteral roots, with brief reason.
"""


def load_corpus_and_extractor():
    """Load the full corpus and build root index."""
    sys.path.insert(0, BASE_DIR)
    from aramaic_core import AramaicCorpus
    from aramaic_core.extractor import RootExtractor

    corpus = AramaicCorpus()
    corpus.add_corpus('peshitta_nt', 'Peshitta NT',
                      os.path.join(DATA_DIR, 'corpora', 'peshitta_nt.csv'))
    corpus.add_corpus('peshitta_ot', 'Peshitta OT',
                      os.path.join(DATA_DIR, 'corpora', 'peshitta_ot.csv'))
    corpus.load()

    extractor = RootExtractor(corpus, ROOTS_DIR)
    extractor.build_index()

    return corpus, extractor


def load_cognates():
    """Load existing cognates."""
    if os.path.exists(COGNATES_PATH):
        with open(COGNATES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"roots": {}}


def find_uncovered_roots(extractor, cognates_data, min_occ=3):
    """Find roots that don't have cognate entries yet."""
    sys.path.insert(0, BASE_DIR)
    from aramaic_core.characters import transliterate_syriac

    existing_syriac = set()
    for key, entry in cognates_data.get('roots', {}).items():
        sr = entry.get('root_syriac', '')
        if sr:
            existing_syriac.add(sr)

    all_entries = extractor.get_all_roots()
    uncovered = []
    for entry in all_entries:
        if entry.root not in existing_syriac and entry.total_occurrences >= min_occ:
            translit = transliterate_syriac(entry.root)
            uncovered.append((entry.root, translit, entry.total_occurrences))

    uncovered.sort(key=lambda x: -x[2])
    return uncovered


def generate_batch(client, batch, dry_run=False):
    """Send a batch of uncovered roots to Claude and get cognate entries back."""
    lines = []
    for syr, translit, occ in batch:
        lines.append(f"  {syr} ({translit}) — {occ} occurrences")

    prompt = (
        f"Here are {len(batch)} Syriac three-letter patterns from the Peshitta Bible.\n"
        f"Identify which are real triliteral roots and generate cognates for them.\n\n"
        + "\n".join(lines)
        + "\n\nReturn JSON only."
    )

    if dry_run:
        print(f"  [DRY RUN] Would send {len(batch)} patterns to Claude")
        return {"roots": {}, "skipped": []}

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()
        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            return json.loads(json_match.group())
        else:
            print(f"  ERROR: No JSON found in response", file=sys.stderr)
            return {"roots": {}, "skipped": []}

    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return {"roots": {}, "skipped": []}


def main():
    parser = argparse.ArgumentParser(description='Generate cognates for uncovered roots')
    parser.add_argument('--dry-run', action='store_true', help='Preview without API calls')
    parser.add_argument('--batch-size', type=int, default=30, help='Roots per batch (default: 30)')
    parser.add_argument('--max-batches', type=int, default=0, help='Max batches to process (0=all)')
    parser.add_argument('--min-occ', type=int, default=3, help='Minimum occurrences (default: 3)')
    args = parser.parse_args()

    print("Loading corpus and building root index...")
    corpus, extractor = load_corpus_and_extractor()

    print("Loading existing cognates...")
    cognates_data = load_cognates()
    existing_count = len(cognates_data.get('roots', {}))

    print("Finding uncovered roots...")
    uncovered = find_uncovered_roots(extractor, cognates_data, args.min_occ)
    print(f"  Total roots: {extractor.get_root_count()}")
    print(f"  With cognates: {existing_count}")
    print(f"  Uncovered (>={args.min_occ} occ): {len(uncovered)}")

    if not uncovered:
        print("All roots are covered!")
        return

    # Initialize Claude client
    if not args.dry_run:
        client = anthropic.Anthropic()
    else:
        client = None

    # Process in batches
    total_new = 0
    total_skipped = 0
    batch_count = 0

    for i in range(0, len(uncovered), args.batch_size):
        batch = uncovered[i:i + args.batch_size]
        batch_count += 1

        if args.max_batches > 0 and batch_count > args.max_batches:
            print(f"\nReached max batches ({args.max_batches}). Stopping.")
            break

        print(f"\n--- Batch {batch_count} ({len(batch)} patterns) ---")
        result = generate_batch(client, batch, args.dry_run)

        new_roots = result.get('roots', {})
        skipped = result.get('skipped', [])

        if new_roots:
            cognates_data['roots'].update(new_roots)
            total_new += len(new_roots)
            print(f"  New roots: {len(new_roots)}")
            for key in new_roots:
                entry = new_roots[key]
                print(f"    {key}: {entry.get('gloss_en', '?')}")

        if skipped:
            total_skipped += len(skipped)
            print(f"  Skipped: {len(skipped)}")

        # Save after each batch
        if not args.dry_run and new_roots:
            with open(COGNATES_PATH, 'w', encoding='utf-8') as f:
                json.dump(cognates_data, f, ensure_ascii=False, indent=2)

        # Rate limiting
        if not args.dry_run:
            time.sleep(1)

    print(f"\n=== Summary ===")
    print(f"Batches processed: {batch_count}")
    print(f"New root entries: {total_new}")
    print(f"Skipped patterns: {total_skipped}")
    print(f"Total cognate entries now: {len(cognates_data.get('roots', {}))}")


if __name__ == '__main__':
    main()
