#!/usr/bin/env python3
"""Measure root-extraction confidence distribution on a corpus CSV.

Usage:
    python3 scripts/measure_confidence.py data/corpora/ephrem_nisibis.csv
    python3 scripts/measure_confidence.py data/corpora/peshitta_nt.csv  # baseline comparison
"""
import csv
import sys
import os

# Ensure aramaic_core is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from aramaic_core.corpus import AramaicCorpus
from aramaic_core.extractor import RootExtractor

ROOTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'roots')


def main():
    if len(sys.argv) < 2:
        print("Usage: measure_confidence.py <corpus.csv>", file=sys.stderr)
        sys.exit(1)

    csv_path = sys.argv[1]
    corpus_id = os.path.splitext(os.path.basename(csv_path))[0]

    corpus = AramaicCorpus()
    corpus.add_corpus(corpus_id, corpus_id, csv_path)
    corpus.load()

    extractor = RootExtractor(corpus, ROOTS_DIR)
    extractor.build_index()

    # Count confidence tiers across all tokens
    high = med = low = none_ = 0
    low_forms: dict[str, int] = {}   # form -> count (for most-common failures)
    none_forms: dict[str, int] = {}

    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for word in (row.get('syriac') or '').split():
                result = extractor.lookup_word_root_with_confidence(word)
                if result is None:
                    none_ += 1
                    none_forms[word] = none_forms.get(word, 0) + 1
                else:
                    _, conf = result
                    if conf >= 0.8:
                        high += 1
                    elif conf >= 0.5:
                        med += 1
                    else:
                        low += 1
                        low_forms[word] = low_forms.get(word, 0) + 1

    total = high + med + low + none_
    print(f"\nCorpus: {corpus_id}")
    print(f"Total tokens: {total}")
    print(f"  High (>=0.8):  {high:>6}  ({100*high/total:.1f}%)")
    print(f"  Medium (>=0.5):{med:>6}  ({100*med/total:.1f}%)")
    print(f"  Low (<0.5):   {low:>6}  ({100*low/total:.1f}%)")
    print(f"  No root:      {none_:>6}  ({100*none_/total:.1f}%)")
    print(f"\nTop 20 low-confidence forms:")
    for form, cnt in sorted(low_forms.items(), key=lambda x: -x[1])[:20]:
        print(f"  {form!r:30s}  {cnt}")
    print(f"\nTop 20 unresolved forms:")
    for form, cnt in sorted(none_forms.items(), key=lambda x: -x[1])[:20]:
        print(f"  {form!r:30s}  {cnt}")


if __name__ == '__main__':
    main()
