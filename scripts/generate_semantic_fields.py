#!/usr/bin/env python3
"""Classify Aramaic roots into semantic domains using Claude Haiku.

Reads data/roots/cognates.json for each root's gloss, sends batches to Claude,
outputs data/roots/semantic_fields.json: {"sh-l-m": ["existence/being", "emotion/mental"], ...}

Usage:
    ANTHROPIC_API_KEY=... python scripts/generate_semantic_fields.py
    python scripts/generate_semantic_fields.py --dry-run
    python scripts/generate_semantic_fields.py --batch-size 30
"""

import argparse
import json
import os
import sys
import time

import anthropic

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ROOTS_DIR = os.path.join(BASE_DIR, 'data', 'roots')
COGNATES_PATH = os.path.join(ROOTS_DIR, 'cognates.json')
OUTPUT_PATH = os.path.join(ROOTS_DIR, 'semantic_fields.json')

DOMAINS = [
    'creation/cosmos',
    'body/anatomy',
    'kinship/family',
    'speech/communication',
    'motion/travel',
    'legal/covenant',
    'worship/cultic',
    'agriculture/food',
    'war/conflict',
    'knowledge/wisdom',
    'time',
    'emotion/mental',
    'commerce/material',
    'nature/elements',
    'existence/being',
]

SYSTEM_PROMPT = f"""\
You are a Semitic linguistics expert. Classify each Aramaic root into 1-2 semantic domains.

Available domains:
{chr(10).join(f'- {d}' for d in DOMAINS)}

For each root, assign exactly 1 or 2 domains that best match its primary meaning.
Respond with a JSON object mapping each root key to an array of 1-2 domain strings.
Only use domains from the list above.
"""


def load_cognates():
    with open(COGNATES_PATH, encoding='utf-8') as f:
        return json.load(f)


def load_existing():
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_output(data):
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)


def classify_batch(client, batch: list[dict]) -> dict:
    """Send a batch of {key, gloss} dicts to Claude Haiku for classification."""
    items_text = '\n'.join(f'{item["key"]}: {item["gloss"]}' for item in batch)
    prompt = f'Classify these Aramaic roots:\n\n{items_text}\n\nRespond with JSON only.'

    response = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{'role': 'user', 'content': prompt}],
    )
    text = response.content[0].text.strip()
    # Strip markdown code fences if present
    if text.startswith('```'):
        text = text.split('```')[1]
        if text.startswith('json'):
            text = text[4:]
    try:
        result = json.loads(text)
        # Validate domains
        cleaned = {}
        for key, fields in result.items():
            if not isinstance(fields, list):
                continue
            valid = [f for f in fields if f in DOMAINS][:2]
            if valid:
                cleaned[key] = valid
        return cleaned
    except json.JSONDecodeError as e:
        print(f'  JSON parse error: {e}', file=sys.stderr)
        return {}


def main():
    parser = argparse.ArgumentParser(description='Generate semantic field classifications')
    parser.add_argument('--dry-run', action='store_true', help='Print prompt, do not call API')
    parser.add_argument('--batch-size', type=int, default=50, help='Roots per API call')
    parser.add_argument('--max-batches', type=int, default=0, help='Max batches (0 = unlimited)')
    args = parser.parse_args()

    cognates_raw = load_cognates()
    # Support both flat and nested {"roots": {...}} structure
    cognates = cognates_raw.get('roots', cognates_raw) if isinstance(cognates_raw, dict) else {}
    existing = load_existing()

    # Build list of roots to classify
    to_classify = []
    for key, entry in cognates.items():
        if not isinstance(entry, dict):
            continue
        if key in existing:
            continue
        gloss = entry.get('gloss_en') or entry.get('sabor_raiz_en') or ''
        if not gloss:
            continue
        to_classify.append({'key': key, 'gloss': gloss})

    print(f'Roots to classify: {len(to_classify)} (already done: {len(existing)})')

    if not to_classify:
        print('Nothing to do.')
        return

    if args.dry_run:
        sample = to_classify[:min(5, len(to_classify))]
        print('\n--- DRY RUN: sample batch ---')
        items_text = '\n'.join(f'{item["key"]}: {item["gloss"]}' for item in sample)
        print(f'Classify these Aramaic roots:\n\n{items_text}\n\nRespond with JSON only.')
        print('\n--- System prompt ---')
        print(SYSTEM_PROMPT[:400] + '...')
        return

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print('Error: ANTHROPIC_API_KEY environment variable not set', file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    output = dict(existing)

    batch_count = 0
    for i in range(0, len(to_classify), args.batch_size):
        batch = to_classify[i:i + args.batch_size]
        batch_count += 1
        print(f'Batch {batch_count}: classifying {len(batch)} roots...')

        result = classify_batch(client, batch)
        output.update(result)
        save_output(output)
        print(f'  Got {len(result)} classifications. Total: {len(output)}')

        if args.max_batches and batch_count >= args.max_batches:
            print(f'Reached max_batches={args.max_batches}, stopping.')
            break

        if i + args.batch_size < len(to_classify):
            time.sleep(1)

    print(f'\nDone. {len(output)} roots classified → {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
