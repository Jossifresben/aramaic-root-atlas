# Ephrem Nisibis Corpus + SEDRA Fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Load Ephrem's Hymns on Nisibis from the Digital Syriac Corpus (CC BY 4.0) as a fifth corpus, measure root-extraction confidence on literary Syriac, and add SEDRA API as a fallback oracle for low-confidence tokens.

**Architecture:** Four new files are added — a fetch/parse script (TEI XML → CSV), a confidence measurement script, a SEDRA lookup module with pre-populated cache, and a cache population script. `app.py` is modified in three targeted places: corpus registration, CORPUS_CHRONOLOGY, and word-level resolution in `api_verse` and `api_interlinear`. The extractor itself is not modified.

**Tech Stack:** Python 3.11, Flask, `requests`, `lxml` (TEI XML parsing), existing `aramaic_core` package.

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `scripts/fetch_ephrem_nisibis.py` | Create | Clone DSC repo subset, parse TEI XML → `data/corpora/ephrem_nisibis.csv` |
| `scripts/measure_confidence.py` | Create | Run extractor on any corpus CSV, print confidence distribution |
| `aramaic_core/sedra_lookup.py` | Create | SEDRA API client + file-based cache reader |
| `scripts/populate_sedra_cache.py` | Create | Pre-query SEDRA for every unique token in ephrem_nisibis.csv → `data/roots/sedra_cache.json` |
| `app.py` | Modify (3 sites) | Register corpus; add to CORPUS_CHRONOLOGY; apply SEDRA fallback in verse/interlinear word loop |
| `data/corpora/ephrem_nisibis.csv` | Generated | Corpus data (committed) |
| `data/roots/sedra_cache.json` | Generated | SEDRA response cache (committed) |

---

## Task 1: Fetch and parse Hymns on Nisibis from DSC

**Files:**
- Create: `scripts/fetch_ephrem_nisibis.py`
- Output: `data/corpora/ephrem_nisibis.csv`

The Digital Syriac Corpus stores each text as a TEI XML file. Carmen Nisibena files are in the `srophe/syriac-corpus` GitHub repo. We download them via the GitHub API (no git required) and parse the Syriac text out of `<l>` elements.

The reference scheme maps onto the existing corpus CSV format:
- `book` = `"Nisibis"` (single work, one "book")
- `book_order` = `1`
- `chapter` = hymn number (extracted from TEI `<div n="...">` or filename)
- `verse` = stanza number within the hymn (each `<lg>` is a stanza; all its `<l>` lines are joined with a space)
- `reference` = `"Nisibis {chapter}:{verse}"` e.g. `"Nisibis 1:3"`
- `syriac` = the Unicode Syriac text of the stanza (all lines joined)

TEI structure in DSC files:
```xml
<body>
  <div type="hymn" n="1">
    <lg type="stanza" n="1">
      <l n="1">ܫܠܡܐ ܢܬܠ ܡܪܝ ...</l>
      <l n="2">ܘܢܚܕܐ ܠܥܕܬܗ ...</l>
    </lg>
    <lg type="stanza" n="2">
      ...
    </lg>
  </div>
</body>
```

- [ ] **Step 1: Install lxml if not present**

```bash
pip install lxml
```

Expected: lxml installed (or already present — no error).

- [ ] **Step 2: Write the fetch script**

