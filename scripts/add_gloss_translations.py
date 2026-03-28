#!/usr/bin/env python3
"""Add Hebrew (gloss_he) and Arabic (gloss_ar) gloss fields to existing cognate entries.

Reads cognates.json, finds entries missing gloss_he or gloss_ar,
batch-translates from gloss_en via Claude, and writes back in-place.

Requires ANTHROPIC_API_KEY environment variable.

Usage:
    python scripts/add_gloss_translations.py                    # Process all missing
    python scripts/add_gloss_translations.py --dry-run          # Preview
    python scripts/add_gloss_translations.py --batch-size 50    # Custom batch size
    python scripts/add_gloss_translations.py --max-batches 10   # Limit batches
"""

import argparse
import json
import os
import sys
import time

import anthropic

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
COGNATES_PATH = os.path.join(BASE_DIR, 'data', 'roots', 'cognates.json')

SYSTEM_PROMPT = """\
You are a translation expert for Semitic languages. You will receive a batch of short Aramaic root glosses \
in English (1-3 words each, e.g. "peace, complete", "write", "go out") and must translate them into:
- Hebrew (modern Israeli Hebrew, 1-3 words, no nikkud needed)
- Arabic (Modern Standard Arabic, 1-3 words, no tashkil needed)

Keep translations concise and idiomatic — match the register and brevity of the English.

RESPOND WITH ONLY valid JSON in this format:
{
  "translations": {
    "root-key": {"gloss_he": "שלום, שלם", "gloss_ar": "سلام، أكمل"},
    ...
  }
}
"""


def load_cognates():
    with open(COGNATES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_cognates(data):
    with open(COGNATES_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Saved {COGNATES_PATH}")


def find_missing(cognates_data):
    """Find entries in roots sub-dict missing gloss_he or gloss_ar."""
    roots = cognates_data.get('roots', {})
    missing = []
    for key, entry in roots.items():
        if isinstance(entry, dict) and entry.get('gloss_en'):
            if not entry.get('gloss_he') or not entry.get('gloss_ar'):
                missing.append((key, entry['gloss_en']))
    return missing


def translate_batch(client, batch, dry_run=False):
    """Translate a batch of (key, gloss_en) pairs."""
    lines = [f'  "{key}": "{gloss}"' for key, gloss in batch]
    prompt = (
        f"Translate these {len(batch)} Aramaic root glosses from English to Hebrew and Arabic:\n\n"
        + "\n".join(lines)
        + "\n\nReturn JSON only."
    )

    if dry_run:
        print(f"  [DRY RUN] Would translate {len(batch)} glosses")
        return {}

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()

        # Strip markdown fences if present
        if text.startswith('```'):
            text = '\n'.join(text.split('\n')[1:])
            if text.endswith('```'):
                text = text[:-3].strip()

        result = json.loads(text)
        return result.get('translations', {})

    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        print(f"  Response snippet: {text[:200] if 'text' in dir() else '?'}")
        return {}
    except Exception as e:
        print(f"  API error: {e}")
        return {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--batch-size', type=int, default=50)
    parser.add_argument('--max-batches', type=int, default=0)
    args = parser.parse_args()

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key and not args.dry_run:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key) if api_key else None

    print("Loading cognates...")
    data = load_cognates()
    missing = find_missing(data)
    print(f"Entries missing he/ar gloss: {len(missing)}")

    if not missing:
        print("All entries already have he/ar glosses.")
        return

    batches = [missing[i:i+args.batch_size] for i in range(0, len(missing), args.batch_size)]
    if args.max_batches:
        batches = batches[:args.max_batches]

    print(f"Processing {len(batches)} batches of up to {args.batch_size}...")
    total_updated = 0

    for i, batch in enumerate(batches, 1):
        print(f"\nBatch {i}/{len(batches)} ({len(batch)} glosses)...")
        translations = translate_batch(client, batch, dry_run=args.dry_run)

        if translations:
            roots = data.get('roots', {})
            updated = 0
            for key, t in translations.items():
                if key in roots and isinstance(roots[key], dict):
                    if t.get('gloss_he'):
                        roots[key]['gloss_he'] = t['gloss_he']
                    if t.get('gloss_ar'):
                        roots[key]['gloss_ar'] = t['gloss_ar']
                    updated += 1
            total_updated += updated
            print(f"  Updated: {updated}")
            if not args.dry_run:
                save_cognates(data)

        if i < len(batches):
            time.sleep(0.5)

    print(f"\nDone. Total entries updated: {total_updated}")


if __name__ == '__main__':
    main()
