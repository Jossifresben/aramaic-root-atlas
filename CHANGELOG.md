# Changelog — Aramaic Root Atlas

All notable changes are documented here. Each release also has a Zenodo deposit
with its own DOI; the **concept DOI** [10.5281/zenodo.19358625](https://doi.org/10.5281/zenodo.19358625)
always resolves to the latest version.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/),
extended with a **Data Changes** sub-section that lists modifications to the
indexed corpora, glosses, cognates, or extraction outputs (information
researchers need when deciding whether re-runs of cited analyses are
reproducible).

## [v3.0.1] — 2026-05-09

Compliance, transparency, and credibility hotfix. No new features, no API
changes; closes 17 of the 47 items raised in the May 2026 critique pass.

### Added
- `LICENSE-DATA.md` at repo root: per-corpus licenses (PD, CC-BY-NC, CC-BY-SA,
  CC-BY) with use-restrictions table.
- README "Limitations & Caveats" section disclosing 12 specific methodological
  weaknesses up front.
- `docs/ROADMAP-v3.1.md` mapping 47 critique items to phased remediation.
- `/privacy` page in EN/ES/HE/AR with opt-in/opt-out toggle and live status.
- First-visit cookie consent banner with Accept / Decline.
- Per-page `<title>` tags consistent across all 18 templates.
- Footer link to `/privacy` on every page.

### Changed
- **Google Analytics is now opt-in only.** Default state: tracking OFF. The
  `gtag.js` script loads only after explicit consent. IP anonymization enabled.
- Cite modal default URL → canonical project URL (was `window.location.href`).
- BibTeX type `@misc` → `@software`. APA `[Web application]` → `[Computer
  software]`. Chicago/MLA include "Zenodo" as publisher.
- README License section split: Apache-2.0 (code) vs. mixed (data).
- Watch Video walkthrough disabled with "being updated for v3.0" notice
  in 4 languages until re-recorded against the new sidebar UI.
- Ephrem corpus relabeled "Hymns on Nisibis (Carmina Nisibena)" with scope
  caveat in README + SOURCES.md.

### Fixed
- Guided Tour selector `.corpus-cells` → `.corpora-grid` (was silently
  skipping the corpus-stats step).
- Tour walkthrough verified against v3.0 DOM in EN.
- Hardcoded version refs synced with v3.0 (cite-modal `VERSION`, sidebar
  foot label, About page citation).

### Data Changes
- None (no corpus, gloss, cognate, or extraction-output changes).

### Disclosed
- Cognates flagged as **LLM-generated and pending lexicographic validation**
  against HALOT, BDB, Sokoloff, Brockelmann, Lane, Wehr.
- Greek translation track flagged as SBLGNT (Holmes 2010, CC-BY-SA), not
  the more-cited NA28 (NestleAland 28th ed.).
- Peshitta NT digitization lineage credited: dukhrana.com (Stephen Silver) +
  SEDRA (Beth Mardutho).
- Ephrem corpus disclosed as one collection (~5%) of Ephrem's surviving works.

---

## [v3.0] — 2026-05-08

Major release: full UI redesign + Swagger API reference + cite modal +
quadrilingual i18n sweep + Hymns of Ephrem corpus added.

### Added
- **New sidebar app shell** — persistent left rail (Explore / Analyze /
  Workspace), sticky topbar with breadcrumb, ⌘K quick-search, tooltipped
  action icons.
- **Interactive Swagger UI API reference** at `/api-docs` covering all 28
  REST endpoints with try-it-out, parameter examples, response schemas.
  OpenAPI 3.0.3 spec at `/static/swagger.json`.
- **Cite modal** — one-click citation export in BibTeX, Chicago, MLA, APA,
  SBL formats from any analysis page; DOI-linked, copy-to-clipboard.
- **Hymns of Ephrem of Nisibis** corpus (1,435 verses, 29,477 words) from
  the Digital Syriac Corpus.
- **2,192 Greek NT cognates** linking Aramaic roots to Greek equivalents.
- **Watch Video** modal on the Guide page (later disabled in v3.0.1).
- **In-app guided tour** (12 steps) extended to walk new sidebar layout.
- Distinct corpus color palette (emerald / blue / purple / amber / crimson)
  applied consistently across stat cards, badges, and tables.

### Changed
- Type scale lifted ~12.5% on rem-based content; px-chrome floor sweep
  raises 10/11/12/13px declarations one step up each (~8.6% lift on
  small UI text).