```python
#!/usr/bin/env python3
"""Fetch Hymns on Nisibis (Carmen Nisibena) from Digital Syriac Corpus GitHub
and convert to Aramaic Root Atlas corpus CSV format.

Source: https://github.com/srophe/syriac-corpus (CC BY 4.0)
Output: data/corpora/ephrem_nisibis.csv
"""
import csv
import os
import sys
import time
import requests
from lxml import etree

GITHUB_API = "https://api.github.com/repos/srophe/syriac-corpus/contents"
RAW_BASE   = "https://raw.githubusercontent.com/srophe/syriac-corpus/main"
OUT_DIR    = os.path.join(os.path.dirname(__file__), '..', 'data', 'corpora')
OUT_CSV    = os.path.join(OUT_DIR, 'ephrem_nisibis.csv')

# Namespaces used in DSC TEI files
NS = {
    'tei': 'http://www.tei-c.org/ns/1.0',
    'xml': 'http://www.w3.org/XML/1998/namespace',
}

def list_nisibis_files() -> list[str]:
    """Return raw URLs for Carmen Nisibena TEI files in the DSC repo."""
    resp = requests.get(f"{GITHUB_API}", timeout=15)
    resp.raise_for_status()
    items = resp.json()
    # Files are at top level; Nisibis files are named like 0259EphremSyrus-...
    # Look for files whose name contains 'Nisib' or are in the 259-331 range
    nisibis = []
    for item in items:
        if item['type'] == 'file' and item['name'].endswith('.xml'):
            # DSC Ephrem Nisibis files start with numbers 259-331
            try:
                num = int(item['name'][:4])
                if 259 <= num <= 331:
                    nisibis.append(item['download_url'])
            except ValueError:
                pass
    return sorted(nisibis)

def parse_tei_file(xml_bytes: bytes, hymn_base: int) -> list[dict]:
    """Parse one TEI XML file and return a list of stanza dicts."""
    rows = []
    try:
        root = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as e:
        print(f"  XML parse error: {e}", file=sys.stderr)
        return rows

    # Find all hymn divs
    body = root.find('.//tei:body', NS)
    if body is None:
        return rows

    hymn_divs = body.findall('.//tei:div[@type="hymn"]', NS)
    if not hymn_divs:
        # Some files have a single div without type="hymn"
        hymn_divs = body.findall('tei:div', NS)

    for hdiv in hymn_divs:
        hymn_n_attr = hdiv.get('n', str(hymn_base))
        try:
            hymn_n = int(hymn_n_attr)
        except ValueError:
            hymn_n = hymn_base

        stanzas = hdiv.findall('.//tei:lg', NS)
        for stanza in stanzas:
            stanza_n_attr = stanza.get('n', '1')
            try:
                stanza_n = int(stanza_n_attr)
            except ValueError:
                stanza_n = 1

            # Collect Syriac lines
            lines = []
            for line in stanza.findall('tei:l', NS):
                # Get text content, strip mixed-content noise
                text = ''.join(line.itertext()).strip()
                if text:
                    lines.append(text)

            syriac = ' '.join(lines).strip()
            if not syriac:
                continue

            # Only include lines that contain Syriac characters (U+0700-074F)
            if not any('܀' <= ch <= 'ݏ' for ch in syriac):
                continue

            ref = f"Nisibis {hymn_n}:{stanza_n}"
            rows.append({
                'book_order': 1,
                'book': 'Nisibis',
                'chapter': hymn_n,
                'verse': stanza_n,
                'reference': ref,
                'syriac': syriac,
            })
    return rows

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Fetching file list from DSC GitHub...")
    urls = list_nisibis_files()
    if not urls:
        print("ERROR: No Nisibis files found. Check GitHub API or file naming.", file=sys.stderr)
        sys.exit(1)
    print(f"Found {len(urls)} files.")

    all_rows = []
    for i, url in enumerate(urls, 1):
        print(f"  [{i}/{len(urls)}] {url.split('/')[-1]}")
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        rows = parse_tei_file(resp.content, hymn_base=i)
        all_rows.extend(rows)
        time.sleep(0.2)  # be polite to GitHub

    # Sort by chapter, verse for consistent ordering
    all_rows.sort(key=lambda r: (r['chapter'], r['verse']))

    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['book_order','book','chapter','verse','reference','syriac'])
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nWrote {len(all_rows)} stanzas to {OUT_CSV}")

if __name__ == '__main__':
    main()
```

- [ ] **Step 3: Run the fetch script**

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
python3 scripts/fetch_ephrem_nisibis.py
```

Expected output (approximate):
```
Fetching file list from DSC GitHub...
Found N files.
  [1/N] 0259EphremSyrus-...xml
  ...
