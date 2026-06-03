# Changelog — Aramaic Root Atlas

All notable changes are documented here. Each release also has a Zenodo deposit
with its own DOI; the **concept DOI** [10.5281/zenodo.19358625](https://doi.org/10.5281/zenodo.19358625)
always resolves to the latest version.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/),
extended with a **Data Changes** sub-section that lists modifications to the
indexed corpora, glosses, cognates, or extraction outputs (information
researchers need when deciding whether re-runs of cited analyses are
reproducible).

## [v3.1.1] — 2026-06-03

Patch release. Fixes two bugs surfaced by an adversarial multi-agent
bug-review of the v3.1.0 work.

### Fixed
- **Cognate `root_syriac` collisions (regression).** The Targum Jonathan
  cognate generation appended entries whose `root_syriac` duplicated an
  existing curated entry. `CognateLookup` indexes by `root_syriac`
  (last-write-wins), so the thinner generated entries shadowed richer
  curated ones in the visualizer and word parser (e.g. ܦܬܚ "open"
  effectively dropped from 7+7 to 1+1 Hebrew/Arabic cognates). Deduped
  `cognates.json` keeping the richest entry per `root_syriac` and merging
  in unique cognate words; added a collision guard to the generator so a
  duplicate key/`root_syriac` is skipped rather than clobbering.
- **Orphan parentheses across a verse boundary.** A Sefaria parenthetical
  spanning Joshua 21:36→37 left a lone `(`/`)` glued to two word tokens,
  corrupting their root extraction. `clean_text()` now strips orphan
  brackets; the two affected cells were cleaned.

### Data Changes
- **Cognate entries 1,655 → 1,604** (removed 51 duplicate `root_syriac`
  keys; 0 collisions remain). Cognate words: 4,572 Hebrew + 4,580 Arabic.
  Verse/word/root totals unchanged (47,358 / 685,848 / 5,666).

## [v3.1.0] — 2026-05-29

First half of the Phase 6A corpus expansion (see `docs/CORPUS-EXPANSION-PLAN.md`).
Adds Targum Jonathan to the Prophets, doubling Targumic coverage and
unlocking Peshitta OT ↔ Targum Jonathan synoptic comparison for the
Prophets in the parallel viewer.

### Added
- **Targum Jonathan to the Prophets** — sixth corpus. 9,296 verses,
  157,449 words across 21 books (Joshua–II Kings, Isaiah, Jeremiah,
  Ezekiel, and the Twelve). Hebrew square script; cross-script root
  normalization (Hebrew שלם ↔ Syriac ܫܠܡ → `SH-L-M`).
- `scripts/fetch_targum_jonathan.py` — Sefaria fetch script
  (fetch-until-empty per book; consonantal text, diacritics stripped).
- `scripts/generate_cognates_targum_jonathan.py` — Opus 4.8 cognate
  generator scoped to Jonathan-exclusive roots, with prompt caching and
  crash-safe incremental writes.
- Distinct rose-magenta corpus color (`--c-tgj #b32a78`, abbr `tgj`);
  wired into all templates, i18n (EN/ES/HE/AR), and the Swagger spec.

### Fixed
- README corpus table listed Targum Onkelos as "Syriac"; corrected to
  "Hebrew square" (it is Hebrew square script, like Biblical Aramaic).
- **Cross-corpus book-name alignment:** Targum Jonathan's Samuel/Kings
  used Roman numerals ("I Samuel") while the rest of the Atlas uses
  Arabic ("1 Samuel"). Mismatched names hid those four books from the
  parallel viewer and broke alignment; normalized to Arabic numerals.
- **Root Card visualizer was clipped** to the graph's fixed 540px height,
  hiding the diachronic bars, sister roots, and the cognate/derivatives
  table below the fold. The card now grows to fit its content.
