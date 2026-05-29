#!/usr/bin/env python3
"""Generate Hebrew & Arabic cognates for roots newly attested by Targum Jonathan.

Scope: roots whose corpus attestation is EXCLUSIVELY `targum_jonathan`
(i.e. the vocabulary Targum Jonathan adds to the Atlas). Roots already
attested in another corpus are out of scope — they were coverable before
this corpus landed.

Uses Opus (claude-opus-4-8) for comparative-Semitic lexicography, with
prompt caching on the system prompt. Writes incrementally to
data/roots/cognates.json after each batch (crash-safe).

Requires ANTHROPIC_API_KEY in the environment. Run with:
    set -a; source .env; set +a
    python3 scripts/generate_cognates_targum_jonathan.py --max-batches 1   # smoke test
    python3 scripts/generate_cognates_targum_jonathan.py --min-occ 2       # full run
"""

import argparse
import json
import os
import re
import sys
import time

import anthropic

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CORPORA_DIR = os.path.join(DATA_DIR, 'corpora')
ROOTS_DIR = os.path.join(DATA_DIR, 'roots')
COGNATES_PATH = os.path.join(ROOTS_DIR, 'cognates.json')

MODEL = "claude-opus-4-8"

CORPORA = [
    ('peshitta_nt', 'Peshitta NT', 'peshitta_nt.csv'),
    ('peshitta_ot', 'Peshitta OT', 'peshitta_ot.csv'),
    ('biblical_aramaic', 'Biblical Aramaic', 'biblical_aramaic.csv'),
    ('targum_onkelos', 'Targum Onkelos', 'targum_onkelos.csv'),
    ('targum_jonathan', 'Targum Jonathan', 'targum_jonathan.csv'),
    ('ephrem_nisibis', 'Ephrem — Nisibis', 'ephrem_nisibis.csv'),
]

SYSTEM_PROMPT = """\
You are a Semitic linguistics expert specializing in Aramaic (Jewish \
Babylonian/Palestinian and Syriac), Biblical Hebrew, and Classical Arabic, \
with command of the standard lexica (Sokoloff DJBA/DJPA, Jastrow, HALOT, \
Brockelmann, Lane, Wehr).

You will receive a batch of three-consonant patterns extracted from \
Targum Jonathan to the Prophets (Jewish Aramaic, written in Hebrew square \
script; presented here in normalized Syriac-script form with academic \
transliteration). MANY of these are NOT genuine triliteral roots — common \
false positives in Targumic Aramaic are:
- Proclitic + word fragments: d- (relative/genitive), w- (and), b- (in), \
  l- (to), k- (like), often stacked (e.g. d'th = d+ʾṯ "that came")
- Pronominal/suffix fragments and the object marker yt (ית)
- Particles, conjunctions, demonstratives, interrogatives
- Proper nouns (people, places) and divine-name abbreviations

Your job, per pattern:
1. FILTER: decide whether it is a genuine triliteral root.
2. GENERATE: for each genuine root, supply Hebrew and Arabic cognates that \
   are real, attested, and etymologically sound. Do NOT invent cognates. \
   If a language has no secure cognate, return an empty array for it rather \
   than guessing.

For each real root provide:
- root_syriac: the root in Syriac Unicode (as given)
- gloss_en: English gloss (1-3 words)
- gloss_es: Spanish gloss (1-3 words)
- hebrew: 0-4 cognate words, each {word (with niqqud), transliteration, meaning_en, meaning_es}
- arabic: 0-4 cognate words, each {word (with tashkil), transliteration, meaning_en, meaning_es}

RESPOND WITH ONLY valid JSON, no prose, no code fences. Format:
{
  "roots": {
    "x-y-z": {
      "root_syriac": "ܝܝܝ",
      "gloss_en": "...",
      "gloss_es": "...",
      "hebrew": [{"word": "...", "transliteration": "...", "meaning_en": "...", "meaning_es": "..."}],
      "arabic": [{"word": "...", "transliteration": "...", "meaning_en": "...", "meaning_es": "..."}]
    }
  },
  "skipped": ["pattern (reason)", ...]
}
"""


def build_index():
    sys.path.insert(0, BASE_DIR)
    from aramaic_core import AramaicCorpus
    from aramaic_core.extractor import RootExtractor
    corpus = AramaicCorpus()
    corpus.set_translations_dir(os.path.join(DATA_DIR, 'translations'))
    for cid, label, fname in CORPORA:
        corpus.add_corpus(cid, label, os.path.join(CORPORA_DIR, fname))
    corpus.load()
    extractor = RootExtractor(corpus, ROOTS_DIR)
    extractor.build_index()
    return extractor


