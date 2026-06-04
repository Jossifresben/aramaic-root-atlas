# Design: Repositioning the Aramaic Root Atlas as a Discovery Tool

**Date:** 2026-06-04
**Status:** Approved (brainstorming) — pending spec review
**Author:** Jose Fresco Benaim (with Claude)

---

## 1. Summary

Reposition the existing Aramaic Root Atlas from an implied scholarly-reference tool
into **The Triliteral Aramaic Atlas — a discovery tool for students and curious
minds**. The product's promise becomes *wonder*: pick a three-letter root and watch
it travel across ~1,500 years and two scripts. The hero experience is the
**time-travel root** (cross-corpus, diachronic sweep), with **cousin cognates**
across Hebrew/Arabic as a delightful secondary thread explicitly framed as
"fascinating, not gospel."

This is a **framing + UI/IA repositioning of the existing Flask app**, not a rewrite.
The linguistic engine, data, and JSON API are reused unchanged. No new root-extraction
logic is introduced. The work is new templates, a new homepage, one new hero view, a
new Discovery journeys page, a sidebar/IA regroup, and the surfacing of honest caveats
at the point of use.

### Why this resolves the prior critique

A harsh review of the project (and its draft paper) centered on one fact: the tool's
analytical outputs (root counts, cognates, confidence scores, diachronic frequencies)
are heuristic and unvalidated, so they are not safely citable. As a discovery tool that
position is no longer a flaw — nobody is asked to footnote a count. The known weaknesses
become **teaching moments** surfaced in context:

- Homograph conflation (ŠLM = "peace" *and* "to repay") → a "one skeleton, several
  meanings" lesson on the hero view.
- LLM-generated cognates → "explorers' leads, not dictionary-grade etymology."
- Heuristic confidence / genre-confounded diachrony → one-line caveat banners on the
  advanced tools.

The word "Atlas" stops being something to apologize for and becomes the honest promise:
a *map for exploring*, not an exhaustive census.

## 2. Goals

- A newcomer who knows **zero roots** reaches a first "aha" in under a minute.
- The cross-script unification ("two scripts, one root") and the diachronic sweep are
  the emotional center, legible at a glance.
- Every output a newcomer might over-trust carries an honest, friendly disclosure where
  it appears.
- The existing scholarly tools remain available, reframed as *exploratory* (not
  citable), nothing deleted.
- No change to the engine, data, DOI, or repository identity.

## 3. Non-goals

- No precision/recall study, gold standard, or cognate validation (out of scope; the
  repositioning removes the *need* for them to ship this).
- No root-extraction or disambiguation algorithm changes.
- No repo rename, no new DOI, no data-license changes.
- No account system or persistence changes.
- No new corpora.

## 4. Target users

Primary: students, lifelong learners, and curious adults with no Semitic-languages
background. Secondary (retained, demoted): researchers using the exploratory tools with
eyes open to the caveats.

## 5. Architecture — two doors

One app, two entrances, regrouped sidebar:

- **Discover (new default, `/`).** The curious-newcomer entrance. Curated hero roots,
  root-of-the-day, "start from a word you know" search, link to Discovery journeys.
- **Explore (renamed advanced area).** Everything that exists today — visualizer,
  reader, parallel viewer, concordance, hapax, PMI collocations, diachronic, paradigms,
  semantic fields, word parser, heatmap, API/Swagger — grouped under "Explore /
  Advanced," each wearing a one-line "exploratory, not citable" caveat banner.

The sidebar regroups from today's flat scholar-tool rack into two groups: **Discover**
(front) and **Explore** (advanced).

All new Discover surfaces are **read-only** and consume existing endpoints
(`/api/roots`, `/api/root-family`, `/api/diachronic/root`, `/api/verse`,
`/api/reverse-search`). No new analytical endpoints are required for v1.

## 6. The front door (`/`, Discover home)

A single warm landing page, three zones top to bottom:

