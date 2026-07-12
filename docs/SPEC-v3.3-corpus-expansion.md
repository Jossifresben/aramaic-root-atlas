# SPEC — v3.3.0 Corpus Expansion: Targums to the Writings + Ephrem (Other Works)

> Status: **in execution** (started 2026-07-12). Companion to
> `docs/CORPUS-EXPANSION-PLAN.md` (completes Phase 6A.2 and inserts a new
> "Targum Writings" item that plan had missed). Written from agent-verified
> source research on 2026-07-12; source facts below are checked, not estimated,
> unless marked.

## Scope

Two new corpora (6 → 8):

| corpus_id | Label | Abbr | Script | Source | License |
|---|---|---|---|---|---|
| `targum_writings` | Targum Writings | `tgw` | Hebrew square | Sefaria API | Public Domain (per-version, see below) |
| `ephrem_works` | Ephrem — Other Works | `epw` | Syriac | Digital Syriac Corpus (srophe/syriac-corpus TEI) | CC-BY 4.0 |

**Dropped from scope: Old Syriac Gospels (Vetus Syra).** Research (2026-07-12)
found no openly-licensed machine-readable transcription: Kiraz's *Comparative
Edition of the Syriac Gospels* is under Brill/Gorgias copyright; CAL
(cal.huc.edu) has the text but in restricted, non-redistributable,
transliterated form; the public-domain Lewis (1910) / Burkitt (1904) editions
exist only as unreliable Syriac OCR on archive.org. Adding it would be a
digitization project, not an ingestion task. Future path: request permission
from CAL (skaufman@cn.huc.edu) or key from Lewis/Burkitt. The parallel viewer
already aligns on `reference` strings, so if a text ever materializes with
Peshitta-NT book names it will align with zero code changes.

## Corpus 1 — Targums to the Writings (`targum_writings`)

Ten Sefaria indices, all fetched with the `fetch_targum_jonathan.py` pattern
(fetch-until-empty per chapter, `clean_text`, `strip_diacritics`, 0.3s sleep):

| Sefaria index title | Output book name (MUST match Peshitta OT exactly) | Chapters |
|---|---|---|
| Aramaic Targum to Psalms | Psalms | 150 |
| Aramaic Targum to Job | Job | 42 |
| Aramaic Targum to Proverbs | Proverbs | 31 |
| Aramaic Targum to Ruth | Ruth | 4 |
| Aramaic Targum to Lamentations | Lamentations | 5 |
| Aramaic Targum to Ecclesiastes | Ecclesiastes | 12 |
| Aramaic Targum to Song of Songs | Song of Songs | 8 |
| Aramaic Targum to Esther | Esther | 10 |
| Targum of I Chronicles | 1 Chronicles | 29 |
| Targum of II Chronicles | 2 Chronicles | 36 |

- Book-name match to Peshitta OT (verified against `data/corpora/peshitta_ot.csv`
  2026-07-12: `Psalms, Job, Proverbs, Ruth, Lamentations, Ecclesiastes,
  Song of Songs, Esther, 1 Chronicles, 2 Chronicles`) gives Peshitta OT ↔
  Targum Writings parallel-viewer alignment for free (viewer is generic:
  books in ≥2 corpora, aligned on `reference`).
- **Excluded: `Targum Sheni on Esther`** — its only Sefaria version ("Berlin,
  1898") carries license "unknown" and is consonantal. Excluded until license
  clarity; note in LICENSE-DATA.md. (No targum to Daniel/Ezra exists — confirmed.)
- Licenses: Mikraot Gedolot version, Public Domain, vocalized — verified for
  Psalms/Job/Ruth/Song of Songs/Esther; **inferred** for Proverbs/Lamentations/
  Ecclesiastes; Chronicles = Wikisource version, Public Domain (I verified,
  II inferred). **Fetcher must read each version's `license` field at fetch
  time, fail loudly on anything other than "Public Domain"/CC, and emit a
  license report for LICENSE-DATA.md.**
- `book_order`: follow Peshitta OT's `book_order` values for the same books
  (read them from `peshitta_ot.csv`) so cross-corpus book sorting is coherent.
- Expected scale: ~6,900 verses (Psalms 2,527 alone), est. 300–450k words
  (Writings targums are paraphrastic). Report actuals.
- Chronology slot (`CORPUS_CHRONOLOGY`, app.py ~L2359): append last —
  `('targum_writings', 'Targum Writings', '~4th–8th c. CE')`.
- `read.html` L46: add `'tgw'` to `is_hebrew_script` tuple.

## Corpus 2 — Ephrem, Other Works (`ephrem_works`)

- Source: `srophe/syriac-corpus` GitHub repo, `data/tei/*.xml` (632 TEI files,
  CC-BY 4.0, bulk-downloadable). ~107 files carry author ref
  `syriaca.org/person/13` (Ephrem); 73 of them (file numbers **259–331**) are
  the Carmina Nisibena already ingested as `ephrem_nisibis`.
- **Kept separate from `ephrem_nisibis`** (do NOT merge/rename): the corpus_id
  is a documented API enum (Swagger, bookmarks, OG cards, tests); renaming
  breaks stable URLs. Diachronic gets two adjacent Ephrem rows — acceptable,
  label distinguishes them.
- Fetch approach: download the repo tarball once
  (`https://github.com/srophe/syriac-corpus/archive/refs/heads/main.tar.gz`)
  to the scratchpad instead of 632 API calls; parse every TEI header; select
  docs whose `<author ref=".../person/13">`; **exclude file numbers 259–331**;
  parse text with the existing `fetch_ephrem_nisibis.py` logic (namespace
  `http://www.tei-c.org/ns/1.0`, `<div type="section">` stanzas, direct
  text/tail only, skip refrains `ܥܽܘܢܺܝܬܳܐ` and non-Syriac lines).
- Book/chapter/verse synthesis: `book` = hymn-cycle name derived from the TEI
  title (e.g. "On Faith", "Nativity", "Against Heresies"); `chapter` = hymn
  number within the cycle; `verse` = stanza index; `reference` = "{book}
  {ch}:{v}". If a title doesn't parse into (cycle, number), fall back to
  `book='Ephrem'`, chapter = running index. Keep book names short and stable —
  they become browse cards and citation refs.
- Scale is **smaller than the old plan's ~500k estimate** (that assumed DSC
  had all 400+ hymns; it has ~107 docs incl. Nisibis). Expect roughly ~34
  docs / order of 50–150k words. Report actuals; update
  CORPUS-EXPANSION-PLAN.md numbers.