Wrote XXXX stanzas to data/corpora/ephrem_nisibis.csv
```

- [ ] **Step 4: Verify the CSV**

```bash
head -5 "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas/data/corpora/ephrem_nisibis.csv"
wc -l "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas/data/corpora/ephrem_nisibis.csv"
```

Expected: header + rows with Syriac text in the `syriac` column; at least 500 stanzas.

If Syriac column is empty or mostly empty, the TEI namespace or element names differ — inspect one raw XML file:
```bash
python3 -c "
import requests
r = requests.get('https://raw.githubusercontent.com/srophe/syriac-corpus/main/data/tei/0259EphremSyrus-hymni.xml', timeout=15)
print(r.text[:3000])
"
```
Adjust element names in `parse_tei_file()` accordingly.

- [ ] **Step 5: Commit**

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
git add scripts/fetch_ephrem_nisibis.py data/corpora/ephrem_nisibis.csv
git commit -m "feat(corpus): add Ephrem Hymns on Nisibis from Digital Syriac Corpus (CC BY 4.0)"
```

---

## Task 2: Measure confidence baseline on Ephrem corpus

**Files:**
- Create: `scripts/measure_confidence.py`

This script loads the corpus CSV, runs the root extractor on every token, and prints a confidence distribution report. Run it before and after SEDRA integration to quantify improvement.

- [ ] **Step 1: Write the measurement script**

```python
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
    print(f"  High (≥0.8):  {high:>6}  ({100*high/total:.1f}%)")
    print(f"  Medium (≥0.5):{med:>6}  ({100*med/total:.1f}%)")
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
```

- [ ] **Step 2: Run on Ephrem corpus**

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
python3 scripts/measure_confidence.py data/corpora/ephrem_nisibis.csv
```

Expected: a report showing confidence distribution. Save this output — it's the baseline.

- [ ] **Step 3: Run on Peshitta NT for comparison**

```bash
python3 scripts/measure_confidence.py data/corpora/peshitta_nt.csv
```

Expected: Peshitta NT should show higher high-confidence % than Ephrem. This confirms the extractor struggles more with literary Syriac.

- [ ] **Step 4: Commit**

```bash
git add scripts/measure_confidence.py
git commit -m "feat(scripts): add confidence measurement script for corpus benchmarking"
```

---

## Task 3: SEDRA API lookup module with file-based cache

**Files:**
- Create: `aramaic_core/sedra_lookup.py`

SEDRA API endpoint: `GET https://sedra.bethmardutho.org/api/word/{syriac_word}`  
Returns a JSON array. Each element has: `stem` (Syriac root), `category` (verb/noun/etc.), `glosses.eng` (list of English glosses), `kaylo` (verb stem: peal/pael/etc.).

We pre-populate a cache (`data/roots/sedra_cache.json`) so runtime lookups are instant file reads with no HTTP calls in production.

- [ ] **Step 1: Write the SEDRA lookup module**

