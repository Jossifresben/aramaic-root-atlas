# Aramaic Root Atlas -- Data Sources & Attribution

This document lists all data sources, licenses, and third-party resources used by the Aramaic Root Atlas project.

---

## Corpora

### Peshitta New Testament

- **Content:** 22 books, 7,440 verses, 101,469 words
- **Underlying text:** BFBS Peshitta edition (public domain) — the British
  and Foreign Bible Society edition of the Syriac NT. The exact BFBS edition
  in the digitization lineage is the **Pusey-Gwilliam-Mosul** family.
- **Digitization lineage:** [dukhrana.com](https://dukhrana.com) (Stephen
  Silver) and the [SEDRA project](https://sedra.bethmardutho.org)
  (Beth Mardutho Syriac Institute).
- **License:** Public domain (text); attribution requested for the
  digitization providers per their site terms.
- **Script:** Syriac (Unicode block U+0710--U+074F)
- **Corpus ID:** `peshitta_nt`
- **File:** `data/corpora/peshitta_nt.csv`
- **Attribution string:** "Peshitta NT text from the BFBS edition
  (public domain), digitized via dukhrana.com (Stephen Silver) and the
  SEDRA project (Beth Mardutho Syriac Institute)."

### Peshitta Old Testament

- **Content:** 39 books, 23,072 verses, 309,889 words
- **Source:** ETCBC/peshitta project, Leiden Peshitta Institute
- **License:** CC-BY-NC (Creative Commons Attribution-NonCommercial)
- **Script:** Syriac (Unicode block U+0710--U+074F)
- **Corpus ID:** `peshitta_ot`
- **File:** `data/corpora/peshitta_ot.csv`
- **Notes:** The ETCBC (Eep Talstra Centre for Bible and Computer) at the Vrije Universiteit Amsterdam produced this digitized Syriac text based on the Leiden Peshitta Institute critical edition.

### Biblical Aramaic

- **Content:** 269 verses, 4,880 words
- **Passages:** Daniel 2:4b--7:28, Ezra 4:8--6:18, Ezra 7:12--26, Genesis 31:47, Jeremiah 10:11
- **Source:** Sefaria API, based on the Westminster Leningrad Codex (WLC)
- **License:** CC-BY-SA (Creative Commons Attribution-ShareAlike)
- **Script:** Hebrew square script (Unicode block U+0590--U+05FF)
- **Corpus ID:** `biblical_aramaic`
- **File:** `data/corpora/biblical_aramaic.csv`
- **Fetch script:** `scripts/fetch_biblical_aramaic.py`
- **Notes:** The Biblical Aramaic passages are the Aramaic-language sections of the Hebrew Bible. They are written in Hebrew square script, not Syriac. The Atlas performs cross-script root normalization so that shared roots (e.g., Hebrew square script and Syriac) resolve to a common root key.

### Targum Onkelos

- **Content:** 5,846 verses, 82,684 words (Torah / Pentateuch only)
- **Source:** Sefaria API
- **License:** CC-BY-SA (Creative Commons Attribution-ShareAlike)
- **Script:** Syriac (Unicode block U+0710--U+074F)
- **Corpus ID:** `targum_onkelos`
- **File:** `data/corpora/targum_onkelos.csv`
- **Fetch script:** `scripts/fetch_targum_onkelos.py`
- **Notes:** Targum Onkelos is the authoritative Jewish Aramaic translation of the Torah. Dating is debated: traditional dates place it in the 1st-3rd c. CE, but some scholars place the final redaction as late as the 5th c. CE. The text was fetched from the Sefaria API; the underlying critical edition basis is *not* fully documented by Sefaria, and this should be regularized in a future release (target: replace with Sperber's critical edition). Stored in Hebrew square script.

### Ephrem of Nisibis -- Hymns on Nisibis (Carmina Nisibena)

- **Content:** 1,435 verses, 29,477 words. **Important caveat:** this is *one
  collection* of Ephrem the Syrian's surviving works (~5% of the total
  corpus). Other major Ephrem collections (Hymns on Faith, on Heresies, on
  Paradise, on the Nativity, against Julian, on Virginity, the Letters, and
  the Commentaries on Genesis, Exodus, and the Diatessaron) are **not**
  currently indexed.
- **Source:** [Digital Syriac Corpus](https://syriaccorpus.org)
  (`srophe/syriac-corpus` repository), TEI XML.
- **License:** CC-BY 4.0 (Creative Commons Attribution).
- **Script:** Syriac (Unicode block U+0710--U+074F)
- **Corpus ID:** `ephrem_nisibis`
- **File:** `data/corpora/ephrem_nisibis.csv`
- **Fetch script:** `scripts/fetch_ephrem_nisibis.py`
- **Period:** ~4th c. CE (Ephrem ca. 306-373 CE), Patristic Syriac.
- **Notes:** The TEI source includes textual apparatus (variant readings)
  that is *not* preserved in the CSV; only the main reading is loaded. For
  text-critical work, consult the upstream Digital Syriac Corpus directly.

---

## Translation Tracks

All translations were fetched from the **bible.helloao.org** API and are stored as JSON files in `data/translations/`.

### English -- World English Bible (WEB)

- **File:** `data/translations/translations_en.json`
- **License:** Public Domain
- **Notes:** The World English Bible is a modern English translation released into the public domain. It covers both Old and New Testaments.

### Spanish -- Reina-Valera 1909 (RV1909)

- **File:** `data/translations/translations_es.json`
- **License:** Public Domain
- **Notes:** The Reina-Valera 1909 is a classic Spanish Bible translation. The 1909 revision is in the public domain.

### Hebrew -- Westminster Leningrad Codex (WLC)

- **File:** `data/translations/translations_he.json`
- **License:** Public Domain
- **Notes:** The Westminster Leningrad Codex is a digital version of the Leningrad Codex, the oldest complete manuscript of the Hebrew Bible. For NT passages, Hebrew translations from bible.helloao.org are used.

### Arabic -- Van Dyck Translation

- **File:** `data/translations/translations_ar.json`
- **License:** Public Domain
- **Notes:** The Smith & Van Dyck Arabic Bible (1865) is the most widely used Arabic Protestant Bible translation. It is in the public domain.

### Fetch Script

- **Script:** `scripts/fetch_ot_translations.py`
- **API:** bible.helloao.org
- **Notes:** The script fetches EN, ES, HE, and AR translation tracks for all OT books. NT translations were fetched separately during the initial project setup.

---

## Linguistic Data

### Cognates

- **File:** `data/roots/cognates.json`
- **Entries:** 1,584 cognate root entries (1,577 with Hebrew and/or Arabic; 405 with a Greek NT parallel; some with both); 4,599 individual Hebrew cognate words and 4,633 Arabic cognate words across all entries
- **Generation:** Initial set extracted from scholarly sources; 493 additional entries generated via the Claude API (Anthropic) and manually curated.
- **Script:** `scripts/generate_new_cognates.py`
- **Structure:** Each entry contains:
  - Root key (Latin transliteration, e.g., `sh-l-m`)
  - English and Spanish glosses
  - "Root flavor" (sabor de raiz) -- a poetic one-line description of the root's semantic core
  - Hebrew cognates with word, transliteration, and bilingual meanings
  - Arabic cognates with word, transliteration, and bilingual meanings
  - Semantic bridges linking related roots
  - Outlier flags for cognates with divergent meanings

### Peshitta Constellations (companion project)

- **URL:** https://peshitta.onrender.com
- **DOI:** [10.5281/zenodo.19358529](https://doi.org/10.5281/zenodo.19358529)
- **Author:** Jose Fresco Benaim (same author as the Aramaic Root Atlas)
- **Contribution:** Supplied curated root-card seed data used to populate the root family visualizer -- paradigmatic verse citations, sister-root and semantic-bridge relationships, and root-flavor descriptions. The Aramaic Root Atlas extends and generalizes this material across all five corpora.

### Known Roots

- **File:** `data/roots/known_roots.json`
- **Description:** Curated list of verified triliteral roots used to guide the root extraction engine.

### Stopwords

- **File:** `data/roots/stopwords.json`
- **Description:** List of high-frequency function words (particles, prepositions, conjunctions) excluded from root extraction.

### Word Gloss Overrides

- **File:** `data/roots/word_glosses_override.json`
- **Description:** Manual gloss overrides for specific word forms where the automated compositional glossing produces incorrect results.

---

## Internationalization (i18n)

- **File:** `data/i18n.json`
- **Languages:** English (en), Spanish (es), Hebrew (he), Arabic (ar)
- **Content:** 277+ UI string keys per language, plus localized book names for all 61 books across 4 languages.
- **Notes:** Hebrew and Arabic UI strings use right-to-left (RTL) text direction.

---

## Fonts

### Noto Sans Syriac

- **Provider:** Google Fonts
- **License:** SIL Open Font License 1.1 (OFL-1.1)
- **URL:** https://fonts.google.com/noto/specimen/Noto+Sans+Syriac
- **Usage:** The Atlas supports three Syriac script styles via the settings panel:
  - **Estrangela** -- the oldest and most common Syriac script
  - **Eastern (Madnhaya)** -- used in the Church of the East
  - **Western (Serto)** -- used in the Syriac Orthodox Church
- **Notes:** All three styles are provided by the Noto Sans Syriac font family.

---

## JavaScript Libraries

### D3.js

- **Version:** v7 (loaded via CDN)
- **License:** ISC License (functionally equivalent to BSD/MIT)
- **URL:** https://d3js.org
- **Usage:** Powers the passage constellation visualization -- a force-directed graph showing roots, their cognates, and semantic bridges within a selected passage.

---

## API Dependencies

### bible.helloao.org

- **Purpose:** Translation text retrieval
- **Usage:** Fetch scripts call this API to download verse-by-verse translations in EN (WEB), ES (RV1909), HE (WLC), and AR (Van Dyck).
- **Notes:** Used only during data pipeline execution, not at runtime. All translations are stored locally as JSON.

### Sefaria API

- **Purpose:** Biblical Aramaic corpus retrieval
- **URL:** https://www.sefaria.org/api
- **License:** Sefaria's API provides access to the Westminster Leningrad Codex text, licensed CC-BY-SA.
- **Usage:** The fetch script (`scripts/fetch_biblical_aramaic.py`) retrieves the Aramaic portions of Daniel, Ezra, Genesis, and Jeremiah.
- **Notes:** Used only during data pipeline execution, not at runtime. The corpus is stored locally as CSV.

### Claude API (Anthropic)

- **Purpose:** Cognate data generation
- **Usage:** The script `scripts/generate_new_cognates.py` sends uncovered roots to the Claude API to generate Hebrew/Arabic cognate entries with glosses, semantic bridges, and outlier flags.
- **Notes:** Generated entries are manually reviewed before inclusion. Used only during the data pipeline, not at runtime.

---

## Summary Table

| Resource | License | Runtime? |
|----------|---------|----------|
| Peshitta NT text | -- | Yes (loaded from CSV) |
| Peshitta OT text (ETCBC) | CC-BY-NC | Yes (loaded from CSV) |
| Biblical Aramaic (WLC via Sefaria) | CC-BY-SA | Yes (loaded from CSV) |
| Targum Onkelos (Sefaria) | CC-BY-SA | Yes (loaded from CSV) |
| WEB English translation | Public Domain | Yes (loaded from JSON) |
| Reina-Valera 1909 Spanish | Public Domain | Yes (loaded from JSON) |
| Westminster Leningrad Codex Hebrew | Public Domain | Yes (loaded from JSON) |
| Van Dyck Arabic translation | Public Domain | Yes (loaded from JSON) |
| Cognate data | Project-generated | Yes (loaded from JSON) |
| Noto Sans Syriac font | OFL-1.1 | Yes (via Google Fonts CDN) |
| D3.js | ISC | Yes (via CDN) |
| bible.helloao.org API | -- | No (pipeline only) |
| Sefaria API | CC-BY-SA | No (pipeline only) |
| Claude API (Anthropic) | -- | No (pipeline only) |
