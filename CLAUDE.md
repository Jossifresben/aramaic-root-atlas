# Aramaic Root Atlas

## Project Overview
A cross-corpus triliteral root explorer for Aramaic literature. Evolved from the [Peshitta Root Finder](https://peshitta-roots.onrender.com) into a multi-corpus tool spanning ~1,500 years of Aramaic literary history.

## Architecture
- **aramaic_core/** — Shared linguistic engine (zero Flask dependencies)
  - `characters.py` — Syriac/Hebrew/Arabic character maps, transliteration, script detection
  - `affixes.py` — Prefix/suffix stripping rules for Syriac morphological analysis
  - `affixes_hebrew.py` — Biblical Aramaic affix stripping (Hebrew square script)
  - `corpus.py` — `AramaicCorpus` class: multi-corpus CSV loader with corpus_id filtering
  - `extractor.py` — `RootExtractor`: triliteral root extraction + scoring engine
  - `cognates.py` — `CognateLookup`: Hebrew & Arabic cognate lookup
  - `glosser.py` — `WordGlosser`: compositional word-level glossing (EN/ES)
- **app.py** — Flask app (port 5001)
- **templates/** — Jinja2 templates (base, index, browse, read, about)
- **static/style.css** — CSS with corpus-coded color variables
- **data/** — Organized subdirectories:
  - `corpora/` — CSV files (peshitta_nt.csv, peshitta_ot.csv, biblical_aramaic.csv)
  - `roots/` — cognates.json, known_roots.json, stopwords.json, word_glosses_override.json
  - `translations/` — translations_{en,es,he,ar}.json
- **scripts/** — Data pipeline scripts
  - `fetch_ot_translations.py` — Fetch OT translations from bible.helloao.org (EN/ES/HE)
  - `generate_new_cognates.py` — Generate cognates for uncovered roots via Claude API
  - `fetch_biblical_aramaic.py` — Fetch BA corpus from Sefaria API
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
- `GET /api/proximity-search?root1=SH-L-M&root2=K-TH-B&scope=verse` — Proximity search
- `GET /api/passage-constellation?book=Daniel&chapter=2&v_start=4&v_end=10` — Constellation data
- `GET /constellation?book=Matthew&chapter=5&v_start=1&v_end=5` — Constellation visualization page

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
- ✅ Full Peshitta OT loaded (39 books, 23,072 verses, 309,889 words)
- ✅ Cognates generated for 493 new roots (1,127 total; ~2,085 patterns were non-roots)
- ✅ Translations fetched: EN (WEB), ES (RV1909), HE (WLC), AR (Van Dyck) via bible.helloao.org
- ✅ Arabic translation track added to reader UI with RTL support
- ✅ Book names localized in 4 languages (EN/ES/HE/AR, 61 books)
- ✅ 277 i18n UI keys per language (34 new keys added)
- ✅ Search with autocomplete, KWIC inline expansion, verse modal with prev/next
- ✅ Settings panel: transliteration, translation track, Syriac font (Estrangela/Eastern/Western)
- ✅ Language selector (EN/ES/HE/AR), dark mode, QR sharing
- ✅ Word highlighting in reader when navigating from search results
- ✅ Data pipeline scripts: fetch_ot_translations.py, generate_new_cognates.py

## Phase 2 Complete — Biblical Aramaic
- ✅ Biblical Aramaic corpus loaded (269 verses, 4,880 words from Daniel 2:4b-7:28, Ezra 4:8-6:18, 7:12-26, Genesis 31:47, Jeremiah 10:11)
- ✅ Cross-script root normalization: Hebrew כתב and Syriac ܟܬܒ resolve to same root key
- ✅ Hebrew affix stripping module (affixes_hebrew.py) for BA morphological analysis
- ✅ Cross-corpus attestation in root API (shows counts per corpus: NT, OT, BA)
- ✅ Root display in multiple scripts (Syriac + Hebrew when both attested)
- ✅ 4,485 roots indexed (up from 4,299), 57,849 unique word forms
- ✅ Constellation visualization ported from Peshitta app (D3.js force graph)
- ✅ Proximity search API ported (co-occurring roots across verse/chapter scope)
- ✅ 19 new i18n keys added (281 total per language)
- ✅ Data source: Sefaria API (Westminster Leningrad Codex, CC-BY-SA)
- ✅ Fetch script: scripts/fetch_biblical_aramaic.py

## Next Steps (Phase 3 — Targums & Beyond)
1. Add Targum Onkelos corpus (Aramaic translation of Torah)
2. Synoptic parallel viewer (Peshitta OT ↔ Biblical Aramaic side-by-side)
3. Full root family visualizer page (ported from Peshitta app)
4. Root frequency heat map across corpora
5. Export/download functionality (root data as CSV/JSON)

## Conventions
- Syriac text uses Unicode (U+0710-U+074F), stored as-is in CSV
- Roots are 2-3 character Syriac strings (e.g., ܫܠܡ for SH-L-M)
- Root keys in cognates.json use Latin transliteration: "sh-l-m"
- Verse references follow "Book Chapter:Verse" format (e.g., "Psalms 1:1")
- Quadrilingual UI: every user-facing string has EN, ES, HE, AR variants via i18n.json