- Diachronic-bar corpus labels overflowed their pills in the visualizer.
- Corrected redundant page titles ("Visualize root family Root
  Visualizer", "Parallel Viewer viewer", "Diachronic Analysis Diachronic
  Analysis") and the visualizer breadcrumb ("Browse corpora" → "Root
  Visualizer").
- **Reconciled stale "five corpora" copy → "six"** across all four UI
  languages (browse, concordance, tour, diachronic caveat, About page,
  Swagger); the About corpus list now includes Targum Jonathan. Refreshed
  Swagger example totals to the six-corpus state.

### `.zenodo.json`
- Added a `.zenodo.json` deposit record with a full tool description,
  a "what's new in v3.1" section, citation guidance, keywords, and the
  concept-DOI relationship.

### Data Changes
- **Corpora 5 → 6.** Totals: 38,062 → 47,358 verses; 528,399 → 685,848
  words; 72,566 → 105,237 unique forms.
- **Roots 5,249 → 5,666** (+417 newly attested). Re-runs of cited
  cross-corpus or diachronic analyses that omit Targum Jonathan will
  differ from analyses run after this change.
- Source: Sefaria API (Targum Jonathan, CC-BY-SA), fetched 2026-05-29.
- **Cognates 1,584 → 1,655** (+71 entries; 4,647 Hebrew + 4,634 Arabic
  cognate words). Generated with Opus 4.8 via
  `scripts/generate_cognates_targum_jonathan.py`, scoped to roots
  attested only in Targum Jonathan (≥2 occurrences): 84 genuine roots
  identified, ≈200 proclitic/particle false-positives filtered. A few
  cognates also gap-filled common roots that previously lacked entries
  (e.g. ܩܒܪ "bury"). All entries carry a Syriac `root_syriac` for
  lookup. Cost ≈ $2. Cognates remain `unverified` pending lexicographer
  review per `docs/VALIDATION.md`.

## [v3.0.3] — 2026-05-09

Infrastructure & accessibility release. Closes 3 more critique items
(C1.16, C2.25, plus an a11y floor across all 19 pages) and corrects
3 stale headline numbers that had drifted from the live data.

### Added
- **Accessibility floor: every page scores 100/100 on Lighthouse**
  (audited 19 pages). Fixes:
  - `--ink-4` darkened from #8e8676 → #6e6353 in light mode and
    lightened from #6e6757 → #88806c in dark mode (≥4.5:1 on warm
    surfaces; was 3:1)
  - Corpus badges now use a darker `--cb-text` per corpus (Peshitta
    NT/OT, BA, Targum, Ephrem) so badge text passes 4.5:1 against the
    soft-tinted background; dot prefix keeps the brighter colour
  - Footer + cookie banner + privacy-page links now have explicit
    underline + 2px offset (link-in-text-block)
  - About-page feature-card headings: `<h4>` → `<h3>` (heading order)
  - 22 `<label for=X>` ↔ `<select id=X>` pairings wired across 7
    templates; `aria-label` on every floating select
  - Range sliders (hapax frequency, concordance context width) now
    have proper labels + `aria-valuemin/max/now` + `aria-controls`
  - Heatmap colour scale: heat-4/heat-5 opacity bumped from 0.45/0.65
    → 0.85/0.95 so white text actually clears 4.5:1
  - Swagger UI (third-party): CSS overrides on `.info a` + HTTP
    method badges; JS injects `aria-label` on `#servers` and promotes
    Swagger's `<h3>` tag headings to `<h2>` for proper hierarchy
- **API versioning** — every `/api/X` endpoint is also reachable at
  `/api/v1/X`. Single source of truth via a post-registration loop
  that walks the URL map after all routes register and adds a v1
  alias for each `/api/` rule. 29 endpoints aliased.
- **Rate limiting** (Flask-Limiter) — 600 req/min and 60 req/sec per
  IP. Every API response now includes `X-RateLimit-Limit`,
  `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `Retry-After`
  headers. Excess requests get HTTP 429.
- `docs/API-STABILITY.md` — versioning + 12-month deprecation policy
  for breaking changes; what counts as breaking vs non-breaking;
  rate limits + headers; CORS posture; cite-the-version-DOI guidance
- `docs/SUCCESSION.md` — per-asset access documentation (GitHub,
  Render, Zenodo, GA, Anthropic API), recommended institutional
  anchors, minimum survival kit, "how to keep healthy as a successor"
  runbook
- Test suite expanded **150 → 197 tests**. New file
  `tests/test_api_versioning.py` (47 tests): byte-identical legacy↔v1
  parity for representative endpoints, regression guard against new
  routes landing without an alias, count-match sanity check, limiter
  is wired
- Swagger spec (`static/swagger.json`) bumped to 3.0.3 with API
  versioning + rate-limiting sections in the description

### Changed
- **Root count: 5,039 → 5,249** in current-state docs. Live
  `/api/stats` had been reporting `root_count: 5249` since cognate-
  generation work landed earlier; README and docs hadn't caught up.
- **Cognate root entries: 1,127 → 1,584** in current-state docs.
  Live `data/roots/cognates.json` has 1,584 entries (1,577 with
  Hebrew and/or Arabic cognates; 405 with a Greek NT parallel;
  1,584 with at least one cognate). 4,599 individual Hebrew + 4,633
  Arabic cognate words across all entries.
- **Greek NT cognates: 2,192 → 405** — the 2,192 number was an
  overcount of unclear origin (possibly counting SBLGNT verses with
  Aramaic parallels rather than distinct cognate links). Actual
  count from the data: 405 roots have a single `greek_parallel`
  entry (one Greek word per root at most).
- UI version refs synced to v3.0.3 (cite-modal, sidebar foot, About
  page citation, README cite line, CITATION.cff)
- Footer + cookie-banner + privacy-page links now explicitly underline
  (was relying on color alone — failed AA link-in-text-block)

### Fixed
- A11y regressions across 19 pages now closed (see Added above)
- Historical mentions in CHANGELOG and Phase 1 notes preserved as
  snapshots of their respective release states; only current-state
  references corrected

### Data Changes
- None. The underlying CSVs, cognates.json, and extraction outputs
  are unchanged. The 5,249 / 1,584 / 405 figures reflect the live
  state at v3.0.3 — what changed is that the docs now reflect it.

### Disclosed
- API stability contract: `/api/v1/` is the recommended base; legacy
  `/api/` URLs continue to work but have no contract. Breaking
  changes require major version bump + 12-month deprecation per
  `docs/API-STABILITY.md`.
- Succession plan published: `docs/SUCCESSION.md` documents what a
  successor needs (GitHub admin / Render team membership / Zenodo
  GitHub-integration link) to keep the project alive.

---

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

[v3.0.3]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v3.0.3
[v3.0.2]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v3.0.2
[v3.0.1]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v3.0.1
[v3.0]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v3.0
[v2.3]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v2.3
[v2.2]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v2.2
[v2.1]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v2.1
[v2.0]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v2.0
[v1.1.0]: https://github.com/Jossifresben/aramaic-root-atlas/releases/tag/v1.1.0
