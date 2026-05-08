# Changelog — Aramaic Root Atlas

All notable changes are documented here. Each release also has a Zenodo deposit
with its own DOI; the **concept DOI** [10.5281/zenodo.19358625](https://doi.org/10.5281/zenodo.19358625)
always resolves to the latest version.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/),
extended with a **Data Changes** sub-section that lists modifications to the
indexed corpora, glosses, cognates, or extraction outputs (information
researchers need when deciding whether re-runs of cited analyses are
reproducible).

## [v3.0.2] — 2026-05-09

Transparency, discoverability, and validation-foundations release.
Closes 7 additional critique items from the May 2026 review (now 24
of 47 closed). No corpus-data changes. Real bug fixed in cross-script
input handling.

### Added
- **`docs/VALIDATION.md`** — 12-section reference document collecting
  every quantitative and methodological caveat in one place: no
  precision/recall study yet, recall floor vs Brockelmann/Sokoloff,
  genre-chronology confound, chronology debate (esp. Targum Onkelos
  dating), LLM-generated cognates, triliteral framing failures on
  non-CCC roots, stem-classification ambiguity, translator bias,
  ephemeral localStorage, direction-aware Greek "cognates", thin
  corpus coverage, what 5,039 actually means.
- **`docs/SEARCH-ALGORITHMS.md`** — published the actual ranking
  rubric for all five search modes; what's NOT implemented (no
  embeddings, stemming, fuzzy match, synonym expansion).
- **`CHANGELOG.md`** — backfilled v1.1.0 → v3.0.1 with per-release
  Data Changes sections.
- **`og-image.png`** + Open Graph + Twitter Card + Highwire Press +
  Dublin Core + Schema.org `SoftwareApplication` JSON-LD on every
  page. Project is now real-search-engine and link-preview discoverable.
- **`/robots.txt`** + **`/sitemap.xml`** with 16 canonical URLs.
- **Diachronic-page caveat banner** in EN/ES/HE/AR — visible
  disclosure that the chart confounds genre with chronology and that
  the chronological ordering is editorial.
- **Test suite expanded 15 → 150 tests** across 6 files: smoke
  (every page route 200 in EN; homepage/about/privacy in 4 langs),
  API contracts (28 endpoints), cross-script normalization (8
  paradigmatic roots, 4 input scripts), paradigmatic-root regression
  battery (10 well-known roots × 5 endpoints).

### Changed
- README citation line bumped to v3.0.2.
- UI version refs synced to v3.0.2 (cite-modal, sidebar foot, About
  page citation).
- About-page Confidence-Scoring methodology rewritten: explicit that
  the score reflects extraction *path* not measured correctness, no
  P/R study published, indicator is a researcher-attention prior not
  citable evidence.
- About-page Verb-Stem feature description: "Aramaic stems" / "tallos"
  is now the primary term in EN/ES (was "binyanim" — that's the
  Hebrew term for a related-but-not-identical inventory). HE/AR keep
  their native scholarly terminology. "Group by form or binyan stem"
  → "Group by form or stem" in concordance description.
- TipTopJar demoted from prominent README ## Support section to a
  discreet `<sub>` line at the bottom; institutional reviewers see
  substance first.

### Fixed
- **`parse_root_input()` cross-script bug.** The README documented
  Syriac/Hebrew/Arabic input as supported via `/api/roots`, but the
  parser only handled Latin transliteration. Direct Syriac like
  `?q=ܫܠܡ` returned HTTP 400 "Could not parse root". Extended to
  detect input script and route accordingly: Syriac returned as-is
  (after letter-only filter), Hebrew letter-by-letter via existing
  `HEBREW_TO_SYRIAC` map, Arabic chained via `ARABIC_TO_LATIN →
  LATIN_TO_SYRIAC`. All four scripts now resolve to the same
  canonical root key. Surfaced by the new `test_cross_script.py`
  end-to-end test.
- BibTeX type `@misc` → `@software` in cite modal output.
- Cite-modal default URL → canonical project URL (was
  `window.location.href` — citing the page the user happened to be
  on rather than the work).

### Data Changes
- None (no corpus, gloss, cognate, or extraction-output changes).

### Disclosed
- Recall floor: 5,039 attested roots ≪ ~7,000 in Brockelmann's
  *Lexicon Syriacum*, ~6,000 in Sokoloff's *DJBA*. The Atlas figure
  reflects what's attested in 5 specific corpora, not a coverage
  ceiling.
- Diachronic charts confound genre/register/dialect/translation
  source with chronology — explicit banner now on the page.
- Chronological ordering is editorial; Targum Onkelos dating is
  scholarly debated.

---

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

[v3.0.2]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v3.0.2
[v3.0.1]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v3.0.1
[v3.0]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v3.0
[v2.3]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v2.3
[v2.2]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v2.2
[v2.1]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v2.1
[v2.0]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v2.0
[v1.1.0]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v1.1.0
