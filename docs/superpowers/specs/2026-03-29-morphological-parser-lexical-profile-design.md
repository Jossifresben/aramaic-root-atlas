# Design: Full Morphological Word Parser + Passage Lexical Profile

**Date:** 2026-03-29
**Status:** Approved for implementation
**Branch:** to be implemented on a new feature branch

---

## Overview

Two complementary philological features that expose the full morpho-lexical infrastructure already embedded in `aramaic_core/` to scholars who need granular analysis tools.

- **Feature 1 — Full Morphological Word Parser**: surfaces the complete morpheme breakdown of any Syriac/Aramaic word: prefixes → root → suffixes, with grammatical labels, part-of-speech, verb stem (binyan), confidence score, gloss, and cognate links — all in one API call and an enhanced word popover in the reader.
- **Feature 2 — Passage Lexical Profile**: a dedicated analysis page where a scholar selects a book and verse range, then receives a rich statistical portrait of that passage's vocabulary: unique roots, hapax density, rarity distribution, verb stem breakdown, semantic field coverage, and a verse-by-verse root-density chart.

---

## Feature 1 — Full Morphological Word Parser

### Problem it solves

Today, clicking a word in the reader shows a basic popover: root, gloss, confidence, and stem. Scholars who work with morphology need the full picture: *which prefixes were stripped? which suffixes? what is the grammatical function of each affix?* This is critical for teaching, commentary writing, and manuscript comparison. No free web tool currently exposes Syriac morpheme segmentation this cleanly.

### Architecture

**New API endpoint**: `GET /api/word-parse?word=<syriac_word>&corpus=<optional>`

Calls into existing infrastructure:
1. `affixes.strip_prefixes(word)` → list of `(prefix_char, label)` stripped in order
2. `affixes.strip_suffixes(stem)` → list of `(suffix_char, label)` stripped in order
3. Root lookup via `_word_to_root[word]` (or re-derive from extractor)
4. Stem lookup via `_word_to_stem[word]`
5. Confidence from `_word_to_score[word]`
6. Cognate lookup via `_cognate_lookup.lookup(root_key, lang)`
7. Compose response object (see schema below)

**Response schema:**
```json
{
  "word": "ܘܫܠܡܘ",
  "script": "syriac",
  "root": "ܫܠܡ",
  "root_key": "sh-l-m",
  "stem": "peal",
  "confidence": 0.92,
  "pos_guess": "verb",
  "prefixes": [
    {"char": "ܘ", "label": "conjunction (waw)"}
  ],
  "suffixes": [
    {"char": "ܘ", "label": "3mp subject suffix"}
  ],
  "gloss_en": "to complete, finish, make peace",
  "gloss_es": "completar, hacer paz",
  "gloss_he": "לְהַשְׁלִים, שָׁלוֹם",
  "gloss_ar": "يُكمل، يُسالم",
  "cognates": {
    "hebrew": "שָׁלַם / שָׁלוֹם",
    "arabic": "سَلِمَ / سَلَام"
  },
  "corpus_attestations": {"peshitta_nt": 142, "peshitta_ot": 318, "biblical_aramaic": 5, "targum_onkelos": 27}
}
```

**POS guess logic** (heuristic, not full tagger):
- If stem is in `{peal, ethpeel, pael, ethpaal, aphel, shafel, ettaphal}` → "verb"
- Else if word ends in known nominal suffixes → "noun"
- Else → "unknown"

**Enhanced word popover in `read.html`**:

Replace current popover structure with a segmented morpheme display:

```
PREFIX  |  ROOT  |  SUFFIX
  ܘ     |  ܫܠܡ  |   ܘ
conj.  | sh-l-m | 3mp
─────────────────────────
Stem: Peal  ·  Confidence: High
Gloss: to complete, make peace
Hebrew cognate: שָׁלַם · Arabic: سَلِمَ
[View root family →]
```

Morpheme boxes use distinct colors (prefix = teal, root = gold, suffix = purple) consistent with existing stem-badge palette. The popover is wider (380px vs current ~280px) on desktop, full-width on mobile.

