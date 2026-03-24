# Aramaic Root Atlas

## Project Overview
A cross-corpus triliteral root explorer for Aramaic literature. Evolved from the [Peshitta Root Finder](https://peshitta-roots.onrender.com) into a multi-corpus tool spanning ~1,500 years of Aramaic literary history.

## Architecture
- **aramaic_core/** — Shared linguistic engine (zero Flask dependencies)
  - `characters.py` — Syriac/Hebrew/Arabic character maps, transliteration, script detection
  - `affixes.py` — Prefix/suffix stripping rules for Syriac morphological analysis
  - `corpus.py` — `AramaicCorpus` class: multi-corpus CSV loader with corpus_id filtering
  - `extractor.py` — `RootExtractor`: triliteral root extraction + scoring engine
  - `cognates.py` — `CognateLookup`: Hebrew & Arabic cognate lookup
  - `glosser.py` — `WordGlosser`: compositional word-level glossing (EN/ES)
- **app.py** — Flask app (port 5001)
- **templates/** — Jinja2 templates (base, index, browse, read, about)
- **static/style.css** — CSS with corpus-coded color variables
- **data/** — Organized subdirectories:
  - `corpora/` — CSV files (peshitta_nt.csv, peshitta_ot.csv)
  - `roots/` — cognates.json, known_roots.json, stopwords.json, word_glosses_override.json
  - `translations/` — translations_{en,es,he,ar}.json
- **scripts/** — Data pipeline scripts
  - `fetch_ot_translations.py` — Fetch OT translations from bible.helloao.org (EN/ES/HE)
  - `generate_new_cognates.py` — Generate cognates for uncovered roots via Claude API
- **docs/PRD.md** — Full product requirements document with 4-phase roadmap

## Current State (Phase 1 — OT Complete)
- **Full Peshitta OT**: All 39 books loaded (23,072 verses, 309,889 words)
- **Full Peshitta NT**: 22 books (7,440 verses, 101,469 words)
- **Total**: 30,512 verses, 411,358 words, 56,062 unique forms
- **4,299 roots** indexed across both corpora (up from 3,329)
- **1,127 cognate entries** with Hebrew/Arabic cognates, semantic bridges
- Corpus filtering works on all API endpoints (?corpus=peshitta_nt|peshitta_ot)
- Bilingual UI (EN/ES) with EN/ES/HE/AR translation tracks
- OT data source: ETCBC/peshitta (CC-BY-NC, Leiden Peshitta Institute)
- Translation sources: WEB (EN), Reina-Valera 1909 (ES), WLC (HE), Van Dyck (AR) via bible.helloao.org

## API Routes
- `GET /` — Home page with search + stats
- `GET /browse` — Book browser with corpus filter tabs
- `GET /read/<book>/<chapter>` — Verse reader with translation selector
- `GET /about` — About page
- `GET /api/stats` — Corpus statistics JSON
- `GET /api/roots?q=SH-L-M&corpus=peshitta_ot` — Root search with optional corpus filter
- `GET /api/books?corpus=peshitta_nt` — Book list with optional filter
- `GET /api/chapter/<book>/<chapter>?trans=es` — Chapter verses with translation
- `GET /api/search?q=peace&lang=en&corpus=` — Text search across corpora

## Run
```bash
python3 app.py  # starts on port 5001
```

## Relationship to Peshitta Root Finder
- This is a **separate repo** (Option C from the PRD: two repos, shared core)
- Core modules were copied from `peshitta-root-finder/peshitta_roots/` and adapted
- Key change: `PeshittaCorpus` → `AramaicCorpus` with multi-corpus support
- The Peshitta app stays clean and stable; this app is multi-corpus by design
- Bug fixes can be cherry-picked between repos; formalize shared package later if needed

## Phase 1 Complete
- ✅ Cognates generated for 493 new roots (1,127 total; ~2,085 patterns were non-roots)
- ✅ Arabic translations fetched: Van Dyck (arb_vdv) via bible.helloao.org (30,585 verses)
- ✅ Arabic translation track added to reader UI with RTL support

## Next Steps (Phase 2 — Biblical Aramaic)
1. Add Biblical Aramaic corpus (Daniel 2:4b-7:28, Ezra 4:8-6:18) from Sefaria API
2. Cross-script root normalization (Hebrew square script → shared Latin root key)
3. Cross-corpus root card (attestation across corpora)
4. Constellation visualization (D3.js, ported from Peshitta app)
5. Proximity search (co-occurring roots, ported from Peshitta app)

## Conventions
- Syriac text uses Unicode (U+0710-U+074F), stored as-is in CSV
- Roots are 2-3 character Syriac strings (e.g., ܫܠܡ for SH-L-M)
- Root keys in cognates.json use Latin transliteration: "sh-l-m"
- Verse references follow "Book Chapter:Verse" format (e.g., "Psalms 1:1")
- Bilingual: every user-facing string has EN and ES variants via i18n.json
