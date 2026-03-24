# Aramaic Root Atlas

A cross-corpus triliteral root explorer spanning ~1,500 years of Aramaic literary history.

Search, browse, and visualize the shared linguistic DNA across the Peshitta, Biblical Aramaic, and Targum Onkelos -- from morphological root extraction to cognate mapping in Hebrew and Arabic.

## Features

- **Multi-corpus search** -- Peshitta NT & OT, Biblical Aramaic (Daniel, Ezra), Targum Onkelos
- **Cross-script root normalization** -- Syriac (&#x0710;-&#x074F;) and Hebrew square script resolve to the same root key
- **Hebrew & Arabic cognates** -- Semantic bridges across Semitic languages with 1,127+ cognate entries
- **Constellation visualization** -- D3.js force-directed graph of root relationships within a passage
- **Proximity search** -- Find co-occurring roots at verse or chapter scope
- **Quadrilingual UI** -- Full interface in English, Spanish, Hebrew, and Arabic with RTL support
- **Four translation tracks** -- WEB (EN), Reina-Valera 1909 (ES), WLC (HE), Van Dyck (AR)
- **Three Syriac font styles** -- Estrangela, Eastern (Madnkhaya), Western (Serto)
- **Dark mode, QR sharing, KWIC search** -- Modern research tools for ancient texts

## Screenshots

<!-- TODO: Add screenshots -->

| Home & Search | Verse Reader | Constellation |
|:---:|:---:|:---:|
| *Search with autocomplete and KWIC results* | *Side-by-side Syriac text with translation tracks* | *D3.js root relationship graph* |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-username/aramaic-root-atlas.git
cd aramaic-root-atlas

# Install dependencies
pip install -r requirements.txt

# Run the app
python3 app.py
```

The app starts on **http://localhost:5001**.

## Corpora

| Corpus | Verses | Words | Source | License |
|--------|-------:|------:|--------|---------|
| Peshitta NT | 7,440 | 101,469 | BFBS Peshitta | Public domain |
| Peshitta OT | 23,072 | 309,889 | ETCBC / Leiden Peshitta Institute | CC-BY-NC |
| Biblical Aramaic | 269 | 4,880 | Sefaria (Westminster Leningrad Codex) | CC-BY-SA |
| Targum Onkelos | 5,846 | 82,684 | Sefaria | CC-BY-SA |
| **Total** | **36,627** | **~498,922** | | |

**5,039 roots** indexed across all corpora. **1,127+ cognate entries** with Hebrew and Arabic cognates and semantic bridges.

## API

The app exposes a JSON API for programmatic access:

| Endpoint | Description |
|----------|-------------|
| `GET /api/stats` | Corpus statistics |
| `GET /api/roots?q=SH-L-M&corpus=peshitta_ot` | Root search with optional corpus filter |
| `GET /api/books?corpus=peshitta_nt` | Book list |
| `GET /api/chapter/<book>/<chapter>?trans=es` | Chapter text with translation |
| `GET /api/search?q=peace&lang=en` | Full-text search across corpora |
| `GET /api/proximity-search?root1=SH-L-M&root2=K-TH-B&scope=verse` | Co-occurring roots |
| `GET /api/passage-constellation?book=Daniel&chapter=2&v_start=4&v_end=10` | Constellation data |

See [docs/API.md](docs/API.md) for full documentation.

## Architecture

```
aramaic-root-atlas/
  aramaic_core/          # Shared linguistic engine (zero Flask dependencies)
    characters.py        #   Syriac/Hebrew/Arabic character maps, transliteration
    affixes.py           #   Syriac prefix/suffix stripping
    affixes_hebrew.py    #   Biblical Aramaic affix stripping (Hebrew script)
    corpus.py            #   AramaicCorpus: multi-corpus CSV loader
    extractor.py         #   RootExtractor: triliteral root extraction + scoring
    cognates.py          #   CognateLookup: Hebrew & Arabic cognate lookup
    glosser.py           #   WordGlosser: compositional word-level glossing
  app.py                 # Flask application (port 5001)
  templates/             # Jinja2 templates (base, index, browse, read, about)
  static/style.css       # CSS with corpus-coded color variables
  data/
    corpora/             # CSV corpus files
    roots/               # cognates.json, known_roots.json, stopwords.json
    translations/        # translations_{en,es,he,ar}.json
  scripts/               # Data pipeline scripts
  docs/                  # PRD, API docs, source attribution
```

## Data Sources & Attribution

- **Peshitta NT** -- BFBS Peshitta (public domain)
- **Peshitta OT** -- ETCBC/peshitta, Leiden Peshitta Institute (CC-BY-NC)
- **Biblical Aramaic** -- Westminster Leningrad Codex via Sefaria API (CC-BY-SA)
- **Targum Onkelos** -- Sefaria API (CC-BY-SA)
- **Translations** -- WEB (EN), Reina-Valera 1909 (ES), WLC (HE), Van Dyck (AR) via [bible.helloao.org](https://bible.helloao.org)

See [docs/SOURCES.md](docs/SOURCES.md) for full attribution details.

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.

## Related

- [Peshitta Root Finder](https://peshitta-roots.onrender.com) -- The predecessor project focused on the Peshitta NT. This atlas extends it into a multi-corpus tool with cross-script normalization and additional corpora.