**New page**: `GET /parse?word=<optional_prefill>&lang=<lang>`

A standalone word parser page where any user can type or paste a Syriac word and see the full morphological breakdown. Useful for teachers, students, and anyone not reading in the `/read/` view. Has a "copy citation" button that outputs a LaTeX-style morpheme gloss line (Leipzig glossing standard).

### Files modified
| File | Change |
|------|--------|
| `app.py` | Add `GET /api/word-parse` endpoint; add `GET /parse` page route |
| `templates/read.html` | Enhanced word popover (morpheme boxes, wider, cognate row) |
| `templates/parse.html` | New standalone parser page |
| `templates/base.html` | Add "Word Parser" link under Research dropdown |
| `static/style.css` | Morpheme box styles, wider popover |
| `data/i18n.json` | ~12 new keys |

### i18n keys
`parse_title`, `parse_subtitle`, `parse_input_placeholder`, `parse_analyze`, `parse_prefixes`, `parse_root`, `parse_suffixes`, `parse_stem`, `parse_confidence`, `parse_cognates`, `parse_pos`, `parse_copy_gloss`

---

## Feature 2 — Passage Lexical Profile

### Problem it solves

Scholars preparing commentaries, dissertations, or translations need to understand the lexical character of a passage as a whole: how rare is its vocabulary? how dense are the verbs? which semantic domains dominate? This kind of *passage-level statistical lexicography* is what tools like CATSS or Accordance do for Greek/Hebrew but with narrow scope and high cost. The Atlas can provide it freely, across all four Aramaic corpora, in seconds.

### Architecture

**New API endpoint**: `GET /api/passage-profile?book=Matthew&ch_start=5&ch_end=7&v_start=1&v_end=48&corpus=`

Processing pipeline:
1. Collect all verse refs in range using `_corpus.get_chapter_verses()` across chapters
2. For each word in those verses: look up root via `_word_to_root`; skip stopwords
3. Aggregate per root: occurrence count within passage, total corpus count, stem distribution
4. Compute metrics:
   - `unique_roots` — count of distinct root keys
   - `total_words` — token count (excluding stopwords)
   - `lexical_density` — unique_roots / total_words
   - `hapax_in_passage` — roots occurring exactly once in the passage
   - `corpus_hapaxes` — roots whose total corpus count ≤ 1 (absolute hapaxes)
   - `rarity_buckets` — {hapax: N, rare(2-5): N, common(6-20): N, very_common(21+): N}
   - `stem_distribution` — {peal: N, ethpeel: N, pael: N, ...}
   - `top_roots` — top 15 by passage frequency with gloss and corpus count
   - `semantic_fields` — if `data/roots/semantic_fields.json` loaded: domain distribution (counts per domain, top domain)
   - `verse_density` — list of `{ref, root_count, unique_root_count}` per verse for the density chart
   - `confidence_dist` — {high: N, medium: N, low: N}

**Response schema (abbreviated):**
```json
{
  "passage": "Matthew 5–7",
  "verse_count": 111,
  "word_count": 1842,
  "unique_roots": 287,
  "lexical_density": 0.156,
  "hapax_in_passage": 43,
  "corpus_hapaxes": 12,
  "rarity_buckets": {"hapax": 43, "rare": 89, "common": 112, "very_common": 43},
  "stem_distribution": {"peal": 145, "ethpeel": 32, "pael": 28, ...},
  "top_roots": [...],
  "semantic_fields": {"worship/cultic": 34, "speech/communication": 28, ...},
  "verse_density": [{"ref": "Matthew 5:3", "root_count": 8, "unique": 7}, ...],
  "confidence_dist": {"high": 201, "medium": 58, "low": 28}
}
```

**New page**: `GET /passage-profile?lang=<lang>`

Layout (single-column, scholarly feel):