- Full template internationalization sweep across EN/ES/HE/AR with RTL
  support: every page (homepage, browse, reader, concordance, diachronic,
  hapax, heatmap, parallel, visualize, parse, collocations, semantic
  fields, passage profile, bookmarks, annotations, about) translated.
- "Search" → "Trace Root" terminology throughout; `?` → quick-search hotkey.

### Fixed
- Sticky-topbar-aware scroll helper (window scroll, not `.main` flex
  container).
- `lang` query param preserved across all sidebar nav links.
- Mobile overflow patches at 760px breakpoint.
- Dropdown active-state checkmarks; ref-separator dot visibility.

### Data Changes
- Ephrem corpus added: +1,435 verses, +29,477 words. New corpus key
  `ephrem_nisibis`.
- Greek SBLGNT translation track added (7,939 verses, `grc_sbl`).
- Cognate count: 1,127 Hebrew/Arabic + 2,192 Greek (was 1,127 / 0).
- Total root index expanded to 5,039 (was 4,485).

---

## [v2.3] — 2026-03-31

Watch Video modal, Tour updates, Guide page refresh.

### Added
- Watch Video modal on Guide page (viewport-wide, fullscreen support).
- Guided Tour: corrected selectors, "Roots only across all five corpora"
  search-step copy, SH-L-M as canonical example.

### Data Changes
- None.

---

## [v2.2] — 2026-03-29

Word Parser, Passage Profile, Guided Tour. Major UX polish.

### Added
- **Word Parser** at `/parse` — full morphological breakdown of any Syriac
  word with stem, cognates, attestations.
- **Passage Lexical Profile** at `/passage-profile` — unique roots, lexical
  density, hapax counts, stem distribution, top-15 roots, per-verse
  density sparkline for any book + chapter range.
- 12-step Driver.js guided tour, EN/ES/HE/AR.

### Data Changes
- None.

---

## [v2.1] — 2026-03-28

Collocations, Semantic Fields, Annotations.

### Added
- **Collocations** at `/collocations` — PMI-scored root co-occurrence
  at verse or chapter scope.
- **Semantic Fields** at `/semantic-fields` — 15-domain classification
  of all roots (legal/covenant, cultic, kinship, war, knowledge, etc.)
  via Claude Haiku.
- **Researcher Annotations** at `/annotations` — inline notes on verses
  and roots, tag-based filtering, JSON/CSV/Markdown export.
- Multilingual glosses (HE/AR added to existing EN/ES).

### Data Changes
- Multilingual gloss expansion: +HE, +AR for all glossed forms.
- Semantic field assignments added to root metadata.

---

## [v2.0] — 2026-03-28

Verb Stems, KWIC Concordance, Diachronic Analysis, Hapax Legomena.

### Added
- **Verb Stem (Binyan) Analysis** — every word form classified into
  Peal/Ethpeel/Pael/Ethpaal/Aphel/Shafel/Ettaphal. Stem badge in word
  popover; stem distribution chart and paradigm table in root card.
- **Hapax Legomena Finder** at `/hapax` with frequency slider, corpus
  filter, scope toggle, CSV/JSON export.
- **KWIC Concordance** at `/concordance` — left-context | keyword |
  right-context layout, group by form or stem, CSV/JSON/plain-text/TEI
  XML export.
- **Diachronic Root Analysis** at `/diachronic` — normalized frequency
  per corpus in chronological order; Frequency Shifts view.

### Data Changes
- Stem (binyan) classification added to word-level data.
- Paradigm tables computed for all roots.

---

## [v1.1.0] — 2026-03-27

Corpus expansion: Targum Onkelos.

### Added
- **Targum Onkelos** corpus (5,846 verses, 82,684 words; Torah only)
  via Sefaria API.
- Synoptic parallel viewer at `/parallel` (Peshitta OT ↔ Targum Onkelos
  ↔ Biblical Aramaic).
- Root frequency heat map at `/heatmap` with filter, sort, CSV/JSON export.

### Data Changes
- Targum Onkelos corpus added: +5,846 verses, +82,684 words.

---

[v3.0.1]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v3.0.1
[v3.0]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v3.0
[v2.3]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v2.3
[v2.2]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v2.2
[v2.1]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v2.1
[v2.0]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v2.0
[v1.1.0]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v1.1.0