1. **Hook line + meaning search.** A short promise ("Every Aramaic word grows from a
   three-letter root. Pick one and watch it travel.") and one input: *type a word you
   know* (peace, king, write, bless). Maps the English/Spanish word to a root via the
   existing reverse-meaning search and routes to the Root Journey. Relabeled honestly as
   a "best guess," not "the answer."
2. **Root of the day.** One featured card: root in Syriac + Hebrew + transliteration, a
   one-line flavor, a mini time-travel sparkline across the six corpora, and a "see its
   journey" button. Rotates daily, chosen **deterministically by date** from a curated
   list (no randomness — must be reproducible and avoids the `Math.random`/`Date.now`
   issues in cached contexts; server computes index from the current date).
3. **Curated hero roots.** A grid of ~8–12 hand-picked vivid roots (e.g. šlm, ktb, mlk,
   brk, qdš, ḥyy, ʾmr, škn) as story cards. Click → Root Journey.

A quiet footer link: "Looking for the research tools? → Explore."

Curated/hero root lists and the root-of-the-day pool are stored as a small data file
(`data/discovery/featured_roots.json`) so the curation can change without code edits.

## 7. The hero — "Root Journey" view

The page everything funnels into; the thing people screenshot. One root told as a
journey through time, scroll-driven, newcomer-legible. New route, e.g.
`/journey/<root_key>`; renders a new template; all data from existing APIs.

Sections, top to bottom:

1. **The root, big.** Syriac ܫܠܡ · Hebrew שלם · `SH-L-M`, with the canonical-key note
   ("both scripts, one root") and a plain-language gloss. The cross-script aha in one
   glance.
2. **The timeline strip.** The six corpora as a left-to-right chronological ribbon
   (Biblical Aramaic → Targum Onkelos → Targum Jonathan → Peshitta NT → Peshitta OT →
   Ephrem), each a bar sized by frequency and clickable to a real example verse. This is
   the time-travel hero, reusing `/api/diachronic/root` data.
3. **"One skeleton, several meanings."** An honest panel naming the homograph reality:
   "ŠLM can mean *peace/wholeness* and also *to repay* — same three letters, different
   senses. This tool groups words by their skeleton; a dictionary separates the senses."
4. **Cousins across languages (dash of B).** Hebrew *shalom*, Arabic *salām / Islam* as
   "related words in sister languages," tagged: *"Fascinating connections — explorers'
   leads, not dictionary-grade etymology."* From the existing cognate data.
5. **One real verse, decoded.** A single paradigmatic verse (already stored per root)
   with the root highlighted and translated — proof it is a living text.
6. **Keep exploring.** Buttons to the full visualizer, the reader, or "another root."

Adds no extraction logic; it is a narrative skin over already-computed data.

## 8. The Discovery page (`/discover` journeys)

A browsable shelf of **guided journeys** — short authored multi-root walks with a
museum-exhibit feel. Each journey is an ordered list of roots plus a sentence of
narration per stop, rendering as a scrollable story that hands off into individual Root
Journeys.

- Launch with ~4–6 hand-authored journeys, e.g.: "Words of the Covenant" (brk, qdš,
  qym), "Kings & Kingdoms" (mlk, šlṭ, dyn), "From shalom to Islam," "Everyday Aramaic"
  (say, do, go, see), "The Sacred Vocabulary" (holy, bless, pray, glory).
- Stored as simple data files `data/journeys/*.json` — no code change to add a journey.
  Each: `{ title, blurb, stops: [{ root, note }] }`.
- Fast-follow after the hero view; this is content authoring, not engine work.

## 9. Honesty-as-pedagogy + tool triage

**Honesty becomes UI wherever over-trust is possible:**

- Discover side: curiosity-framed ("explorers' leads, not gospel") — the cousins tag and
  the "one skeleton, several meanings" panel.
- Explore side: each advanced tool carries a one-line **caveat banner** stating its
  specific limit (heuristic extraction; uncalibrated confidence; genre-confounded
  frequency; unvalidated LLM cognates).
- A single shared **"How this works & what it can't do"** page, linked from both doors,
  consolidating the limitations (sourced from `docs/VALIDATION.md`).

**Triage of what exists today:**

| Disposition | Items |
|---|---|
| **Promote to Discover (front)** | Root Journey (new), reader, root-of-the-day, curated roots, meaning search, Discovery journeys (new) |
| **Keep under Explore, caveat banner** | visualizer, parallel viewer, concordance, hapax, PMI collocations, diachronic, paradigms, semantic fields, word parser, heatmap, API / Swagger |
| **Drop from the default experience (not deleted)** | "Cite this" citation-export modal and TEI export — they imply citability we are explicitly disclaiming as the headline; moved to a quiet corner of Explore |
| **Rename / reframe** | App identity → *Triliteral Aramaic Atlas*; tagline + homepage copy rewritten; sidebar regrouped Discover / Explore |

No repo rename, no DOI change — product framing only.

## 10. Data & reuse

- **Reused endpoints (no change):** `/api/roots`, `/api/root-family`,
  `/api/diachronic/root`, `/api/verse`, `/api/reverse-search`.
- **New data files:** `data/discovery/featured_roots.json` (hero grid + root-of-the-day
  pool), `data/journeys/*.json` (guided journeys).
- **New routes:** `/` (rebuilt Discover home), `/journey/<root_key>` (Root Journey),
  `/discover` (journeys shelf), `/how-it-works` (limitations page). Existing scholar
  routes unchanged except for added caveat banners and nav regrouping.
- **New templates + CSS:** Discover home, Root Journey, journeys shelf, how-it-works;
  caveat-banner partial; sidebar regroup in the shared layout.

## 11. Success criteria

- From a cold load of `/`, a user with no prior knowledge can reach a Root Journey and
  read the cross-script + timeline story without typing a root key.
- The Root Journey renders for any indexed root using only existing APIs.
- Every advanced tool shows its caveat banner; the homograph lesson and cousins
  disclaimer are present on the hero view.
- Existing scholar tools remain reachable and functional under Explore.
- No regression in the existing test suite.

## 12. Out of scope (explicit)

Validation studies, disambiguation algorithms, new corpora, accounts/persistence, repo
or DOI changes, the academic paper (parked separately).

## 13. Open questions (non-blocking)

- Exact curated set for the hero grid and root-of-the-day pool (content decision; can be
  filled during implementation).
- Whether journeys narration is authored by hand now or seeded and edited (default: hand
  for the launch 4–6).
- Visual treatment of the timeline strip (sparkline vs. full ribbon) — a design detail
  to settle when building the hero view.
