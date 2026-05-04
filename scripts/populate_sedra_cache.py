#!/usr/bin/env python3
"""Pre-populate the SEDRA cache for all unique tokens in specified corpus CSVs.

Usage:
    python3 scripts/populate_sedra_cache.py data/corpora/ephrem_nisibis.csv
    python3 scripts/populate_sedra_cache.py data/corpora/ephrem_nisibis.csv data/corpora/peshitta_nt.csv
"""
import csv
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from aramaic_core.sedra_lookup import SedraLookup


def collect_tokens(csv_paths: list) -> list:
    seen = set()
    for path in csv_paths:
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                for word in (row.get('syriac') or '').split():
                    seen.add(word.strip())
    return sorted(seen)


def main():
    if len(sys.argv) < 2:
        print("Usage: populate_sedra_cache.py <corpus.csv> [corpus2.csv ...]")
        sys.exit(1)

    paths = sys.argv[1:]
    tokens = collect_tokens(paths)
    print(f"Unique tokens to look up: {len(tokens)}")

    sedra = SedraLookup()
    sedra.load_cache()
    already = sum(1 for t in tokens if t in sedra._cache)
    print(f"Already cached: {already}. New lookups needed: {len(tokens) - already}")
    print("Querying SEDRA API (0.15s delay between calls)...")
    sedra.populate(tokens)
    print(f"Cache saved to {sedra.cache_path}")


if __name__ == '__main__':
    main()
