# Search Algorithms — Aramaic Root Atlas

How each of the five search modes on the homepage actually ranks results.
Documented because [opaque ranking is a credibility risk](ROADMAP-v3.1.md)
for any tool used in scholarly work — researchers should be able to know
*why* a particular root surfaces first.

> **TL;DR:** The "Search by meaning" and "Search by cognate" modes use a
> simple weighted heuristic over the gloss strings carried by each root.
> They are *not* embedding-based, semantic-similarity, or learned models.
> Reverse lookup ranks by how literally the query string matches translator
> glosses (WEB / Reina-Valera 1909 / WLC / Van Dyck), which encodes
> translator decisions, not the underlying Aramaic semantic range.

---

## 1. Search by root (`/api/roots?q=…`)

**Input formats accepted, in this order:**
- Latin transliteration with dashes (e.g. `SH-L-M`, `K-T-B`, `Q-D-SH`)
- Plain Latin without dashes (e.g. `SHLM`, `KTB`)
- Syriac Unicode (e.g. `ܫܠܡ`)
- Hebrew square script (e.g. `שלם`)
- Arabic (e.g. `سلم`)

The auto-detect routine in `aramaic_core/characters.py` normalizes all
five inputs to a single canonical Latin key (e.g. `sh-l-m`), then looks
up the root in the in-memory index. **Exact-match only** — no fuzzy
matching, no edit-distance correction, no autocomplete typo recovery
(autocomplete suggestions are a separate prefix lookup).

**Ranking:** trivial — at most one root matches a normalized key. If no
match, the response is empty; the UI then falls back to the "Search by
cognate" mode if the input looks like a Hebrew/Arabic word.

---

## 2. Search by cognate (`/api/cognate-lookup?word=…`)

Reverse lookup: given a Hebrew, Arabic, or transliterated cognate, find
the Aramaic roots it links to.

**Index structure:** an inverted index built at startup from
`data/roots/cognates.json`. Each cognate entry contributes one or more
search terms (the cognate's surface form, transliteration, and bilingual
glosses) keyed back to the root.

**Matching:**
- Direct equality on the cognate's `word`, `transliteration`, or any
  bilingual gloss → match.
- Partial substring containment → match (lower priority).

**Ranking:** matches are returned in the order the cognates appear in
the JSON file (no scoring). The UI groups by root, so multiple cognates
of the same root collapse into one card.