```python
"""SEDRA API client for Aramaic Root Atlas.

Provides root and gloss lookup for Syriac words via the SEDRA IV API
(sedra.bethmardutho.org, Apache 2.0). Uses a pre-populated JSON cache
to avoid runtime HTTP calls.

Cache format (data/roots/sedra_cache.json):
    {
        "ܫܠܡ": {"stem": "ܫܠܡ", "gloss": "complete, finish", "category": "verb", "kaylo": "paʿʿel"},
        "ܡܠܟܐ": {"stem": "ܡܠܟ", "gloss": "king, counsel", "category": "noun", "kaylo": null},
        "ܐܝܕܐ": null   <- null means SEDRA has no entry for this word
    }
"""
import json
import os
import time
from typing import Optional

import requests

SEDRA_API = "https://sedra.bethmardutho.org/api/word/{word}"
CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'roots', 'sedra_cache.json')


def _parse_response(data: list[dict]) -> Optional[dict]:
    """Extract the most useful entry from a SEDRA response array."""
    if not data:
        return None
    # Prefer entries that are lexical forms (isLexicalForm=true), else take first
    lexical = [e for e in data if e.get('isLexicalForm') == 'true']
    entry = lexical[0] if lexical else data[0]
    stem = entry.get('stem', '')
    if not stem:
        return None
    glosses = entry.get('glosses', {}).get('eng', [])
    gloss = '; '.join(glosses[:3]) if glosses else ''
    return {
        'stem': stem,
        'gloss': gloss,
        'category': entry.get('category', ''),
        'kaylo': entry.get('kaylo'),
    }


class SedraLookup:
    """SEDRA IV lookup with file-based cache.

    Usage:
        sedra = SedraLookup()
        sedra.load_cache()                    # call once at startup
        result = sedra.lookup('ܫܠܡ')         # returns dict or None
    """

    def __init__(self, cache_path: str = CACHE_FILE):
        self._cache_path = cache_path
        self._cache: dict[str, Optional[dict]] = {}
        self._loaded = False

    def load_cache(self) -> None:
        """Load the pre-populated cache from disk. Silent if file missing."""
        if os.path.exists(self._cache_path):
            with open(self._cache_path, encoding='utf-8') as f:
                self._cache = json.load(f)
        self._loaded = True

    def lookup(self, syriac_word: str) -> Optional[dict]:
        """Return SEDRA data for a word, or None if not found.

        Returns dict with keys: stem, gloss, category, kaylo.
        """
        if not self._loaded:
            self.load_cache()
        word = syriac_word.strip()
        if word in self._cache:
            return self._cache[word]   # may be None (cached miss)
        return None  # not in cache — don't do live API calls at runtime

    # ------------------------------------------------------------------ #
    # Methods used only by populate_sedra_cache.py (not called at runtime)
    # ------------------------------------------------------------------ #

    def fetch_live(self, syriac_word: str) -> Optional[dict]:
        """Query SEDRA API directly. Use only from populate script."""
        url = SEDRA_API.format(word=syriac_word)
        try:
            resp = requests.get(url, timeout=8)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return _parse_response(resp.json())
        except Exception:
            return None

    def save_cache(self) -> None:
        """Persist current cache to disk."""
        os.makedirs(os.path.dirname(self._cache_path), exist_ok=True)
        with open(self._cache_path, 'w', encoding='utf-8') as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=2)

    def populate(self, words: list[str], delay: float = 0.15) -> None:
        """Query SEDRA for each word not yet in cache. Saves after each batch of 100."""
        new = 0
        for i, word in enumerate(words):
            if word in self._cache:
                continue
            result = self.fetch_live(word)
            self._cache[word] = result
            new += 1
            if new % 100 == 0:
                self.save_cache()
                print(f"  Cached {new} new entries ({i+1}/{len(words)} words processed)")
            time.sleep(delay)
        if new % 100 != 0:
            self.save_cache()
        print(f"Done. {new} new entries added to cache.")
```

Save as `aramaic_core/sedra_lookup.py`.

- [ ] **Step 2: Write a quick smoke test**

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
python3 -c "
import sys; sys.path.insert(0, '.')
from aramaic_core.sedra_lookup import SedraLookup
s = SedraLookup()
result = s.fetch_live('ܫܠܡ')
print(result)
assert result is not None
assert 'stem' in result
assert result['stem'] == 'ܫܠܡ'
print('SEDRA lookup OK')
"
```

Expected:
```
{'stem': 'ܫܠܡ', 'gloss': '...', 'category': 'verb', 'kaylo': '...'}
SEDRA lookup OK
```

- [ ] **Step 3: Commit**

```bash
git add aramaic_core/sedra_lookup.py
git commit -m "feat(sedra): add SEDRA IV lookup module with file-based cache"
```

---

## Task 4: Populate the SEDRA cache for Ephrem tokens

**Files:**
- Create: `scripts/populate_sedra_cache.py`
- Output: `data/roots/sedra_cache.json`

- [ ] **Step 1: Write the populate script**

```python
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

def collect_tokens(csv_paths: list[str]) -> list[str]:
    seen: set[str] = set()
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
    print(f"Cache saved to {sedra._cache_path}")

if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Run the populate script**

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
python3 scripts/populate_sedra_cache.py data/corpora/ephrem_nisibis.csv
```

Expected: runs for several minutes (0.15s × unique tokens); prints progress every 100. Final output: `data/roots/sedra_cache.json` created.

- [ ] **Step 3: Verify the cache**

```bash
python3 -c "
import json
with open('data/roots/sedra_cache.json', encoding='utf-8') as f:
    cache = json.load(f)