- Chronology slot: after `ephrem_nisibis`:
  `('ephrem_works', 'Ephrem — Other Works', '~337–373 CE')`.

## Integration checklist (from codebase map, agent-verified)

Per corpus: `app.py` (`add_corpus` ~L116; `CORPUS_ABBR` ×2 L562+L682;
`CORPUS_LABELS` L683; `CORPUS_CHRONOLOGY` ~L2359) · `static/style.css`
(8 rules per abbr: light/dark `--c-XXX`/`--c-XXX-soft`, `.cbadge.XXX` + dark,
`.corpus-cell.XXX`, `.chip[data-c]`, `.dia-bar.XXX i`, `.book-card.XXX`) ·
`data/i18n.json` (`corpus_<id>` ×4 langs; prose keys `index_lede`,
`ql_browse_desc` say "six corpora" → update) · 16 templates with their own
abbr/label/order/color maps (browse, index ×3 copies, concordance, diachronic,
visualize, parse, passage_profile, semantic_fields, hapax, collocations,
interlinear, heatmap, parallel, about, base) · `about.html` (count 6→8, corpus
table row + `--c-XXX-soft`, data-sources row, fix already-stale diachronic dot
legend) · `static/swagger.json` (corpus enum L110–117 + corpora table in
description) · `tests/` (see below).

Colors: existing palette is emerald/blue/purple/amber/crimson + rose-magenta
(`--c-tgj #b32a78`). Suggest `tgw` = teal family (~#0f766e) and `epw` = warm
sienna/copper (~#b45309-adjacent, distinct from amber) — final values must pass
contrast on both themes.

i18n label suggestions: `corpus_targum_writings` EN "Targum Writings",
ES "Tárgum de los Escritos", HE "תרגום כתובים", AR "ترجوم الكتابات";
`corpus_ephrem_works` EN "Ephrem — Other Works", ES "Efrén — Otras obras",
HE "אפרם — חיבורים נוספים", AR "أفرام — أعمال أخرى".

## Cognates

Clone `scripts/generate_cognates_targum_jonathan.py` per corpus; exclusive-set
literal `{'targum_writings'}` / `{'ephrem_works'}`, `--min-occ 2`; script
already calls Opus 4.8 with cached system prompt and has a `root_syriac`
collision guard. Expect modest new-root counts (heavy vocab overlap with
Onkelos/Jonathan and existing Syriac). Filter proclitic/particle
false-positives as the Jonathan run did.

## Tests

- Clone `tests/test_api_contracts.py::test_targum_jonathan_corpus_present` for
  each new corpus (in `/api/stats`, plausible scale, cross-script SH-L-M
  attestation for `targum_writings`, `/browse?corpus=` 200).
- New: parallel-alignment test — `/api/parallel?ref=Psalms 23:1` returns both
  `peshitta_ot` and `targum_writings` rows; a Chronicles ref aligns too.
- New: CSV loader sanity — row counts > floor, 6-column schema, no empty
  `syriac` fields, references parse.
- Fix stale docstring "across all 5 corpora" in `tests/test_paradigmatic_roots.py`.
- Whole suite (197 tests) must stay green.

## Memory gate (Render sizing)

Current: 6 corpora / 686k words ≈ 900 MB RSS (per CORPUS-EXPANSION-PLAN
hosting table ≈ 0.4 MB per 1k words marginal). Adding ~350–600k words projects
**+150–250 MB → ~1.05–1.15 GB RSS** — inside Render Pro headroom, but must be
**measured, not assumed**: before/after RSS of the fully-loaded app locally
(port 5002), recorded in CHANGELOG + this spec. If measured RSS exceeds
1.5 GB, stop and implement mitigations (string interning of book/reference
prefixes, drop redundant per-word dict fields, precomputed root index) before
release.

## Execution phases & model assignment

| Phase | Work | Agent model |
|---|---|---|
| A1 ∥ A2 | Fetch scripts + run fetches → CSVs (targum_writings; ephrem_works) | Sonnet (templated engineering) |
| B | Wire both corpora across app.py/CSS/i18n/16 templates/Swagger | Fable (broad, error-prone sweep + 4-lang i18n) |
| C | Tests (contracts, parallel alignment, loader) | Sonnet |
| D | Cognate generation (script itself calls Opus 4.8) | Sonnet driver |
| E | Memory measurement gate; docs (CHANGELOG, SOURCES.md, LICENSE-DATA.md, CLAUDE.md, CITATION.cff → 3.3.0, CORPUS-EXPANSION-PLAN.md status + corrected Ephrem numbers) | main session |
| F | Local verify on **:5002**, full test suite, commit. **No `git push` — user tests first and must explicitly say push.** | main session |

A1/A2 run in parallel (disjoint files). B starts only after both CSVs exist
(labels/counts feed templates). C–D after B. E–F last.
