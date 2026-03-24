# Product Requirements Document: The Aramaic Root Atlas

**A Cross-Corpus Triliteral Root Explorer for Aramaic Literature**

| Field | Value |
|-------|-------|
| **Author** | Jossif Fresco |
| **Date** | March 23, 2026 |
| **Version** | 1.1 |
| **Status** | Draft |
| **Stakeholders** | Aramaic/Syriac scholars, Semitic linguistics researchers, theological students, digital humanities community |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Product Vision & Goals](#3-product-vision--goals)
4. [Target Users & Personas](#4-target-users--personas)
5. [Competitive Landscape](#5-competitive-landscape)
6. [Product Scope & Phasing](#6-product-scope--phasing)
7. [Detailed Feature Specifications](#7-detailed-feature-specifications)
8. [Technical Architecture](#8-technical-architecture)
9. [Data Strategy](#9-data-strategy)
10. [User Experience & Design](#10-user-experience--design)
11. [API Specification](#11-api-specification)
12. [Non-Functional Requirements](#12-non-functional-requirements)
13. [Dependencies & Constraints](#13-dependencies--constraints)
14. [Risk Assessment](#14-risk-assessment)
15. [Success Metrics & KPIs](#15-success-metrics--kpis)
16. [Go-to-Market Strategy](#16-go-to-market-strategy)
17. [Timeline & Milestones](#17-timeline--milestones)
18. [Open Questions](#18-open-questions)
19. [Appendices](#19-appendices)

---

## 1. Executive Summary

The Aramaic Root Atlas evolves the Peshitta Root Finder — a bilingual (Spanish/English) web application for exploring the Syriac New Testament through triliteral root analysis — into a cross-corpus tool spanning ~1,500 years of Aramaic literary history.

Today, scholars studying Aramaic use fragmented tools: CAL for Talmudic Aramaic, Dukhrana for Syriac, Sefaria for Targum, and print dictionaries for Biblical Aramaic. No tool unifies these corpora at the triliteral root level — the fundamental unit of Semitic meaning.

The Atlas will allow a scholar to trace a single root (e.g., **sh-l-m**, "peace/completion") from its earliest attestation in Daniel (530 BCE) through Targum Onkelos (200 CE), across the Peshitta (2nd-5th c. CE), and into Ephrem's hymns (4th c. CE) — with Hebrew, Arabic, and Greek cognates visible at every layer, and D3.js constellation visualizations showing semantic evolution across centuries.

No such tool exists today. The four-phase rollout (Peshitta OT completion, Biblical Aramaic, Targum Onkelos, Syriac Fathers) leverages 80-95% of existing infrastructure.

**Architecture decision:** The Atlas is a **new, separate application** sharing a core linguistic library (`aramaic-core`) with the existing Peshitta Root Finder. The Peshitta app remains focused and stable; the Atlas is built multi-corpus from day one. Both apps benefit from shared bug fixes and improvements to the core engine.

---

## 2. Problem Statement

### 2.1 The Fragmentation Problem

Aramaic scholarship suffers from tool fragmentation:

- **Peshitta scholars** use Dukhrana.com (text display, basic lexicon) and SEDRA (morphological database) — neither offers root-level analysis, cognate exploration, or semantic visualization.
- **Targum scholars** use Sefaria (text + translation) and CAL (Comprehensive Aramaic Lexicon) — no root-level comparison with Peshitta or other Aramaic dialects.
- **Biblical Aramaic students** rely on BDB and HALOT (print dictionaries) — no interactive digital tools for the Aramaic portions of Daniel/Ezra.
- **Syriac literature scholars** use manual concordances — no automated root-play detection or biblical allusion tracking for patristic texts.
- **Semitic linguists** must mentally bridge between tools per language — no unified cross-dialect root atlas.

### 2.2 The Missing Layer

All these scholars work with the same linguistic building block: the **triliteral consonantal root**. A root like כ-ת-ב / ܟ-ܬ-ܒ (k-t-b, "write") is shared across every Aramaic dialect, yet no tool allows searching, comparing, or visualizing roots across corpora.

### 2.3 The Spanish-Language Gap

The Spanish-speaking theological academy (Latin America, Spain) has essentially zero digital Aramaic tools. Existing tools are English-only. The Peshitta Root Finder's bilingual architecture is unique in the field and ready to extend.

### 2.4 What We've Already Proven

The Peshitta Root Finder (current state) demonstrates that:
- Triliteral root extraction from unvocalized Syriac text works reliably (~436 roots indexed)
- Hebrew and Arabic cognate mapping enriches understanding (3,459 cognate words)
- Semantic constellation visualization reveals patterns invisible in linear text
- Bilingual (ES/EN) UI serves an underserved scholarly audience
- The Claude API pipeline can generate high-quality linguistic analysis at scale

---

## 3. Product Vision & Goals

### 3.1 Vision Statement

> The Aramaic Root Atlas is the first digital tool that lets scholars trace a triliteral root across centuries of Aramaic literature — from Biblical Aramaic through Targum and Peshitta to Syriac patristic writing — with cognate mapping and semantic visualization, in Spanish and English.

### 3.2 Strategic Goals

| # | Goal | Success Indicator |
|---|------|-------------------|
| G1 | **Unify Aramaic corpora at root level** | A single search returns attestations from 4+ corpora |
| G2 | **Enable cross-corpus comparative analysis** | Scholars can compare Targum and Peshitta translations of the same Hebrew verse at root level |
| G3 | **Serve the Spanish-speaking academy** | Full bilingual coverage for all corpora and features |
| G4 | **Become a reference tool for Aramaic digital humanities** | Citations in academic papers, adoption by university programs |
| G5 | **Maintain the Peshitta as anchor corpus** | Peshitta remains the home experience; other corpora enrich it |

### 3.3 Non-Goals

- **Full morphological parser** — We do root analysis, not complete morphological tagging (CAL and SEDRA already do this)
- **Critical text apparatus** — We present one text per corpus, not variant readings
- **Talmudic Aramaic (Phase 1-4)** — Explicitly deferred to Phase 5+ due to corpus size and morphological complexity
- **Machine translation** — We show existing scholarly translations, not AI-generated ones
- **Mobile-native app** — Responsive web is sufficient for the academic audience

---

## 4. Target Users & Personas

### Persona 1: The Peshitta Scholar
**Name:** Dr. Maria Elena Torres
**Role:** Professor of New Testament Studies, Universidad Pontificia de Salamanca
**Language:** Spanish (primary), English (reading)
**Current tools:** Dukhrana, Strong's Concordance, Payne Smith dictionary
**Pain point:** Cannot see how a Syriac root connects to its Aramaic ancestors or Hebrew cognates without switching between 4 reference works
**Atlas value:** Searches a root once, sees it across all corpora with cognates. Spanish UI means she can assign it to students.

### Persona 2: The Comparative Semitist
**Name:** Prof. David Levi
**Role:** Semitic Linguistics, Hebrew University of Jerusalem
**Language:** Hebrew, English, reads Arabic
**Current tools:** CAL, HALOT, Lane's Arabic Lexicon
**Pain point:** Tracing a root across Aramaic dialects requires manual lookup in separate databases with incompatible interfaces
**Atlas value:** One search, four corpora, three cognate languages. The cross-corpus attestation timeline shows diachronic semantic drift visually.

### Persona 3: The Targum Researcher
**Name:** Dr. Sarah Cohen
**Role:** Post-doc, Jewish Studies, University of Oxford
**Language:** English
**Current tools:** Sefaria, CAL, Jastrow dictionary
**Pain point:** Comparing how Targum Onkelos and Peshitta independently translated the same Hebrew verse is a manual, verse-by-verse process
**Atlas value:** The Synoptic Parallel Viewer with root-level alignment automates what currently takes hours of manual comparison.

### Persona 4: The Syriac Literature Scholar
**Name:** Fr. Yuhanna Barsoum
**Role:** Syriac Studies, St. Ephrem Theological Seminary
**Language:** Arabic, Syriac, English
**Current tools:** Printed concordances, critical editions
**Pain point:** Ephrem's root-play (paronomasia) must be identified by close reading — no tool detects it
**Atlas value:** Automated root-play detection highlights patterns across entire hymn cycles.

### Persona 5: The Graduate Student
**Name:** Carlos Mendez
**Role:** MA in Biblical Studies, seminario in Mexico City
**Language:** Spanish
**Current tools:** Strong's in Spanish, occasional Google Translate
**Pain point:** No Aramaic tools exist in Spanish. Feels locked out of a layer of the biblical text.
**Atlas value:** Full Spanish interface for Aramaic root exploration. First encounter with the Semitic root system, made accessible.

---

## 5. Competitive Landscape

### 5.1 Existing Tools

| Tool | Corpora | Root search | Cognates | Visualization | Spanish | Cross-corpus |
|------|---------|-------------|----------|---------------|---------|-------------|
| **CAL** (cal.huc.edu) | Talmudic, Targumic, Syriac, Mandaic | Yes (advanced) | No | No | No | Within CAL corpora only |
| **Dukhrana** (dukhrana.com) | Peshitta NT+OT | Basic lexicon | No | No | No | No |
| **Sefaria** (sefaria.org) | Hebrew Bible, Talmud, Targumim | No (text search only) | No | No | No | Limited (linked texts) |
| **SEDRA** (sedra.bethmardutho.org) | Peshitta | Morphological DB | No | No | No | No |
| **Peshitta Root Finder** (current) | Peshitta NT | Yes (triliteral) | Hebrew, Arabic, Greek | D3.js constellations | Yes (ES/EN) | No (single corpus) |

### 5.2 Our Differentiation

1. **Root-level cross-corpus search** — No tool does this across Aramaic dialects
2. **Visual semantic constellation** — No Aramaic tool has D3.js or any data visualization
3. **Cognate triangulation** — Hebrew + Arabic + Greek at every root, across every corpus
4. **Bilingual (ES/EN)** — Unique in the field
5. **Synoptic parallel viewer** — Targum ↔ Peshitta comparison at root level is unprecedented
6. **Semantic bridge architecture** — Cross-root connections through outlier cognates

### 5.3 Relationship to CAL

CAL (Comprehensive Aramaic Lexicon) is the closest existing tool. Key differences:
- CAL is a **lexicon** (word→definition); the Atlas is a **root explorer** (root→attestations→cognates→visualization)
- CAL has more corpora but no visualization, no cognates, no semantic bridges
- CAL's interface is designed for expert lexicographers; the Atlas is designed for scholars and students
- CAL is English-only
- The Atlas could potentially **link to** CAL entries as an enrichment source (not a replacement)

---

## 6. Product Scope & Phasing

### Phase Overview

| Phase | Corpus | Size | Script | Reuse | Effort | Target |
|-------|--------|------|--------|-------|--------|--------|
| **1** | Peshitta OT (complete remaining 35 books) + extract `aramaic-core` | ~17,215 new verses | Syriac | 95% | 3-4 weeks | Q2 2026 |
| **2** | Biblical Aramaic (Daniel, Ezra) | ~200 verses | Hebrew square | 70% | 4-6 weeks | Q3 2026 |
| **3** | Targum Onkelos | ~5,800 verses | Hebrew square | 65% | 6-8 weeks | Q4 2026 |
| **4** | Syriac Fathers (Ephrem) | ~50-100K words | Syriac | 85% | 8-12 weeks | H1 2027 |

### Phase 1 — Complete Peshitta OT + Extract Shared Library

**Objective:** Full OT coverage in the Peshitta Root Finder app. Extract core linguistic modules into `aramaic-core` shared library to prepare for the Atlas.

**Current OT status (what we already have):**
| Book | Verses |
|------|--------|
| Psalms | 2,461 |
| Proverbs | 915 |
| Isaiah | 1,292 |
| Ezekiel | 1,262 |
| **Total existing** | **5,930** |

**What's missing (~35 books, ~17,215 verses):**
- **Torah (critical — prerequisite for Phase 3):** Genesis, Exodus, Leviticus, Numbers, Deuteronomy
- **Historical:** Joshua, Judges, Ruth, 1-2 Samuel, 1-2 Kings, 1-2 Chronicles, Ezra, Nehemiah, Esther
- **Wisdom:** Job, Song of Songs, Ecclesiastes
- **Prophets:** Jeremiah, Lamentations, Daniel, Hosea, Joel, Amos, Obadiah, Jonah, Micah, Nahum, Habakkuk, Zephaniah, Haggai, Zechariah, Malachi
- **Deuterocanonical (Peshitta tradition):** Wisdom of Solomon, Sirach/Ben Sira, Baruch, Letter of Jeremiah, 1-2 Maccabees

> **Critical dependency:** The Torah must be complete before Phase 3, since the Synoptic Parallel Viewer compares Targum Onkelos against the Peshitta *of the same Torah verses*.

**In scope:**
- Acquire and integrate remaining 35 OT books (~17,215 verses)
- Run root extraction pipeline on new books; discover ~200-350 new roots
- Generate cognates, semantic bridges, and sabor de raiz for new roots
- Add OT translation tracks for new books (EN, ES, HE, AR)
- Add corpus filter to search (NT / OT / All)
- Update browse and reader pages for all OT books
- **Prepare modules for extraction** — ensure `characters.py`, `affixes.py`, `extractor.py`, `corpus.py`, `cognates.py`, `glosser.py` have zero Flask dependencies (already the case — just verify and document)
  - Actual extraction happens at Phase 2 when modules are copied into the new Atlas repo

**Out of scope:**
- Multi-script support (OT is same Syriac Unicode)
- New visualization types
- Atlas app creation (Phase 2)

**Data source:** dukhrana.com / SEDRA (bethmardutho.org) / Leiden Peshitta Institute

**Acceptance criteria:**
- [ ] All 39 OT books loadable and searchable (existing 4 + new 35)
- [ ] Root extraction covers full OT with <5% false positive rate
- [ ] New roots have Hebrew + Arabic cognates generated
- [ ] Corpus filter works on search, browse, and reader
- [ ] OT translations display correctly in all tracks
- [ ] Core modules verified Flask-free (ready for copy into Atlas repo at Phase 2)

---

### Phase 2 — Biblical Aramaic

**Objective:** Add the Aramaic portions of the Hebrew Bible as the first non-Syriac corpus, establishing the multi-corpus architecture.

**In scope:**
- Daniel 2:4b-7:28, Ezra 4:8-6:18 + 7:12-26, Genesis 31:47, Jeremiah 10:11
- Hebrew square-script display and transliteration
- Cross-script root normalization (Hebrew script → same Latin root key as Syriac)
- Biblical Aramaic morphological analysis (affixes.py extensions)
- Multi-corpus data model with `corpus_id`
- Cross-corpus root card (attestation across corpora)
- Corpus selector on all search endpoints

**Out of scope:**
- Synoptic parallel viewer (Phase 3)
- Full BA vocalization analysis
- BA-specific semantic bridges (reuse Peshitta bridges where roots overlap)

**Data source:** Sefaria API (CC-BY-SA, Westminster Leningrad Codex)

**Acceptance criteria:**
- [ ] Biblical Aramaic text renders correctly in Hebrew square script
- [ ] Root search returns BA attestations alongside Peshitta results
- [ ] Root normalization: BA כתב and Peshitta ܟܬܒ resolve to same root `k-th-b`
- [ ] Cross-corpus root card shows attestation count per corpus
- [ ] BA reader page functional with verse navigation
- [ ] 70%+ of BA roots successfully cross-referenced with Peshitta roots

---

### Phase 3 — Targum Onkelos

**Objective:** Add the authoritative Aramaic translation of the Torah, enabling unprecedented three-way comparison: Hebrew source → Targum Aramaic → Peshitta Syriac.

**In scope:**
- Full Targum Onkelos (Pentateuch, ~5,800 verses, ~65,000 words)
- Targum-specific morphological extensions
- **Synoptic Parallel Viewer** — side-by-side Hebrew MT + Targum + Peshitta OT for any Torah verse, with root-level color alignment
- **Translation Technique Analysis** — identify where Targum and Peshitta agree/diverge in translating the same Hebrew source
- Verse alignment system (Hebrew ref → Targum verse → Peshitta verse)
- Three-corpus overlay on constellation viewer

**Out of scope:**
- Targum Pseudo-Jonathan, Targum Neofiti (later targumim — potential Phase 5)
- Full halakhic commentary analysis
- Automated translation technique classification (manual annotation initially)

**Data source:** Sefaria API (CC-BY-SA)

**Acceptance criteria:**
- [ ] Targum Onkelos text renders in Hebrew square script, all 5 books
- [ ] Synoptic Parallel Viewer displays 3 columns for any Torah verse
- [ ] Root-level color alignment works across Hebrew, Targum, and Peshitta columns
- [ ] Click any word in any column → root lookup across all corpora
- [ ] Translation technique divergences documented for 100+ notable verses
- [ ] Constellation viewer supports three-corpus overlay with color coding

---

### Phase 4 — Syriac Patristic Literature

**Objective:** Add selected works of Ephrem the Syrian, extending the app beyond biblical text into literary Syriac.

**In scope:**
- Ephrem's *Hymns on Paradise*, *Hymns on Faith*, *Commentary on the Diatessaron* (selected works, ~50-100K words)
- **Non-verse indexing system** — flexible reference: `work.section.paragraph.line` or `hymn.stanza.line`
- **Root Wordplay Detector** — automatic identification of paronomasia (root-punning) in adjacent lines
- **Biblical Allusion Tracker** — link patristic root usage back to Peshitta biblical verses
- Literary register weighting in root scoring

**Out of scope:**
- Other Syriac Fathers (Aphrahat, Jacob of Serugh) — future expansion
- Full critical apparatus or manuscript variants
- Liturgical text integration (Maronite/Syriac Orthodox)

**Data source:** bethmardutho.org (SEDRA), syriaca.org, archive.org (public domain critical editions)

**Acceptance criteria:**
- [ ] Non-verse reference system works for hymn/stanza/line structure
- [ ] Root-play detector identifies paronomasia with >80% precision in tested hymns
- [ ] Biblical allusion tracker links 50%+ of Ephrem roots to Peshitta verses
- [ ] Patristic reader displays Ephrem texts with root highlighting
- [ ] Constellation viewer includes patristic attestations

---

## 7. Detailed Feature Specifications

### 7.1 Cross-Corpus Root Search (Phase 2+)

**Description:** User enters a root (any script or Latin transliteration); results aggregate attestations from all loaded corpora.

**User flow:**
1. User types `sh-l-m` (or ܫܠܡ or שלם)
2. System normalizes to shared root key `sh-l-m`
3. Results panel shows:
   - Root card with gloss (ES/EN)
   - Attestation summary: "Found in 4 corpora: BA (3x), Targum (12x), Peshitta NT (47x), Peshitta OT (89x)"
   - Expandable per-corpus verse list
   - Hebrew, Arabic, Greek cognates
   - Semantic bridges to related roots
4. User can filter by corpus or click through to any verse

**Technical notes:**
- Root normalization: `normalize_root()` in `characters.py` converts any script to shared Latin key
- Query parameter: `/api/roots?q=sh-l-m&corpus=all|peshitta_nt|peshitta_ot|biblical_aramaic|targum_onkelos`
- Response includes `corpus_id` per match for frontend grouping

### 7.2 Cross-Corpus Attestation Timeline (Phase 2+)

**Description:** Visual timeline on root cards showing when/where a root appears across history.

**Display:**
```
────────────────────────────────────────────────────────────►
530 BCE           200 CE          200-400 CE         4th c. CE
Biblical Aramaic  Targum Onkelos  Peshitta           Ephrem
שְׁלָם (3x)        שלם (12x)       ܫܠܡ (136x)         ܫܠܡ (23x)
Dan 4:1           Gen 43:27       Matt 10:13         Hymns Par. III.4
```

**Implementation:** SVG or CSS timeline, data from `/api/cross-corpus/<root_key>`

### 7.3 Synoptic Parallel Viewer (Phase 3)

**Description:** Three-column view of Torah verses showing Hebrew source, Targum translation, and Peshitta translation with root-level alignment.

**Layout:**
```
┌──────────────────┬──────────────────┬──────────────────┐
│  Hebrew (MT)     │  Targum Onkelos  │  Peshitta        │
│  Right-to-left   │  Right-to-left   │  Right-to-left   │
├──────────────────┼──────────────────┼──────────────────┤
│  בְּרֵאשִׁית בָּרָא  │  בקדמין ברא      │  ܒܪܫܝܬ ܒܪܐ       │
│  אֱלֹהִים         │  יי               │  ܐܠܗܐ            │
│  אֵת הַשָּׁמַיִם    │  ית שמיא          │  ܫܡܝܐ            │
│  וְאֵת הָאָרֶץ     │  וית ארעא         │  ܘܐܪܥܐ           │
└──────────────────┴──────────────────┴──────────────────┘
       ↑ shared root: b-r-ʾ (create) highlighted in all three columns
```

**Interactions:**
- Click any word → root popup showing cross-corpus attestation
- Hover root → highlight same root in all three columns (color-coded)
- Navigate: prev/next verse, jump to chapter
- Translation technique badge: "Literal" / "Paraphrase" / "Theological expansion" / "Anti-anthropomorphism"

**Technical notes:**
- Verse alignment: Hebrew refs map 1:1 to Targum (same versification). Peshitta OT versification may differ slightly — build alignment table.
- Root alignment across columns is approximate (word order differs); highlight by root presence, not positional alignment.

### 7.4 Translation Technique Analysis (Phase 3)

**Description:** For each Torah verse, identify how Targum and Peshitta independently translated the Hebrew source, flagging notable patterns.

**Categories:**
| Technique | Description | Example |
|-----------|-------------|---------|
| Literal | Word-for-word root match | Hebrew ברא → Targum ברא → Peshitta ܒܪܐ (all b-r-ʾ) |
| Synonym substitution | Different root, similar meaning | Hebrew שמר → Targum נטר → Peshitta ܢܛܪ (both chose n-ṭ-r instead of sh-m-r) |
| Paraphrase | Restructured for clarity | Hebrew "hand of God" → Targum "might before the Lord" |
| Anti-anthropomorphism | Avoids human attributes for God | Hebrew "God rested" → Targum "there was rest before God" |
| Theological expansion | Adds interpretive content | Hebrew "seed" → Targum "the King Messiah" |
| Agreement | Targum and Peshitta match each other against Hebrew | Both chose the same non-literal rendering independently |
| Divergence | Targum and Peshitta differ from each other | Different root choices for the same Hebrew word |

**Implementation:**
- Phase 3a: Manual annotation of 100+ notable verses (stored as JSON)
- Phase 3b: Claude-assisted classification of remaining verses (stretch goal)
- Display as badges/tags on Synoptic Parallel Viewer

### 7.5 Root Wordplay Detector (Phase 4)

**Description:** Automatically identify paronomasia (root-punning) in Ephrem's texts.

**Detection rules:**
1. **Same root, adjacent lines:** Root X appears in line N and line N+1 or N+2
2. **Near-homophonous roots:** Roots differing by one consonant in adjacent lines (e.g., sh-l-m and sh-l-ḥ)
3. **Root cluster:** 3+ distinct roots sharing a consonant appear in a single stanza
4. **Antonymic root-play:** Semantically opposed roots in adjacent lines (requires semantic field data from cognates.json)

**Output:** Highlighted spans in the reader with annotation: "Root-play: sh-l-m (peace) / sh-l-ḥ (send) — Ephrem plays on the proximity of peace and mission."

### 7.6 Biblical Allusion Tracker (Phase 4)

**Description:** When Ephrem uses a root attested in the Peshitta, link back to the most likely biblical source.

**Logic:**
1. Extract roots from Ephrem text
2. For each root, find Peshitta NT/OT verses where the root is prominent (high TF-IDF or low total frequency)
3. Rank candidate allusions by: thematic relevance (from cognate semantic fields), proximity to other allusion-linked roots in the same stanza, known Ephrem citation patterns
4. Display as footnote-style links: "cf. Matt 5:9 (ܫܠܡ — peacemakers)"

---

## 8. Technical Architecture

### 8.1 System Overview — Two Repos, Shared Core

**Architecture decision:** Two Git repositories. The Atlas repo owns the shared linguistic core (`aramaic_core/`). The Peshitta repo stays as-is and consumes the core as a Git dependency.

**Why this approach:**
- The Peshitta app is already deployed and stable — don't restructure it
- The Atlas is new — it can own the shared code from birth
- Avoids three-repo overhead or monorepo complexity
- If the Atlas never ships, the Peshitta app is unaffected
- For a solo developer, pragmatism beats purity

#### Repo 1: `peshitta-root-finder` (existing, unchanged structure)

```
github.com/jfresco/peshitta-root-finder     ← EXISTING REPO
├── app.py
├── peshitta_roots/
│   ├── characters.py      ← keeps working as-is during Phase 1
│   ├── corpus.py           stays local until core stabilizes
│   ├── affixes.py
│   ├── extractor.py
│   ├── cognates.py
│   └── glosser.py
├── templates/
├── static/
├── data/
│   ├── syriac_nt_traditional22_unicode.csv
│   ├── syriac_ot_selected_unicode.csv  → expanded to full OT (Phase 1)
│   ├── cognates.json
│   └── translations*.json
└── requirements.txt
```

Phase 1: The Peshitta app keeps its own copy of the modules. No dependency on the Atlas repo yet. OT completion happens here.

Phase 2+: Once `aramaic_core` is stable in the Atlas repo, the Peshitta app *optionally* switches to importing it:
```
# requirements.txt (Phase 2+ optional migration)
aramaic-core @ git+https://github.com/jfresco/aramaic-root-atlas.git#subdirectory=aramaic_core
```
Or — simpler — just cherry-pick bug fixes between repos when needed. Formalize the dependency only when both apps are actively diverging.

#### Repo 2: `aramaic-root-atlas` (new repo, Phase 2+)

```
github.com/jfresco/aramaic-root-atlas       ← NEW REPO
├── aramaic_core/                            ← SHARED PACKAGE (lives here)
│   ├── __init__.py
│   ├── characters.py                        # + normalize_root()
│   ├── corpus.py                            # + multi-corpus, corpus_id
│   ├── affixes.py                           # + BA/Targum morphology
│   ├── extractor.py                         # + cross-corpus scoring
│   ├── cognates.py                          # + cross-corpus attestation
│   ├── glosser.py                           # + multi-dialect glossing
│   └── alignment.py                         # NEW (Phase 3)
├── app.py                                   ← Atlas Flask app
├── templates/
│   ├── base.html
│   ├── index.html                           # multi-corpus search
│   ├── read.html                            # multi-corpus reader
│   ├── browse.html                          # cross-corpus root browser
│   ├── visualize.html                       # constellation + corpus colors
│   └── parallel.html                        # Synoptic Parallel Viewer (Phase 3)
├── static/
│   ├── style.css                            # new palette (corpus-coded colors)
│   └── global.js
├── data/
│   ├── corpora/
│   │   ├── peshitta_nt.csv                  # copied from Peshitta repo
│   │   ├── peshitta_ot.csv                  # copied from Peshitta repo
│   │   ├── biblical_aramaic.csv             # Phase 2
│   │   ├── targum_onkelos.csv               # Phase 3
│   │   └── ephrem_hymns.csv                 # Phase 4
│   ├── roots/
│   │   ├── cognates.json                    # extended (all corpora)
│   │   ├── known_roots.json                 # extended (all corpora)
│   │   └── cross_corpus_index.json          # root → {corpus: [refs]}
│   ├── translations/
│   ├── alignment/
│   │   └── torah_alignment.json             # Phase 3
│   └── annotations/
│       ├── translation_techniques.json      # Phase 3
│       └── root_play_patterns.json          # Phase 4
├── scripts/
│   ├── fetch_ba_text.py                     # Sefaria API
│   ├── fetch_targum.py                      # Sefaria API
│   └── generate_cross_corpus_index.py
└── pyproject.toml
```

#### How the two repos relate over time

```
Phase 1 (Q2 2026):
  peshitta-root-finder: complete OT, all work happens here
  aramaic-root-atlas:   does not exist yet

Phase 2 (Q3 2026):
  peshitta-root-finder: stable, no changes
  aramaic-root-atlas:   created ← copy modules from Peshitta into aramaic_core/
                         extend with multi-corpus, BA support
                         Peshitta CSV data copied into data/corpora/

Phase 3 (Q4 2026):
  peshitta-root-finder: stable (cherry-pick any core bug fixes if needed)
  aramaic-root-atlas:   add Targum, Synoptic Viewer, alignment engine
                         optionally: Peshitta app migrates to import aramaic_core

Phase 4 (H1 2027):
  peshitta-root-finder: optionally imports aramaic_core as Git dependency
  aramaic-root-atlas:   add Ephrem, root-play detection, allusion tracker
```

#### Key principle: pragmatic sharing, not premature abstraction

- Phase 1: **no shared code yet** — just complete the OT in the Peshitta app
- Phase 2: **copy + extend** — fork the modules into the Atlas repo, evolve them for multi-corpus
- Phase 3+: **formalize if needed** — if both apps are actively maintained, make `aramaic_core` a proper installable package and point the Peshitta app at it
- If only one app survives, the code lives where it's used — no orphaned packages

**Why two apps instead of one:**
1. **Peshitta stays clean** — no corpus selectors, synoptic viewers, or BA morphology it doesn't need
2. **Atlas is multi-corpus by design** — no retrofit, no backward compatibility hacks
3. **Independent deployment** — Peshitta can stay on current hosting; Atlas launches when ready
4. **Different audiences** — biblical scholars → Peshitta; comparative Semitists → Atlas
5. **Risk isolation** — Atlas experiments don't regress the stable Peshitta app

### 8.2 Shared Root Normalization

The architectural keystone: all Aramaic dialects share the same 22-consonant root system. Different scripts represent the same sounds.

| Dialect | Script | "write" | Normalized key |
|---------|--------|---------|----------------|
| Biblical Aramaic | כתב (Hebrew square) | k-t-b | `k-th-b` |
| Targum Onkelos | כתב (Hebrew square) | k-t-b | `k-th-b` |
| Peshitta | ܟܬܒ (Syriac) | k-t-b | `k-th-b` |
| Ephrem | ܟܬܒ (Syriac) | k-t-b | `k-th-b` |

**Implementation:**
```python
# characters.py — new function
def normalize_root(consonants: str, source_script: str) -> str:
    """Normalize consonants from any Aramaic script to shared Latin root key."""
    if source_script == 'syriac':
        return transliterate_syriac(consonants)
    elif source_script == 'hebrew':
        return transliterate_hebrew_aramaic(consonants)
    # Both produce identical key: 'k-th-b'
```

Consonant correspondence table (22 letters, 1:1 between scripts):

| # | Syriac | Hebrew | Latin | IPA |
|---|--------|--------|-------|-----|
| 1 | ܐ (Alap) | א (Alef) | ʾ | ʔ |
| 2 | ܒ (Beth) | ב (Bet) | b | b/v |
| 3 | ܓ (Gamal) | ג (Gimel) | g | g/ɣ |
| 4 | ܕ (Dalath) | ד (Dalet) | d | d/ð |
| 5 | ܗ (He) | ה (He) | h | h |
| 6 | ܘ (Waw) | ו (Vav) | w | w |
| 7 | ܙ (Zayn) | ז (Zayin) | z | z |
| 8 | ܚ (Heth) | ח (Het) | ḥ | ħ |
| 9 | ܛ (Teth) | ט (Tet) | ṭ | tˤ |
| 10 | ܝ (Yodh) | י (Yod) | y | j |
| 11 | ܟ (Kaph) | כ (Kaf) | k | k/x |
| 12 | ܠ (Lamadh) | ל (Lamed) | l | l |
| 13 | ܡ (Mim) | מ (Mem) | m | m |
| 14 | ܢ (Nun) | נ (Nun) | n | n |
| 15 | ܣ (Semkath) | ס (Samekh) | s | s |
| 16 | ܥ (ʿE) | ע (Ayin) | ʿ | ʕ |
| 17 | ܦ (Pe) | פ (Pe) | p | p/f |
| 18 | ܨ (Tsade) | צ (Tsade) | ṣ | sˤ |
| 19 | ܩ (Qoph) | ק (Qof) | q | q |
| 20 | ܪ (Resh) | ר (Resh) | r | r |
| 21 | ܫ (Shin) | ש (Shin) | sh | ʃ |
| 22 | ܬ (Taw) | ת (Tav) | th | t/θ |

### 8.3 Multi-Corpus Data Model

**Repository structure:** See Section 8.1 for full directory trees of both repos. Key points:

- `peshitta-root-finder/` keeps its current structure, modules stay local
- `aramaic-root-atlas/aramaic_core/` owns the shared linguistic engine
- Peshitta CSV data is **copied** into the Atlas `data/corpora/` directory (not symlinked — keeps repos independent)
- Each repo has its own `data/`, `templates/`, `static/`, and `app.py`

**CSV schema (universal across corpora):**
```csv
corpus_id,book_order,book,chapter,verse,reference,text,script
peshitta_nt,1,Matthew,1,1,Matthew 1:1,ܟܬܒܐ ܕܝܠܝܕܘܬܐ...,syriac
biblical_aramaic,27,Daniel,2,4,Daniel 2:4,מַלְכָּא לְעָלְמִין...,hebrew
targum_onkelos,1,Genesis,1,1,Genesis 1:1,בקדמין ברא...,hebrew
```

### 8.4 Module Changes by Phase

**Phase 1 (Peshitta OT):**
| Module | Change | Complexity |
|--------|--------|-----------|
| `corpus.py` | Load second CSV; add `corpus_id` field | Low |
| `app.py` | Add `corpus` query param to search routes | Low |
| Templates | Add OT books to reader/browse dropdowns | Low |
| `generate_new_cognates.py` | Run on OT-only roots | Low |

**Phase 2 (Biblical Aramaic):**
| Module | Change | Complexity |
|--------|--------|-----------|
| `characters.py` | Add `normalize_root()`, `transliterate_hebrew_aramaic()` | Medium |
| `corpus.py` | Multi-corpus loading, shared root index | Medium |
| `affixes.py` | BA pronominal suffixes, haphel/hitpeel prefixes | Medium |
| `extractor.py` | `corpus_id` on `RootMatch`, cross-corpus scoring | Medium |
| `app.py` | `/api/cross-corpus/<root_key>` endpoint | Low |
| Templates | Cross-corpus root card, BA reader, attestation timeline | Medium |

**Phase 3 (Targum Onkelos):**
| Module | Change | Complexity |
|--------|--------|-----------|
| `alignment.py` (NEW) | Verse alignment Hebrew↔Targum↔Peshitta | High |
| `affixes.py` | Targum-specific definite articles, suffixes | Low |
| `app.py` | `/api/parallel/<ref>`, `/api/translation-technique/<ref>` | Medium |
| Templates | Synoptic Parallel Viewer (new template) | High |
| `cognates.json` | Add Targum attestation layer | Low |

**Phase 4 (Ephrem):**
| Module | Change | Complexity |
|--------|--------|-----------|
| `corpus.py` | Non-verse reference system (`work.section.line`) | High |
| `extractor.py` | Register weighting, root-play detection | High |
| `app.py` | `/api/root-play/`, `/api/biblical-allusion/` | Medium |
| Templates | Patristic reader, root-play highlights | Medium |

---

## 9. Data Strategy

### 9.1 Data Sources

| Corpus | Primary source | License | Format | Acquisition method |
|--------|---------------|---------|--------|-------------------|
| Peshitta OT | dukhrana.com | Free academic | HTML | Web scrape + manual validation |
| Peshitta OT (alt) | SEDRA (bethmardutho.org) | Academic | DB export | Contact Beth Mardutho |
| Peshitta OT (alt2) | ETCBC/Leiden | Academic | ETCBC format | Python API (text-fabric) |
| Biblical Aramaic | Sefaria | CC-BY-SA | JSON | REST API (`api.sefaria.org`) |
| Biblical Aramaic (alt) | BHSA/ETCBC | CC-BY | Text-Fabric | Python API |
| Targum Onkelos | Sefaria | CC-BY-SA | JSON | REST API |
| Targum Onkelos (alt) | CAL (HUC) | Academic | Web | Limited scraping (verify ToS) |
| Ephrem | bethmardutho.org | Varies | SEDRA/TEI | Contact institution |
| Ephrem (alt) | archive.org | Public domain | PDF → OCR | Manual + Claude OCR |

### 9.2 Data Processing Pipeline

For each new corpus:

```
1. Acquire raw text
   ↓
2. Normalize encoding (→ Unicode, strip formatting)
   ↓
3. Convert to standard CSV schema (corpus_id, book, chapter, verse, ref, text, script)
   ↓
4. Validate: character range checks, verse count checks, spot-check vs. print edition
   ↓
5. Run root extraction (extractor.py)
   ↓
6. Cross-reference extracted roots with existing root index
   ↓
7. Identify new roots (not in any existing corpus)
   ↓
8. Generate cognates for new roots (generate_new_cognates.py via Claude API)
   ↓
9. Generate semantic bridges for new outlier cognates
   ↓
10. Run quality audit (deep_hebrew_audit.py pattern)
   ↓
11. Build cross-corpus index (cross_corpus_index.json)
   ↓
12. Generate/extend translation tracks
```

### 9.3 Licensing & Attribution

| License | Corpora | Requirements |
|---------|---------|-------------|
| CC-BY-SA | Sefaria texts (BA, Targum) | Attribution + share-alike |
| Academic use | SEDRA, Dukhrana | Non-commercial, cite source |
| Public domain | Archive.org editions | None |
| Custom | ETCBC/Leiden | Per-agreement |

**Attribution strategy:** Dedicated "Sources & Credits" page listing all data providers. Each corpus display includes source attribution in footer.

---

## 10. User Experience & Design

### 10.1 Design Principles

1. **Peshitta-first:** The Peshitta remains the home experience. Other corpora enrich it, not compete with it.
2. **Progressive disclosure:** Cross-corpus features are discoverable but not overwhelming. A first-time user sees a simple root search; power users unlock the synoptic viewer and constellation overlays.
3. **Consistent visual language:** Corpus identity through color-coding:
   - Peshitta: Olive/stone (current palette)
   - Biblical Aramaic: Deep blue (ancient/authoritative)
   - Targum: Amber/gold (rabbinic tradition)
   - Ephrem: Purple/violet (liturgical/literary)
4. **Script respect:** Each corpus renders in its native script. No forced transliteration unless requested.
5. **Bilingual always:** Every new feature, label, and annotation available in ES and EN.

### 10.2 Navigation Changes

**Current:** Search | Browse | Read | Constellation | Methodology | About | Help

**Phase 3+:** Search | Browse | Read | Parallel | Constellation | Methodology | About | Help

The "Parallel" nav item (Phase 3) leads to the Synoptic Parallel Viewer. Other corpora integrate into existing pages via corpus selectors.

### 10.3 Key Screen Wireframes

**Cross-corpus root card (Phase 2+):**
```
┌─────────────────────────────────────────────────┐
│  ܫܠܡ  sh-l-m  "peace, completion"               │
│  ──────────────────────────────────────────      │
│  📖 Attestations                                 │
│  ┌──────────────────────────────────────────┐   │
│  │ Biblical Aramaic  ███░░░░░░░░  3 verses  │   │
│  │ Targum Onkelos    █████░░░░░  12 verses  │   │
│  │ Peshitta NT       ████████░░  47 verses  │   │
│  │ Peshitta OT       ██████████  89 verses  │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  🔗 Cognates                                     │
│  Hebrew: שָׁלוֹם shalom — Arabic: سلام salam      │
│  Greek: εἰρήνη eirene                            │
│                                                  │
│  🌿 Semantic bridges                             │
│  → sh-l-ḥ (send) via "mission of peace"         │
│  → g-m-r (complete) via "wholeness"              │
│                                                  │
│  [View constellation] [View all verses]          │
└─────────────────────────────────────────────────┘
```

---

## 11. API Specification

### 11.1 New Endpoints

**Phase 1:**
```
GET /api/roots?q={root}&corpus={nt|ot|all}
    Add corpus filter to existing endpoint.
    Response: existing format + corpus_id per match.

GET /read?corpus={ot}&book={book}&ch={chapter}
    OT reader pages.
```

**Phase 2:**
```
GET /api/cross-corpus/{root_key}
    Returns root data aggregated across all corpora.
    Response:
    {
      "root_key": "sh-l-m",
      "root_syriac": "ܫܠܡ",
      "root_hebrew": "שלם",
      "gloss_es": "paz, completar",
      "gloss_en": "peace, complete",
      "corpora": {
        "biblical_aramaic": {"count": 3, "verses": [...]},
        "targum_onkelos": {"count": 12, "verses": [...]},
        "peshitta_nt": {"count": 47, "verses": [...]},
        "peshitta_ot": {"count": 89, "verses": [...]}
      },
      "cognates": { "hebrew": [...], "arabic": [...], "greek": {...} },
      "semantic_bridges": [...]
    }
```

**Phase 3:**
```
GET /api/parallel/{reference}
    Returns synoptic parallel data for a Torah verse.
    Response:
    {
      "reference": "Genesis 1:1",
      "hebrew_mt": {"text": "בְּרֵאשִׁית בָּרָא אֱלֹהִים...", "words": [...]},
      "targum_onkelos": {"text": "בקדמין ברא יי...", "words": [...]},
      "peshitta": {"text": "ܒܪܫܝܬ ܒܪܐ ܐܠܗܐ...", "words": [...]},
      "root_alignments": [
        {"root": "b-r-ʾ", "hebrew_word": "ברא", "targum_word": "ברא", "peshitta_word": "ܒܪܐ"}
      ],
      "technique_annotations": [
        {"type": "literal", "scope": "full_verse", "note_es": "...", "note_en": "..."}
      ]
    }

GET /api/translation-technique/{reference}
    Returns analysis of how Targum and Peshitta rendered a Hebrew verse.
```

**Phase 4:**
```
GET /api/root-play/{work}/{section}
    Returns detected paronomasia in a section of Ephrem.

GET /api/biblical-allusion/{work}/{reference}
    Returns probable Peshitta allusion sources for an Ephrem passage.
```

---

## 12. Non-Functional Requirements

### 12.1 Performance

| Metric | Target | Current |
|--------|--------|---------|
| Root search response time | <500ms | ~200ms (NT only) |
| Cross-corpus search response | <1s | N/A |
| Parallel viewer load | <2s | N/A |
| Initial app load (cold) | <5s | ~3s |
| Data file total size | <50MB | ~15MB |

**Strategy:** Lazy-load corpora on first access. Pre-compute cross-corpus root index at startup. Cache per-corpus root indexes.

### 12.2 Scalability

- Phase 1-3: ~36,000 total verses — well within single-process Flask capacity
- Phase 4: ~50-100K additional words — still manageable
- If growth continues (Talmudic Aramaic in Phase 5+): consider SQLite migration for word index

### 12.3 Accessibility

- WCAG 2.1 AA compliance (current standard maintained)
- RTL text support for Syriac, Hebrew, and Arabic (already implemented)
- Screen reader support for D3.js visualizations (add aria labels to nodes)
- High-contrast mode for constellation viewer

### 12.4 Internationalization

- ES/EN bilingual for all UI text, annotations, and glosses
- All new i18n keys added to `i18n.json` in both languages simultaneously
- HE/AR script display support maintained for transliteration tables

### 12.5 Browser Support

- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Mobile responsive (tablets for academic use; phone as reference)

---

## 13. Dependencies & Constraints

### 13.1 External Dependencies

| Dependency | Phase | Risk | Mitigation |
|-----------|-------|------|------------|
| Sefaria API availability | 2, 3 | Low (stable API) | Cache responses; offline fallback data |
| Dukhrana/SEDRA data access | 1 | Medium | Multiple alternative sources identified |
| bethmardutho.org cooperation | 4 | Medium-High | Start outreach early; fallback to archive.org public domain editions |
| Claude API for cognate generation | 1-4 | Low | Existing pipeline proven; budget ~$50-100 per phase |

### 13.2 Technical Constraints

- **Single-process Flask:** Sufficient for Phases 1-4 corpus sizes. No database migration needed.
- **Client-side rendering:** D3.js constellation may slow on very large root networks (>500 nodes). Implement node limit with "show more" pagination.
- **Unicode rendering:** Some browsers render Syriac vowel diacritics inconsistently. We already work with consonantal text only, which avoids this.

### 13.3 Licensing Constraints

- Sefaria data (CC-BY-SA) requires attribution and share-alike. Any derived data must also be CC-BY-SA.
- If using ETCBC data, academic-only license may restrict commercial use. Clarify terms.
- The Atlas itself should be open-source (matching current Peshitta Root Finder approach).

---

## 14. Risk Assessment

| # | Risk | Likelihood | Impact | Mitigation | Owner |
|---|------|-----------|--------|------------|-------|
| R1 | Peshitta OT text quality varies by source | Medium | Medium | Cross-reference SEDRA + Dukhrana + Leiden; spot-check against print editions | Jossif |
| R2 | Biblical Aramaic corpus too small to be independently compelling | Low | Low | Compensate with rich cross-corpus linking; frame as "the ancestral roots" |Jossif |
| R3 | Targum morphology harder than expected | Medium | Medium | Start with root-only analysis (no full morphological parse); iterate | Jossif |
| R4 | Ephrem texts not well-digitized | High | Medium | Start with Commentary on Diatessaron (best digitized); contact bethmardutho early | Jossif |
| R5 | Scope creep into Talmudic Aramaic | Medium | High | Explicitly defer JBA to Phase 5+; document boundary in PRD | Jossif |
| R6 | Performance degradation with larger corpus | Low | Medium | Lazy loading already in place; add corpus-specific caching; profile at each phase | Jossif |
| R7 | Character encoding inconsistencies across sources | Medium | Medium | Build validation script normalizing all input to standard Unicode ranges | Jossif |
| R8 | Root normalization edge cases (matres lectionis, defective spelling) | Medium | High | Build comprehensive test suite for cross-script normalization; manual review of mismatches | Jossif |
| R9 | Academic community skepticism toward AI-generated cognate data | Medium | High | Cite authoritative lexicons (Payne, BDB, Lane) as primary sources; AI as synthesis only; transparent methodology page | Jossif |
| R10 | Single developer bandwidth | High | High | Phase strictly; accept longer timelines; consider academic collaborators | Jossif |

---

## 15. Success Metrics & KPIs

### 15.1 Phase-Level Metrics

| Phase | Metric | Target |
|-------|--------|--------|
| 1 | Total roots indexed | 600+ (up from ~436) |
| 1 | OT verses searchable | 23,000+ |
| 1 | New cognate entries generated | 200+ |
| 2 | Cross-corpus root matches (BA↔Peshitta) | 70%+ of BA roots found in Peshitta |
| 2 | BA unique roots with cognates | 50+ |
| 3 | Torah verses with synoptic parallel | All 5,845 |
| 3 | Translation technique annotations | 100+ notable verses |
| 3 | Root alignment accuracy in parallel viewer | >90% correct |
| 4 | Root-play instances detected in Ephrem | 200+ |
| 4 | Biblical allusion links generated | 500+ |

### 15.2 Product-Level KPIs

| KPI | Target | Timeframe |
|-----|--------|-----------|
| Monthly active users | 500+ | 6 months after Phase 3 |
| Academic citations | 5+ papers citing the tool | 12 months after Phase 3 |
| University course adoptions | 3+ programs | 12 months after Phase 3 |
| Root searches per month | 10,000+ | 6 months after Phase 3 |
| User retention (monthly return) | 40%+ | Ongoing |
| GitHub stars (if open-sourced) | 200+ | 12 months |

### 15.3 Quality Gates

Each phase must pass before proceeding to the next:

**Phase 1 gate:**
- [ ] All OT books load without errors
- [ ] Root extraction false positive rate <5%
- [ ] Cognates reviewed against BDB/Payne for 50 sample roots

**Phase 2 gate:**
- [ ] Cross-script normalization passes 100% of test suite
- [ ] BA reader renders Hebrew square script correctly across target browsers
- [ ] 3 sample scholars validate cross-corpus root card accuracy

**Phase 3 gate:**
- [ ] Synoptic parallel viewer tested with 50 Torah passages
- [ ] Translation technique annotations reviewed by Targum scholar
- [ ] Verse alignment verified for all 5 Torah books

**Phase 4 gate:**
- [ ] Root-play detector precision >80% on manually annotated test set
- [ ] Biblical allusion tracker reviewed by Ephrem scholar
- [ ] Non-verse indexing system handles all reference formats

---

## 16. Go-to-Market Strategy

### 16.1 Academic Launch (Phase 2-3)

1. **Pre-launch:** Share beta with 5-10 scholars in Syriac/Targum studies for feedback
2. **Conference presentations:**
   - Society of Biblical Literature (SBL) Annual Meeting — Digital Humanities section
   - International Syriac Studies Symposium
   - NACAL (North American Conference on Afroasiatic Linguistics)
3. **Academic paper:** "The Aramaic Root Atlas: A Cross-Corpus Digital Tool for Triliteral Root Analysis" — submit to *Digital Scholarship in the Humanities* (Oxford) or *Journal of Data Mining and Digital Humanities*
4. **Digital Humanities directories:** Register with DARIAH, Digital Orientalist, AWOL (Ancient World Online)

### 16.2 Community Building

1. **Sefaria partnership:** Propose cross-linking (Atlas links to Sefaria texts; Sefaria links to Atlas root analysis)
2. **CAL relationship:** Position as complementary, not competitive. Link to CAL lexicon entries.
3. **Spanish-language outreach:** Seminarios in Mexico, Spain, Argentina, Colombia. Present at ALALC (Asociacion Latinoamericana de Lenguas y Culturas).
4. **Open-source community:** GitHub repository; invite contributions for additional corpora.

### 16.3 Content Marketing

- Blog series: "Tracing Aramaic Roots Across Centuries" (one per notable root)
- Video tutorials: "How to use the Synoptic Parallel Viewer" (ES and EN)
- Social media: Weekly "Root of the Week" cross-corpus spotlight

---

## 17. Timeline & Milestones

```
2026
  Q2 (Apr-Jun)
    ├── Apr: Acquire Peshitta OT text, validate
    ├── May: Run root extraction + cognate pipeline
    ├── Jun: UI integration, testing → Phase 1 RELEASE
    └── Jun: Begin Sefaria API integration for BA

  Q3 (Jul-Sep)
    ├── Jul: characters.py multi-script, corpus.py multi-corpus
    ├── Aug: BA affixes + root extraction + cross-corpus cards
    ├── Sep: Testing, scholar review → Phase 2 RELEASE
    └── Sep: Begin Targum Onkelos data acquisition

  Q4 (Oct-Dec)
    ├── Oct: Targum morphology + verse alignment system
    ├── Nov: Synoptic Parallel Viewer + translation technique
    ├── Dec: Testing, Targum scholar review → Phase 3 RELEASE
    └── Dec: Submit academic paper, SBL proposal

2027
  Q1 (Jan-Mar)
    ├── Jan: Ephrem text acquisition, non-verse indexing
    ├── Feb: Root-play detector, biblical allusion tracker
    ├── Mar: Testing, Ephrem scholar review

  Q2 (Apr-Jun)
    ├── Apr: Phase 4 RELEASE
    ├── May: Academic presentations, community outreach
    └── Jun: Phase 5 planning (Talmudic Aramaic? Other Targumim?)
```

---

## 18. Open Questions

| # | Question | Impact | Decision needed by |
|---|----------|--------|--------------------|
| Q1 | Should the app rebrand to "Aramaic Root Atlas" at Phase 2, or wait until Phase 3 when cross-corpus comparison is fully realized? | Branding, URL, SEO | Phase 2 start |
| Q2 | Sefaria data is CC-BY-SA — does this require the entire Atlas to be share-alike, or only the Sefaria-derived portions? | Licensing | Phase 2 start |
| Q3 | Should we pursue a formal partnership with Sefaria for cross-linking? | Distribution, credibility | Phase 2-3 |
| Q4 | Which Peshitta OT digital text is highest quality? SEDRA vs. Dukhrana vs. ETCBC/Leiden | Data quality | Phase 1 start |
| Q5 | East Syriac vs. West Syriac pronunciation for audio integration (separate TTS project)? | Audio feature | Phase 1 |
| Q6 | Should we contact Beth Mardutho about Ephrem texts now or wait until Phase 3? | Lead time | Phase 2 |
| Q7 | Is there appetite for a Talmudic Aramaic Phase 5? Should we architect for it now? | Technical debt | Phase 2 architecture |
| Q8 | Should the synoptic parallel viewer support Targum Pseudo-Jonathan alongside Onkelos? | Scope | Phase 3 start |
| Q9 | Academic advisory board — should we form one? Who? | Credibility | Phase 2 |
| Q10 | Hosting: current setup sufficient, or should we plan for higher traffic post-launch? | Infrastructure | Phase 3 |

---

## 19. Appendices

### Appendix A: Infrastructure Reuse Map (Shared Library Architecture)

**Extracted into `aramaic-core` (Phase 1):**
- `characters.py` — transliteration, script detection, `normalize_root()` (Phase 2+)
- `corpus.py` — CSV loading, word index, verse lookup → extended with `corpus_id` and multi-CSV
- `affixes.py` — morphological analysis → extended per dialect
- `extractor.py` — root extraction + scoring → extended with cross-corpus scoring
- `cognates.py` — cognate lookup, semantic bridges → extended with cross-corpus attestation
- `glosser.py` — morphological glossing → extended per dialect

**Peshitta Root Finder (stays in current app, imports aramaic-core):**
- Flask routes, templates, static assets — unchanged
- `cognates.json`, `known_roots.json` — Peshitta-specific data stays here
- D3.js visualizations — stay here, copied/adapted for Atlas
- i18n system, bookmarks, CSS design — stay here
- Claude API pipeline scripts — stay here, shared via scripts/ or copied

**Atlas app (new, imports aramaic-core):**

*Reused from Peshitta app (copied + adapted):*
- Flask route patterns and API conventions
- D3.js constellation and root family visualizer code (add corpus color-coding)
- i18n framework and bilingual UI architecture
- CSS design system (new palette: corpus-coded colors)
- Bookmark system pattern
- `global.js` client utilities

*New code for Atlas:*
- `alignment.py` in `aramaic-core` — verse alignment engine (Hebrew↔Targum↔Peshitta)
- `parallel.html` — Synoptic Parallel Viewer template
- `root_play.py` in `aramaic-core` — paronomasia detection module
- `allusion.py` in `aramaic-core` — biblical allusion tracker module
- Non-verse reference system in `corpus.py` (for patristic texts)
- Cross-corpus root card template
- Attestation timeline component
- Translation technique annotation UI
- `cross_corpus_index.json` — root → {corpus: [refs]} index
- `annotations/*.json` — translation technique and root-play data
- Data acquisition scripts: `scripts/fetch_ba_text.py`, `scripts/fetch_targum.py`, etc.

### Appendix B: Aramaic Dialect Family Tree (Simplified)

```
Proto-Semitic (~3000 BCE)
  └── Proto-Aramaic (~1100 BCE)
       ├── Old Aramaic (1100-700 BCE)
       │    inscriptions, Tell Fekheriye
       │
       ├── Imperial/Official Aramaic (700-200 BCE)
       │    ├── Biblical Aramaic ← PHASE 2
       │    └── Elephantine papyri
       │
       ├── Western Aramaic
       │    ├── Jewish Palestinian Aramaic (Jerusalem Talmud, Palestinian Targumim)
       │    ├── Samaritan Aramaic
       │    └── Western Neo-Aramaic (Maaloula — still spoken)
       │
       └── Eastern Aramaic
            ├── Jewish Babylonian Aramaic (Babylonian Talmud)
            ├── Mandaic (Ginza Rba)
            ├── Classical Syriac ← PESHITTA (anchor corpus)
            │    ├── Peshitta Bible ← PHASES 1, 3
            │    └── Syriac Fathers ← PHASE 4
            ├── Targum Onkelos ← PHASE 3
            │    (debated: Eastern or transitional)
            └── Neo-Aramaic dialects
                 ├── Turoyo
                 ├── NENA (Northeastern Neo-Aramaic)
                 └── Chaldean Neo-Aramaic
```

### Appendix C: Competitor Feature Matrix (Detailed)

| Feature | Atlas (target) | CAL | Dukhrana | Sefaria | SEDRA |
|---------|---------------|-----|---------|---------|-------|
| Triliteral root search | Yes (all corpora) | Yes (lexicon) | Basic | No | Yes (Syriac only) |
| Cross-corpus root tracking | Yes | Within CAL | No | No | No |
| Hebrew cognates | Yes (with nikkud) | No | No | No | No |
| Arabic cognates | Yes (with tashkil) | No | No | No | No |
| Greek NT parallels | Yes | No | No | No | No |
| Semantic bridges | Yes | No | No | No | No |
| D3.js visualization | Yes | No | No | No | No |
| Synoptic parallel viewer | Yes (Phase 3) | No | No | Partial (text-only) | No |
| Translation technique analysis | Yes (Phase 3) | No | No | No | No |
| Root-play detection | Yes (Phase 4) | No | No | No | No |
| Biblical allusion tracking | Yes (Phase 4) | No | No | Partial (links) | No |
| Spanish UI | Yes | No | No | No | No |
| Open source | Yes | No | No | Yes | Partial |
| Morphological tagging | Partial (affixes) | Full | No | No | Full |
| Manuscript variants | No | No | No | No | No |
| Audio integration | Planned | No | Yes | No | No |

### Appendix D: Budget Estimate (Claude API Costs)

| Phase | Task | Est. API calls | Est. cost |
|-------|------|---------------|-----------|
| 1 | Generate cognates for ~300 new OT roots | ~300 | ~$30-50 |
| 1 | Generate semantic bridges for OT outliers | ~100 | ~$10-20 |
| 2 | Generate cognates for ~70 BA-unique roots | ~70 | ~$7-15 |
| 3 | Generate cognates for ~100 Targum-unique roots | ~100 | ~$10-20 |
| 3 | Translation technique classification (stretch) | ~500 | ~$50-100 |
| 4 | Generate cognates for ~50 Ephrem-unique roots | ~50 | ~$5-10 |
| **Total** | | ~1,120 | **~$112-215** |

---

*End of document. This PRD is a living document and will be updated as each phase progresses.*
