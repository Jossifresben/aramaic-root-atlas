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
- **docs/PRD.md** — Full product requirements document with 4-phase roadmap

## Current State (Initial Setup Complete)
- Multi-corpus loading works: Peshitta NT (7,440 verses) + OT (5,929 verses) = 13,369 verses
- 3,329 roots indexed across both corpora
- Corpus filtering works on all API endpoints (?corpus=peshitta_nt|peshitta_ot)
- All routes tested and returning 200
- Bilingual UI (EN/ES) functional
- Initial commit made

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

## Next Steps (from PRD Phase 2)
1. Complete the OT — acquire remaining ~35 books (~17,215 verses) from ETCBC
2. Add Biblical Aramaic corpus (Daniel 2:4b-7:28, Ezra 4:8-6:18)
3. Cross-script root normalization (Hebrew square script → shared Latin root key)
4. Cross-corpus root card (attestation across corpora)
5. Constellation visualization (D3.js, ported from Peshitta app)
6. Proximity search (co-occurring roots, ported from Peshitta app)

## Conventions
- Syriac text uses Unicode (U+0710-U+074F), stored as-is in CSV
- Roots are 2-3 character Syriac strings (e.g., ܫܠܡ for SH-L-M)
- Root keys in cognates.json use Latin transliteration: "sh-l-m"
- Verse references follow "Book Chapter:Verse" format (e.g., "Psalms 1:1")
- Bilingual: every user-facing string has EN and ES variants via i18n.json