**Caveat:** cognates are **LLM-generated and not yet validated against
authoritative lexicons** (see [README § Limitations](../README.md#limitations--caveats)).
The reverse-lookup result should be treated as a starting point for
verification, not as authoritative cognate evidence.

---

## 3. Search by meaning (`/api/reverse-search?q=…&lang=en|es`)

The most heuristic of the five. Given a meaning in English or Spanish,
return Aramaic roots ranked by how closely their *glosses* match.

### Index

At startup the server builds `_reverse_idx`: per language (en, es), a
list of entries each containing:

```python
{
  'key':          'sh-l-m',          # canonical root key
  'root_syriac':  'ܫܠܡ',
  'gloss':        'peace; well-being; greeting',  # primary translator gloss
  'sabor':        'wholeness, completion',         # poetic root flavor
  'terms':        ['peace', 'well-being', 'greeting'],  # individual gloss tokens
  'occurrences':  1247,
}
```

The `gloss` strings come from the manual cognate file plus the
translator-supplied glosses for high-frequency forms (WEB for English,
RV1909 for Spanish). The `terms` array is the gloss tokenized on
punctuation and whitespace.

### Scoring

For a query string `q` (lowercased, split into `query_words`) and an
entry `e`:

```
score = 0
if q == e.gloss:                         score += 100   # exact gloss match
elif q is substring of e.gloss:          score +=  50   # phrase containment

for each query word qw:
  for each term t in e.terms:
    if qw == t:                          score += 30 (3 × 10)  # exact word
    elif qw substring or prefix of t:    score += 10           # partial word

if q is substring of e.sabor:            score +=   5           # poetic match
```

Tie-break: higher `occurrences` ranks first.

Top 30 returned.

### Why this matters for users

- **The ranking is biased toward translator vocabulary.** A search for
  "love" ranks roots whose WEB / RV1909 gloss is literally "love"
  highest. Roots glossed as "compassion" or "mercy" (e.g. R-KH-M) may
  rank lower despite being semantically closer to the Aramaic concept.
- **No stemming, no synonym expansion, no embedding similarity.**
  A search for "loving" will not match glosses containing "love" unless
  the query word is a substring of a gloss term.
- **No multilingual fallback** beyond the requested `lang`. An English
  query won't surface roots whose only glossed meaning is in Spanish.
- **`occurrences` tie-breaker biases toward high-frequency roots** like
  *say*, *do*, *go*, *know*. For rare-but-precise meanings, scroll past
  the first few hits.

### What to do if the result feels wrong

This is exactly the situation the search-by-meaning mode is bad at —
mismatches between English/Spanish translator vocabulary and the
underlying Aramaic semantic range. For research-grade results, cross-check
against the Hebrew/Arabic cognate fields (mode 2 above) and the actual
verse attestations on each root's family page.

---

## 4. Co-occurrence search (`/api/proximity-search?root1=…&root2=…&scope=verse|chapter`)

Given two root keys, returns all verses (or chapters) in which both
appear within the specified scope window.

**Algorithm:** literal set intersection on the per-corpus inverted indices
of `(root → list of verse IDs)`. Scope `verse` requires same verse ID;
scope `chapter` requires same `(book, chapter)`.

**Ranking:** none — results returned in canonical book order.

---

## 5. Text search (`/api/search?q=…&lang=…&corpus=…`)

Full-text search across the **translation tracks** (WEB / RV1909 / WLC /
Van Dyck / SBLGNT), **not** across the original Aramaic/Syriac/Hebrew
text. Implemented as a case-insensitive substring scan in
`AramaicCorpus.search_text`.

**Ranking:** none. Results returned in (corpus, book, chapter, verse)
order. When `corpus_filter` is omitted and total results > 50, results are
**interleaved** across corpora (round-robin) so a user typing "peace" at
"All Corpora" sees a representative sample from each instead of all
Peshitta NT hits first.

**Caveat:** because this searches translations, results reflect the
**translator's word choice**, not the Aramaic original. The Hebrew (WLC)
track is the primary text for Biblical Aramaic; for the other corpora,
all translation tracks are derivative.

---

## What's not implemented (yet)

- **No semantic / embedding similarity** between glosses or roots
- **No stemming or lemmatization** of the English/Spanish query
- **No fuzzy matching / edit-distance** correction for typos in the root key
- **No relevance feedback or learning-to-rank**
- **No query expansion** via WordNet, ConceptNet, or theological lexicons
  (e.g. *Dictionary of Biblical Theology* keys)
- **No phrase / proximity operators** ("near", boolean AND/OR)

These are reasonable next-version improvements but would require either
a real search backend (Whoosh, Tantivy, MeiliSearch) or
sentence-transformer-based semantic indexing. Both are tracked in
`docs/ROADMAP-v3.1.md` as Phase 2+ work.

---

## How to verify a search result for academic use

1. Use **Search by root** (mode 1) to look up the candidate root explicitly
   by transliteration. Confirm gloss against an authoritative lexicon
   (Brockelmann, Sokoloff, Costaz).
2. Cross-check the cognate connection in mode 2 against HALOT (Hebrew),
   Lane / Wehr (Arabic), or DJBA (Babylonian Aramaic).
3. Spot-check at least 3 verse attestations on the root family page; the
   gloss given in the reverse-search index reflects only the most
   frequent translator choice, not the full distribution.
4. For diachronic claims, see the disclosure note in `docs/ROADMAP-v3.1.md`
   (Phase 2.8): genre and chronology are confounded in the Atlas's
   current corpora, and frequency comparisons across them should be
   interpreted with that in mind.

---

*Last updated: 2026-05-09. If the algorithm changes in a future release,
this document and the corresponding entry in `CHANGELOG.md` will be
updated together.*