```
┌─────────────────────────────────────────────────┐
│  Passage Lexical Profile                        │
│  Book: [Matthew ▼]  Ch: [5] – [7]  [Analyze]  │
└─────────────────────────────────────────────────┘

  Summary Cards (row):
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │ 287      │  │ 15.6%    │  │ 43       │  │ 12       │
  │ Unique   │  │ Lexical  │  │ Passage  │  │ Corpus   │
  │ Roots    │  │ Density  │  │ Hapaxes  │  │ Hapaxes  │
  └──────────┘  └──────────┘  └──────────┘  └──────────┘

  ┌───────────────────────────┐  ┌───────────────────┐
  │ Root Frequency Rarity     │  │ Verb Stem Dist.   │
  │ [stacked bar chart]       │  │ [pie / donut]     │
  └───────────────────────────┘  └───────────────────┘

  ┌──────────────────────────────────────────────────┐
  │ Verse-by-Verse Root Density                      │
  │ [sparkline / bar chart — one bar per verse]      │
  └──────────────────────────────────────────────────┘

  ┌──────────────────────┐  ┌─────────────────────┐
  │ Top 15 Roots         │  │ Semantic Domains     │
  │ [table w/ freq bar]  │  │ [horizontal bars]    │
  └──────────────────────┘  └─────────────────────┘

  [Export JSON]  [Export CSV]  [Copy passage citation]
```

Charts use D3.js (already in project). All sections collapse gracefully if data is absent (e.g., semantic fields not generated yet).

**Cross-chapter range support**: `ch_start`/`ch_end` with optional `v_start`/`v_end`. If v_start/v_end omitted, include full chapters. Single chapter: ch_start == ch_end.

### Files modified
| File | Change |
|------|--------|
| `app.py` | Add `GET /api/passage-profile` endpoint; add `GET /passage-profile` page route |
| `templates/passage_profile.html` | New page |
| `templates/base.html` | Add "Passage Profile" link under Research dropdown |
| `data/i18n.json` | ~18 new keys |

### i18n keys
`pp_title`, `pp_subtitle`, `pp_book_label`, `pp_chapter_from`, `pp_chapter_to`, `pp_analyze`, `pp_unique_roots`, `pp_lexical_density`, `pp_passage_hapaxes`, `pp_corpus_hapaxes`, `pp_rarity_dist`, `pp_stem_dist`, `pp_verse_density`, `pp_top_roots`, `pp_semantic_domains`, `pp_col_root`, `pp_col_freq`, `pp_col_rarity`

---

## Implementation Order

1. Feature 1 — API endpoint (`/api/word-parse`) — mostly wiring up existing data
2. Feature 1 — Enhanced popover in `read.html`
3. Feature 1 — Standalone `/parse` page
4. Feature 2 — API endpoint (`/api/passage-profile`)
5. Feature 2 — Page + charts (`passage_profile.html`)
6. i18n keys for both features (all 4 languages)
7. base.html nav links
8. CSS additions

---

## Out of Scope

- Full morphological tagger (deterministic POS for every word) — the heuristic POS guess is sufficient for v1; a trained tagger is a separate project
- Saving/exporting passage profiles as PDFs — export JSON/CSV is sufficient
- Comparing two passages side-by-side — future feature

---

## Verification Checklist

### Feature 1 — Morphological Parser
1. `GET /api/word-parse?word=ܘܫܠܡܘ` → returns prefixes, root `sh-l-m`, suffixes, stem, gloss in all 4 langs
2. Open `/read/Matthew/5`, click any word → enhanced popover shows morpheme boxes
3. Prefix/suffix boxes render in Syriac script, labels in UI language
4. Visit `/parse?lang=es` → type Syriac word → full Spanish-language breakdown
5. Copy gloss button → clipboard contains Leipzig-style gloss line

### Feature 2 — Passage Lexical Profile
1. Visit `/passage-profile?lang=en`, select Matthew ch 5–7, click Analyze
2. Summary cards show: unique roots, lexical density, hapax counts
3. Rarity distribution chart renders (stacked bar)
4. Stem distribution chart renders (donut)
5. Verse density sparkline: each verse has a bar proportional to its root count
6. Top 15 roots table shows correct frequency and gloss
7. Export CSV → downloadable file with root, freq, corpus_count, gloss columns
8. All labels update when switching UI language to es/he/ar
