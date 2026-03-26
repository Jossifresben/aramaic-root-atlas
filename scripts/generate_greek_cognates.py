#!/usr/bin/env python3
"""Generate Greek NT equivalents for Aramaic roots attested in Peshitta NT.

For each root, asks Claude to identify the most common Greek NT word(s) that
the Peshitta translates with forms of this root.

Usage:
    ANTHROPIC_API_KEY=sk-... python scripts/generate_greek_cognates.py
    python scripts/generate_greek_cognates.py --batch-size 20 --limit 100
"""

import argparse
import json
import os
import sys
import time

COGNATES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'roots', 'cognates.json')


def get_nt_roots():
    """Get roots that appear in Peshitta NT corpus."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from aramaic_core.corpus import AramaicCorpus
    from aramaic_core.extractor import RootExtractor
    from aramaic_core.characters import transliterate_syriac

    corpus = AramaicCorpus()
    corpus.add_corpus('peshitta_nt', 'Peshitta NT',
                      os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'corpora', 'peshitta_nt.csv'))
    corpus.load()

    extractor = RootExtractor(corpus, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'roots'))
    extractor.build_index()

    roots = []
    for entry in extractor.get_all_roots():
        # Count NT occurrences from matches
        nt_count = 0
        for match in entry.matches:
            for ref in match.references:
                if corpus.get_verse_corpus(ref) == 'peshitta_nt':
                    nt_count += 1
        if nt_count > 0:
            latin = transliterate_syriac(entry.root).upper()
            gloss = extractor.get_root_gloss(entry.root)
            roots.append({
                'syriac': entry.root,
                'latin': latin,
                'nt_count': nt_count,
                'gloss': gloss or '',
            })

    roots.sort(key=lambda x: x['nt_count'], reverse=True)
    return roots


def generate_batch(roots_batch, api_key):
    """Send a batch of roots to Claude and get Greek equivalents."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    root_list = []
    for r in roots_batch:
        root_list.append(f"- {r['latin']} ({r['syriac']}): {r['gloss'] or 'unknown'}, NT occurrences: {r['nt_count']}")

    prompt = f"""For each Syriac/Aramaic root below, identify the most common Greek New Testament word(s)
that the Peshitta typically translates using forms derived from this root.

Return ONLY valid JSON — an array of objects, one per root, with these fields:
- "root_latin": the root key exactly as given
- "greek": array of objects, each with:
  - "word": the Greek word in Greek script
  - "transliteration": romanized form
  - "meaning_en": English meaning
  - "meaning_es": Spanish meaning

If you're unsure about a root's Greek equivalent, include it with your best guess.
If a root has no clear Greek equivalent (e.g., it's a function word), use an empty array for "greek".

Roots:
{chr(10).join(root_list)}

Return ONLY the JSON array, no markdown, no explanation."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    # Strip markdown code fences if present
    if text.startswith('```'):
        text = text.split('\n', 1)[1]
        if text.endswith('```'):
            text = text.rsplit('```', 1)[0]

    return json.loads(text)


def main():
    parser = argparse.ArgumentParser(description='Generate Greek cognates for NT roots')
    parser.add_argument('--batch-size', type=int, default=25, help='Roots per API call')
    parser.add_argument('--limit', type=int, default=0, help='Max roots to process (0=all)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    args = parser.parse_args()

    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key and not args.dry_run:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Load existing cognates
    with open(COGNATES_PATH, 'r', encoding='utf-8') as f:
        cognates = json.load(f)

    # Get NT roots
    print("Loading NT roots...")
    nt_roots = get_nt_roots()
    print(f"Found {len(nt_roots)} roots attested in Peshitta NT")

    # Filter out roots that already have Greek data
    to_process = []
    for r in nt_roots:
        latin_key = r['latin'].lower().replace('-', '-')
        # Check various key formats
        cog = cognates.get(latin_key) or cognates.get(r['latin'].lower())
        if cog and isinstance(cog, dict) and cog.get('cognates', {}).get('greek'):
            continue
        to_process.append(r)

    if args.limit > 0:
        to_process = to_process[:args.limit]

    print(f"Need Greek cognates for {len(to_process)} roots")

    if args.dry_run:
        for r in to_process[:20]:
            print(f"  {r['latin']} ({r['syriac']}): {r['gloss']} [{r['nt_count']}x]")
        if len(to_process) > 20:
            print(f"  ... and {len(to_process) - 20} more")
        return

    # Process in batches
    total_added = 0
    batches = [to_process[i:i + args.batch_size] for i in range(0, len(to_process), args.batch_size)]

    for batch_idx, batch in enumerate(batches):
        print(f"\nBatch {batch_idx + 1}/{len(batches)} ({len(batch)} roots)...")
        try:
            results = generate_batch(batch, api_key)
            for item in results:
                root_key = item.get('root_latin', '').lower()
                greek_data = item.get('greek', [])
                if not greek_data:
                    continue

                # Find the cognate entry
                if root_key not in cognates:
                    # Try dash-separated format
                    for r in batch:
                        if r['latin'].lower() == root_key:
                            root_key = r['latin'].lower()
                            break

                if root_key in cognates and isinstance(cognates[root_key], dict):
                    if 'cognates' not in cognates[root_key]:
                        cognates[root_key]['cognates'] = {}
                    cognates[root_key]['cognates']['greek'] = greek_data
                else:
                    # Create minimal entry
                    cognates[root_key] = {
                        'cognates': {
                            'greek': greek_data
                        }
                    }
                total_added += 1
                print(f"  + {root_key}: {greek_data[0].get('word', '?')} ({greek_data[0].get('transliteration', '?')})")

        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)

        # Save after each batch
        with open(COGNATES_PATH, 'w', encoding='utf-8') as f:
            json.dump(cognates, f, ensure_ascii=False, indent=2)

        if batch_idx < len(batches) - 1:
            time.sleep(2)  # Rate limit

    print(f"\nDone. Added Greek cognates for {total_added} roots.")
    print(f"Total cognate entries: {len(cognates)}")


if __name__ == '__main__':
    main()