total = len(cache)
hits = sum(1 for v in cache.values() if v is not None)
print(f'Cache entries: {total}')
print(f'Hits (SEDRA found): {hits} ({100*hits/total:.1f}%)')
print(f'Misses (not in SEDRA): {total-hits} ({100*(total-hits)/total:.1f}%)')
"
```

Expected: a meaningful hit rate (SEDRA covers Peshitta NT well; Ephrem-specific hapax legomena will be misses).

- [ ] **Step 4: Commit**

```bash
git add scripts/populate_sedra_cache.py data/roots/sedra_cache.json
git commit -m "feat(sedra): pre-populate SEDRA cache for Ephrem Nisibis tokens"
```

---

## Task 5: Register corpus in app.py and add to CORPUS_CHRONOLOGY

**Files:**
- Modify: `app.py` (2 sites)

- [ ] **Step 1: Add corpus registration in `_init()` (~line 80)**

In `app.py`, in the `_init()` function, after the `targum_onkelos` block and before `_corpus.load()`:

```python
        en_path = os.path.join(CORPORA_DIR, 'ephrem_nisibis.csv')
        if os.path.exists(en_path):
            _corpus.add_corpus('ephrem_nisibis', 'Ephrem — Nisibis', en_path)
```

- [ ] **Step 2: Add to CORPUS_CHRONOLOGY (~line 2059)**

The Hymns on Nisibis were composed c. 350–363 CE. Add after `peshitta_ot`:

```python
CORPUS_CHRONOLOGY = [
    ('biblical_aramaic', 'Biblical Aramaic', '~6th–2nd c. BCE'),
    ('targum_onkelos',   'Targum Onkelos',   '~1st–3rd c. CE'),
    ('peshitta_nt',      'Peshitta NT',      '~2nd–5th c. CE'),
    ('peshitta_ot',      'Peshitta OT',      '~2nd–5th c. CE'),
    ('ephrem_nisibis',   'Ephrem — Nisibis', '~350–363 CE'),
]
```

- [ ] **Step 3: Test the app starts and corpus loads**

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
python3 -c "
import app
app._init()
info = app._corpus._corpora.get('ephrem_nisibis')
print('Corpus loaded:', info)
print('Verse count:', info.verse_count if info else 'NOT LOADED')
"
```

Expected: prints corpus info with a non-zero verse count.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat(corpus): register ephrem_nisibis corpus and add to CORPUS_CHRONOLOGY"
```

---

## Task 6: Add SEDRA fallback in app.py word resolution

**Files:**
- Modify: `app.py` (3 targeted sites)

The SEDRA fallback applies when our extractor returns confidence < 0.5. It is applied in two places: the verse reader's word-level popover data (`api_verse`, ~line 590) and the interlinear word loop (`api_interlinear`, ~line 607).

The fallback logic is identical in both places — extract it into a module-level helper.

- [ ] **Step 1: Initialize SedraLookup in `_init()` (~line 95)**

After `_extractor.build_index()`, add:

```python
        from aramaic_core.sedra_lookup import SedraLookup
        global _sedra
        _sedra = SedraLookup()
        _sedra.load_cache()