def load_cognates():
    if os.path.exists(COGNATES_PATH):
        with open(COGNATES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"roots": {}}


def find_jonathan_exclusive_uncovered(extractor, cognates_data, min_occ):
    sys.path.insert(0, BASE_DIR)
    from aramaic_core.characters import transliterate_syriac
    existing = set(e.get('root_syriac', '')
                   for e in cognates_data.get('roots', {}).values()
                   if e.get('root_syriac'))
    out = []
    for entry in extractor.get_all_roots():
        if set(entry.corpus_counts.keys()) != {'targum_jonathan'}:
            continue
        if entry.root in existing:
            continue
        if entry.total_occurrences < min_occ:
            continue
        out.append((entry.root, transliterate_syriac(entry.root), entry.total_occurrences))
    out.sort(key=lambda x: -x[2])
    return out


def parse_json(text):
    text = text.strip()
    # strip code fences if present
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    m = re.search(r'\{[\s\S]*\}', text)
    if not m:
        return None
    return json.loads(m.group())


def generate_batch(client, batch):
    lines = [f"  {syr} ({translit}) — {occ} occurrences" for syr, translit, occ in batch]
    user = (
        f"Here are {len(batch)} patterns from Targum Jonathan. Identify the "
        f"genuine triliteral roots and generate cognates. Return JSON only.\n\n"
        + "\n".join(lines)
    )
    resp = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": user}],
    )
    u = resp.usage
    text = resp.content[0].text
    return parse_json(text), u


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch-size', type=int, default=20)
    ap.add_argument('--min-occ', type=int, default=2)
    ap.add_argument('--max-batches', type=int, default=0, help='0 = all')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    print("Building root index over all 6 corpora...")
    extractor = build_index()
    cognates = load_cognates()
    before = len(cognates.get('roots', {}))

    targets = find_jonathan_exclusive_uncovered(extractor, cognates, args.min_occ)
    print(f"Existing cognate entries: {before}")
    print(f"Jonathan-exclusive uncovered roots (>= {args.min_occ} occ): {len(targets)}")
    n_batches = (len(targets) + args.batch_size - 1) // args.batch_size
    print(f"Batches of {args.batch_size}: {n_batches}")
    if not targets:
        print("Nothing to do.")
        return
    if args.dry_run:
        for syr, tr, occ in targets[:40]:
            print(f"  {syr} {tr} ({occ})")
        return

    client = anthropic.Anthropic()
    total_new = total_skipped = 0
    cache_w = cache_r = tok_in = tok_out = 0

    for bi in range(n_batches):
        if args.max_batches and bi >= args.max_batches:
            print(f"\nStopping at max-batches={args.max_batches}.")
            break
        batch = targets[bi * args.batch_size:(bi + 1) * args.batch_size]
        print(f"\n--- Batch {bi + 1}/{n_batches} ({len(batch)} patterns) ---")
        try:
            result, usage = generate_batch(client, batch)
        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            break
        if usage:
            tok_in += usage.input_tokens
            tok_out += usage.output_tokens
            cache_w += getattr(usage, 'cache_creation_input_tokens', 0) or 0
            cache_r += getattr(usage, 'cache_read_input_tokens', 0) or 0
        if not result:
            print("  WARN: no JSON parsed; skipping batch")
            continue
        new_roots = result.get('roots', {})
        skipped = result.get('skipped', [])
        if new_roots:
            cognates['roots'].update(new_roots)
            total_new += len(new_roots)
            for k, v in new_roots.items():
                print(f"    + {k}: {v.get('gloss_en', '?')} "
                      f"(he {len(v.get('hebrew', []))}, ar {len(v.get('arabic', []))})")
            with open(COGNATES_PATH, 'w', encoding='utf-8') as f:
                json.dump(cognates, f, ensure_ascii=False, indent=2)
        total_skipped += len(skipped)
        print(f"  new={len(new_roots)} skipped={len(skipped)}")
        time.sleep(1)

    after = len(cognates.get('roots', {}))
    # rough Opus 4.8 cost: $15/M in, $1.50/M cached-read, $75/M out
    cost = (tok_in * 15 + cache_r * 1.5 + tok_out * 75) / 1e6
    print("\n=== Summary ===")
    print(f"New cognate roots: {total_new} | skipped non-roots: {total_skipped}")
    print(f"Cognate entries: {before} -> {after}")
    print(f"Tokens: in={tok_in} cache_write={cache_w} cache_read={cache_r} out={tok_out}")
    print(f"Approx cost: ${cost:.2f}")


if __name__ == '__main__':
    main()
