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
  - `cognates.py` — `CognateLookup`: Hebrew, Arabic & Greek cognate lookup
  - `glosser.py` — `WordGlosser`: compositional word-level glossing (EN/ES)
- **app.py** — Flask app (port 5001)
- **templates/** — Jinja2 templates (base, index, browse, read, about)
- **static/style.css** — CSS with corpus-coded color variables
- **data/** — Organized subdirectories:
  - `corpora/` — CSV files (peshitta_nt.csv, peshitta_ot.csv, biblical_aramaic.csv, targum_onkelos.csv)
  - `roots/` — cognates.json, known_roots.json, stopwords.json, word_glosses_override.json
  - `translations/` — translations_{en,es,he,ar}.json
- **scripts/** — Data pipeline scripts
  - `fetch_ot_translations.py` — Fetch OT translations from bible.helloao.org (EN/ES/HE)
  - `generate_new_cognates.py` — Generate cognates for uncovered roots via Claude API
  - `fetch_biblical_aramaic.py` — Fetch BA corpus from Sefaria API
- **docs/PRD.md** — Full product requirements document with 4-phase roadmap

## Current State (All Phases Complete)
- **4 corpora**: Peshitta NT (7,440v), Peshitta OT (23,072v), Biblical Aramaic (269v), Targum Onkelos (5,846v)
- **Total**: 36,627 verses, 498,922 words, 72,566 unique forms
- **5,039 roots** indexed across all corpora
- **1,127 cognate entries** with Hebrew/Arabic cognates, semantic bridges
- **2,192 Greek NT cognates** linking Aramaic roots to Greek equivalents in the visualizer
- Greek NT translation track (SBLGNT) — 7,939 verses from bible.helloao.org (grc_sbl)
- Quadrilingual UI (EN/ES/HE/AR) with 5 translation tracks
- Corpus filtering on all API endpoints (?corpus=peshitta_nt|peshitta_ot|biblical_aramaic|targum_onkelos)
- Root family visualizer (D3.js force graph + root card)
- Parallel viewer (Peshitta OT ↔ Targum Onkelos / Biblical Aramaic)
- Root frequency heat map with filter and CSV/JSON export
- Word-level root display with confidence scoring in reader
- Chapter root summary panel with frequency table and export
- Bookmarks with tags, CSV/JSON export, copy citation
- Production deployment: https://aramaic-root-atlas.onrender.com
- Data sources: ETCBC/peshitta (CC-BY-NC), Sefaria (CC-BY-SA), bible.helloao.org, SBLGNT (CC-BY-SA)

## API Routes
- `GET /` — Home page with search + stats
- `GET /browse` — Book browser with corpus filter tabs
- `GET /read/<book>/<chapter>` — Verse reader with translation selector
- `GET /bookmarks` — Bookmarks page (localStorage-based verse & root favorites)
- `GET /about` — About page
- `GET /api/stats` — Corpus statistics JSON
- `GET /api/roots?q=SH-L-M&corpus=peshitta_ot` — Root search with optional corpus filter
- `GET /api/books?corpus=peshitta_nt` — Book list with optional filter
- `GET /api/chapter/<book>/<chapter>?trans=es` — Chapter verses with translation
- `GET /api/search?q=peace&lang=en&corpus=` — Text search across corpora
- `GET /api/proximity-search?root1=SH-L-M&root2=K-TH-B&scope=verse` — Proximity search
- `GET /api/passage-constellation?book=Daniel&chapter=2&v_start=4&v_end=10` — Constellation data
- `GET /constellation?book=Matthew&chapter=5&v_start=1&v_end=5` — Constellation visualization page
- `GET /visualize/<root_key>` — Root family visualizer (D3 graph + card)
- `GET /api/root-family?root=SH-L-M` — Root family data (words, cognates, sister roots)
- `GET /parallel` — Parallel viewer (multi-corpus side-by-side)
- `GET /api/parallel?ref=Genesis+1:1` — Parallel texts for a verse across corpora
- `GET /heatmap` — Root frequency heat map page
- `GET /api/heatmap?limit=100&sort=total` — Heat map data (root frequency across corpora)
- `GET /api/suggest?prefix=SH` — Autocomplete suggestions for root search
- `GET /api/chapter-roots?book=Matthew&chapter=5` — All roots in a chapter sorted by frequency
- `GET /api/verse?ref=Matthew+5:3` — Single verse with word-level root data
- `GET /api/cognate-lookup?word=shalom` — Reverse lookup roots by Hebrew/Arabic/transliterated cognate
- `GET /api/reverse-search?q=peace&lang=en` — Search roots by English/Spanish meaning

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

## Phase 3 Complete — Targums & Beyond
- ✅ Targum Onkelos corpus loaded (5,853 verses, Torah only) via Sefaria API
- ✅ Synoptic parallel viewer (Peshitta OT ↔ Targum Onkelos / Biblical Aramaic side-by-side)
- ✅ Full root family visualizer page ported from Peshitta app (D3.js force graph + root card)
- ✅ Root frequency heat map with filter, progressive loading, CSV/JSON export
- ✅ Cross-corpus attestation badges in visualizer (NT, OT, BA, Targum counts)
- ✅ Sister roots discovery (roots sharing 2 of 3 consonants)
- ✅ Semantic bridges between outlier cognates
- ✅ Paradigmatic verse citation per root
- ✅ Heat Map added to navbar with i18n support
- ✅ Data source: Sefaria API (Targum Onkelos, CC-BY-SA)

## Phase 4 Complete — Polish & Scale
- ✅ Bookmark/favorites for roots and verses (localStorage-based, tags, CSV/JSON export, copy citation)
- ✅ Text search UI on homepage (Root Search / Text Search toggle)
- ✅ Mobile responsiveness fixes
- ✅ Deployed to production: https://aramaic-root-atlas.onrender.com
- ✅ TipTopJar support widget
- ✅ Footer with attribution, license, GitHub link

## Scholarly Improvements
- ✅ Root confidence scoring (High ≥0.8, Medium 0.5-0.8, Low <0.5)
- ✅ Word-level root display in reader (click word → popover with root, gloss, confidence, visualizer link)
- ✅ Chapter root summary ("Roots in this chapter" toggle with frequency table, CSV/JSON export)
- ✅ Methodological caveats on About page
- ✅ Enhanced bookmarks (tags, CSV export, copy citation)
- ✅ CITATION.cff for academic citation

## Conventions
- Syriac text uses Unicode (U+0710-U+074F), stored as-is in CSV
- Roots are 2-3 character Syriac strings (e.g., ܫܠܡ for SH-L-M)
- Root keys in cognates.json use Latin transliteration: "sh-l-m"
- Verse references follow "Book Chapter:Verse" format (e.g., "Psalms 1:1")
- Quadrilingual UI: every user-facing string has EN, ES, HE, AR variants via i18n.json