```

And at module level near the other globals (~line 30), add:

```python
_sedra = None
```

- [ ] **Step 2: Add `_resolve_word()` helper after `_root_translit()` (~line 700)**

```python
def _resolve_word(word: str, script: str) -> dict:
    """Return root/confidence/gloss for a word, with SEDRA fallback for low-confidence.

    Returns dict with keys: root_syr, root_translit, confidence, gloss, stem, sedra_used.
    """
    result = _extractor.lookup_word_root_with_confidence(word)
    sedra_used = False

    if result is not None:
        root_syr, conf = result
    else:
        root_syr, conf = None, 0.0

    # SEDRA fallback for low-confidence or unresolved tokens
    if (root_syr is None or conf < 0.5) and _sedra is not None:
        sedra_data = _sedra.lookup(word)
        if sedra_data and sedra_data.get('stem'):
            sedra_root = sedra_data['stem']
            if root_syr is None:
                root_syr = sedra_root
                conf = 0.65
            else:
                # SEDRA agrees with our extraction — boost confidence
                if sedra_root == root_syr:
                    conf = 0.70
                else:
                    # SEDRA disagrees — prefer SEDRA (it's the professional lexicon)
                    root_syr = sedra_root
                    conf = 0.65
            sedra_used = True

    stem = _extractor.lookup_word_stem(word) or ''
    gloss = ''
    if root_syr:
        gloss = _extractor.get_root_gloss(root_syr) or ''
        if not gloss:
            cognate = _cognate_lookup.lookup(root_syr)
            if cognate:
                gloss = cognate.gloss_en or ''

    return {
        'root_syr': root_syr,
        'root_translit': _root_translit(root_syr, script) if root_syr else '',
        'root_key': _translit_to_dash(root_syr) if root_syr else '',
        'confidence': round(conf, 2),
        'gloss': gloss,
        'stem': stem,
        'sedra_used': sedra_used,
    }
```

- [ ] **Step 3: Use `_resolve_word()` in `api_interlinear` (~line 607)**

In the interlinear word loop, find the existing word resolution block (it currently calls `_extractor.lookup_word_root_with_confidence(w)` directly). Replace the per-word resolution section with:

```python
                resolved = _resolve_word(w, script)
                root_syr     = resolved['root_syr']
                root_translit = resolved['root_translit']
                root_key      = resolved['root_key']
                confidence    = resolved['confidence']
                gloss         = resolved['gloss']
                stem          = resolved['stem']
```

Leave the transliteration (`t`) computation above this block unchanged — it handles the display script, not the root.

- [ ] **Step 4: Verify interlinear works for an Ephrem verse**

Start the dev server and test:

```bash
python3 app.py &
sleep 2
curl -s "http://localhost:5001/api/interlinear?book=Nisibis&ch_start=1&v_start=1&ch_end=1&v_end=3&script=latin&lang=en" | python3 -m json.tool | head -60
```

Expected: JSON with `verses` array containing words with `root`, `root_key`, `confidence`, `gloss`. Some `confidence` values should be 0.65 (SEDRA-resolved).

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "feat(sedra): add SEDRA fallback in word resolution for low-confidence tokens"
```

---

## Task 7: Re-measure confidence with SEDRA fallback

- [ ] **Step 1: Extend measure_confidence.py to use SEDRA**

Add a `--sedra` flag. When set, apply `_resolve_word()` logic on low-confidence tokens.

In `scripts/measure_confidence.py`, add after the existing `main()` body (before `if __name__`):

```python
def main_with_sedra(csv_path: str):
    """Re-measure confidence after applying SEDRA fallback."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from aramaic_core.sedra_lookup import SedraLookup

    corpus_id = os.path.splitext(os.path.basename(csv_path))[0]
    corpus = AramaicCorpus()
    corpus.add_corpus(corpus_id, corpus_id, csv_path)
    corpus.load()
    extractor = RootExtractor(corpus, ROOTS_DIR)
    extractor.build_index()

    sedra = SedraLookup()
    sedra.load_cache()

    high = med = low = none_ = sedra_resolved = 0

    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for word in (row.get('syriac') or '').split():
                result = extractor.lookup_word_root_with_confidence(word)
                root_syr = result[0] if result else None
                conf     = result[1] if result else 0.0

                if root_syr is None or conf < 0.5:
                    sd = sedra.lookup(word)
                    if sd and sd.get('stem'):
                        conf = 0.65
                        sedra_resolved += 1

                if conf >= 0.8:
                    high += 1
                elif conf >= 0.5:
                    med += 1
                elif conf > 0.0:
                    low += 1
                else:
                    none_ += 1

    total = high + med + low + none_
    print(f"\nCorpus: {corpus_id} (with SEDRA fallback)")
    print(f"Total tokens: {total}")
    print(f"  High (≥0.8):  {high:>6}  ({100*high/total:.1f}%)")
    print(f"  Medium (≥0.5):{med:>6}  ({100*med/total:.1f}%)")
    print(f"  Low (<0.5):   {low:>6}  ({100*low/total:.1f}%)")
    print(f"  No root:      {none_:>6}  ({100*none_/total:.1f}%)")
    print(f"  SEDRA resolved: {sedra_resolved} tokens lifted from low/none")
```

Update `if __name__ == '__main__':` to:

```python
if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[-1] == '--sedra':
        main_with_sedra(sys.argv[1])
    else:
        main()
```

- [ ] **Step 2: Run comparison**

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
echo "=== BEFORE SEDRA ===" && python3 scripts/measure_confidence.py data/corpora/ephrem_nisibis.csv
echo "=== AFTER SEDRA ===" && python3 scripts/measure_confidence.py data/corpora/ephrem_nisibis.csv --sedra
```

Expected: the `--sedra` run shows meaningfully fewer `none_` and `low` tokens. Record the improvement for the commit message.

- [ ] **Step 3: Commit**

```bash
git add scripts/measure_confidence.py scripts/populate_sedra_cache.py
git commit -m "feat(scripts): extend measure_confidence to benchmark SEDRA fallback improvement"
```

---

## Task 8: Smoke-test the full stack

- [ ] **Step 1: Start the server**

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
python3 app.py
```

- [ ] **Step 2: Check the browse page shows Ephrem**

Open `http://localhost:5001/browse` — the corpus filter tabs should include "Ephrem — Nisibis".

- [ ] **Step 3: Read a Nisibis passage**

Open `http://localhost:5001/read/Nisibis/1` — stanzas should render with word popovers. Some words should show SEDRA gloss (the popover's gloss line).

- [ ] **Step 4: Check diachronic analysis**

Open `http://localhost:5001/diachronic` — search for root ܫܠܡ. The corpus bar chart should now include an "Ephrem — Nisibis" bar at ~350–363 CE.

- [ ] **Step 5: Check interlinear reader**

Open `http://localhost:5001/interlinear` — select corpus "Ephrem — Nisibis", book "Nisibis", range 1:1–1:5. Analyze. Words should render with roots and glosses.

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "chore: final smoke-test pass — Ephrem Nisibis corpus live with SEDRA fallback"
```

---

## Task 9: User validates and tests at localhost:5001

This task is owned by the user. No subagent is dispatched.

- [ ] **Step 1: Start the server (if not already running)**

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
python3 app.py
```

- [ ] **Step 2: Validate in the browser**

Open http://localhost:5001 and check:
- Browse → corpus tabs include "Ephrem — Nisibis"
- Read a Nisibis passage (e.g. `/read/Nisibis/1`) — word popovers show roots and glosses
- Interlinear → select Ephrem — Nisibis, range 1:1–1:5 → roots and SEDRA-boosted glosses appear
- Diachronic → root ܫܠܡ → bar for Ephrem — Nisibis is present

- [ ] **Step 3: Confirm to proceed with deployment**

Tell Claude "looks good, deploy" (or report any issues to fix first).

---

## Self-Review

**Spec coverage check:**
- ✅ Load Hymns on Nisibis from DSC (Task 1)
- ✅ Measure confidence baseline (Task 2)
- ✅ SEDRA lookup module with cache (Task 3)
- ✅ Cache population script (Task 4)
- ✅ Register corpus in app.py (Task 5)
- ✅ SEDRA fallback in word resolution (Task 6)
- ✅ Re-measure with SEDRA (Task 7)
- ✅ Full stack smoke test (Task 8)

**Placeholder scan:** None found. All steps have concrete commands or code.

**Type consistency:**
- `_resolve_word()` returns dict with keys `root_syr`, `root_translit`, `root_key`, `confidence`, `gloss`, `stem`, `sedra_used` — used consistently in Task 6.
- `SedraLookup.lookup()` returns `Optional[dict]` with keys `stem`, `gloss`, `category`, `kaylo` — used consistently in Tasks 3, 4, 6, 7.

**Known risk:** The DSC TEI XML structure may differ from what the plan assumes (element names, namespace prefix, hymn div nesting). Task 1 Step 4 includes a diagnostic command to inspect a raw file and adjust accordingly.
