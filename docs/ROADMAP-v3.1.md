# Aramaic Root Atlas — Post-v3.0 Roadmap

> Living plan addressing the 47 critique items from the May 2026 review pass.
> Critique IDs: **C1.x** = first critique round; **C2.x** = second round.
> Effort scale: **S** = ½–2 days, **M** = 1–2 weeks, **L** = 1–2 months,
> **XL** = 2+ months. **D** = decision needed from author.

---

## Critical path (do first, in order)

These items either (a) carry legal/reputational risk that compounds with time
or (b) unblock everything else. Nothing else in the roadmap should ship before
**Phase 0** is complete.

### Phase 0 — Compliance & honesty hotfix (Week 1, 3–5 days)

| # | Item | Critique | Effort |
|---|---|---|---|
| 0.1 | **Resolve data-license incompatibility.** Move CC-BY-NC and CC-BY-SA datasets out of the Apache-2.0 source tree into `data/` with explicit per-file `LICENSE` and `NOTICE` files. Add a top-level `LICENSE-DATA.md` enumerating each corpus's license, attribution, and use restrictions. Update `README.md` § License to clarify code vs. data licensing. | C2.1, C1.9, C1.10, C2.16 | M |
| 0.2 | **Add `/privacy` page + cookie consent.** Disclose Google Analytics, name the property, link to Google's data-handling docs, provide opt-out. Add cookie consent banner (CC0 banner like Klaro or hand-rolled). Cite property `G-XWZC618EC4`. | C2.3 | S |
| 0.3 | **Pull or re-record the "Watch Video" walkthrough.** It currently shows the pre-redesign UI and is misleading. Take it down with placeholder ("video being updated for v3.0") until re-recorded. | C2.5 | S |
| 0.4 | **Add a prominent "Limitations & Caveats" page** at `/about#limitations`. Disclose: extraction error rates (label as unmeasured for now), LLM-generated cognates, scoring rubric is heuristic-not-empirical, translation track biases, hardcoded chronology debate, corpus selection is a sample not the whole tradition. | C1.21, C1.22, C2.11, C2.21 | S |
| 0.5 | **Credit dukhrana.com** in `README.md` § Data Sources and `docs/SOURCES.md` § Peshitta NT for the lineage of the NT digitization. | C2.2 | S |
| 0.6 | **Cite-modal URL fix.** `ctx.url` should default to the canonical deposit URL (`https://aramaic-root-atlas.onrender.com`), not `window.location.href`. Citations should reference the work, not the page the user happened to be on. | C2.23 | S |
| 0.7 | **Per-page `<title>` tags.** Replace generic `Aramaic Root Atlas` with `<Tool name> | Aramaic Root Atlas` for each page. Improves bookmarking, SEO, screen readers. | C2.24 | S |
| 0.8 | **Render hosting upgrade.** Move from free tier ($0, sleeps after 15 min idle) to Hobby tier (~$7/month, always-on). Document this in `README.md` § Hosting. | C2.22 | S, **D** |
| 0.9 | **Audit the guided Tour against v3.0 in all four languages.** The Tour was originally built for the old horizontal nav. Walk through every step in EN/ES/HE/AR; fix selectors that point at gone elements; verify RTL placement of Driver.js popovers. | C2.8 | S |

**Deliverable:** v3.0.1 patch release with legal compliance, honesty
disclosures, and basic credibility hygiene. No new features.

---

## Phase 1 — Truthful disclosure & quick wins (Weeks 2–4)

Things that materially raise the credibility ceiling without major engineering.

| # | Item | Critique | Effort |
|---|---|---|---|
| 1.1 | **Rebrand `binyan` → `stem` throughout the codebase, UI, API, and i18n.** Aramaic morphology uses *stems* (Pe'al, Pa'el, Aph'el…) not Hebrew *binyanim*. This is a single search-and-replace plus careful i18n updates. Optionally keep "binyan" as a tooltip for users who came in from Hebrew. | C1.6 | M |
| 1.2 | **Rename Ephrem corpus.** Display label: `Ephrem — Hymns on Nisibis (Carmina Nisibena)`. Disclose in `SOURCES.md` and `README.md` that this is ~5% of Ephrem's surviving works. | C2.13 | S |
| 1.3 | **Disclose Greek track caveat.** On the visualizer Greek-cognate panel, on `/api-docs`, and in `SOURCES.md`: clarify the direction (Peshitta NT translates from Greek; not all NT Greek↔Aramaic mappings are "cognates" — some are translation equivalents, some are Aramaisms in Greek). State that the Greek text is **SBLGNT (Holmes 2010, CC-BY-SA)**, not the more-cited NA28. | C1.5, C2.12 | S |
| 1.4 | **"Atlas" framing audit.** Either (a) commit to actually adding spatial data (manuscript provenance maps, dialect distribution overlays) or (b) reframe the tagline from "atlas" toward "concordance + visualizer." Decision needed. | C2.4 | S, **D** |
| 1.5 | **Add OpenGraph + Twitter Card meta tags** to `base.html`. Render preview when the URL is shared on Slack/Twitter/Bluesky. Custom OG image with the v3.0 sidebar UI hero. | C2.9 | S |
| 1.6 | **Add `robots.txt` and `sitemap.xml`** with all canonical URLs. Add Schema.org `SoftwareApplication` and `Dataset` JSON-LD to homepage and About page. Add Highwire / Dublin Core / BEPress citation meta tags so Zotero connector and Google Scholar pick the tool up. | C2.10 | S |
| 1.7 | **Document the "search by meaning" algorithm.** On `/about` and on the search page itself, explain ranking (TF-IDF over translation tracks? string match? embedding similarity?) and the translation-track basis (WEB/RV1909/WLC/Van Dyck). | C1.8, C2.11 | S |
| 1.8 | **CHANGELOG.md** with explicit "DATA CHANGES" entries per release. Every Zenodo deposit must have a change log entry that says exactly what changed in the indexed data (root counts, corpus boundaries, glosses revised, cognates added). Backfill v1.1→v3.0 from git history. | C2.7 | M |
| 1.9 | **Reposition the TipTopJar widget.** Move from README front and About page top-of-fold to a less prominent footer location. Keep it — but it shouldn't be the second thing institutional reviewers see. | C2.18 | S, **D** |
| 1.10 | **Replace "confidence score" labels.** Either (a) calibrate against a gold standard and use real probabilities, or (b) rename to **Heuristic Strength: A/B/C** so users don't mistake heuristic ratings for empirical probabilities. Phase 0 disclosed the issue; this implements the fix. | C1.2, C2.21 | M |
| 1.11 | **Honest cognate-count framing.** Reword "1,127+ cognate families" in README and About to "1,127 LLM-generated cognate entries pending lexicographic validation (see Limitations)." Until cognates are checked against authoritative lexicons, the prominent number stays caveated. | C1.4, C2.20 | S |

---

## Phase 2 — Validation foundations (Weeks 4–10)

The single biggest credibility gap. Must happen before any pitch to a JOSS-tier
journal or institutional collaborator.

| # | Item | Critique | Effort |
|---|---|---|---|
| 2.0 | **Treat non-triliteral roots as first-class.** Add explicit pattern classes for biliteral, geminate (`qll`), II-w/y hollow verbs, III-y, III-ʾ, and quadriliteral (`targem`, `parnes`) roots. Currently the extractor either force-fits these into CCC or labels them low-confidence; both are wrong. Update `aramaic_core/extractor.py` to emit a structural type alongside the root, and update the UI to display non-CCC roots correctly (e.g., `Q-W-M`, `Q-L-L`). | C1.1 | L |
| 2.1 | **Build a gold-standard test set.** Hand-annotate **300 verses** sampled across all five corpora (60 per corpus, stratified by frequency). For each token: correct lemma, root, stem, prefix/suffix decomposition. Use ETCBC's lemmatization where it overlaps, plus expert review where it doesn't. Store as `tests/gold/<corpus>/<book>_<ch>_<v>.tsv`. | C1.2, C2.14 | L |
| 2.2 | **Run extractor against gold set; publish precision/recall.** Add `scripts/eval_extractor.py` that reports per-corpus precision, recall, F1 for root extraction, stem classification, and prefix/suffix splitting. Publish results in a `docs/EVALUATION.md` and link from About. | C1.2, C1.13, C2.21 | M |
| 2.3 | **Sanity-check 10 paradigmatic roots end-to-end.** K-T-B (write), SH-L-M (peace), Q-D-SH (holy), B-R-K (bless), R-KH-M (love/mercy), T-W-B (return), Y-D-` (know), `-M-R (say), N-T-N (give), `-B-D (do/serve). For each: walk through every tool (root explorer, KWIC, diachronic, paradigm) and document expected vs. actual results. Fix the bugs found. | C2.14 | M |
| 2.4 | **Audit the 1,127 cognate entries.** For each, key it back to an authoritative lexicon entry: HALOT or BDB for Hebrew, Lane or Wehr for Arabic, Brockelmann or Sokoloff for Aramaic. Mark each entry with a `verified_in: <citation>` field or flag as `unverified: true`. Aim for ≥80% verification before claiming "1,127 cognates" without caveat. | C1.4, C2.20 | XL |
| 2.5 | **Calibrate confidence scoring.** Once gold set exists, regress current heuristic score against actual correctness rate. Either (a) publish a calibration curve so users can map score→probability, or (b) replace numeric score with discrete A/B/C tiers anchored to empirical ranges. | C1.2, C2.21 | M |
| 2.6 | **Write `tests/` properly.** Add: snapshot tests for root extraction on the gold set, regression tests for cross-script normalization, API contract tests for all 28 endpoints, smoke test for each tool page renders. CI on every push. | C1.12 | M |
| 2.7 | **Disclose recall floor vs published lexicons.** Compare your 5,039-root index against Brockelmann's *Lexicon Syriacum* (~7,000 Syriac roots), Sokoloff's *DJBA* (~6,000 BA roots). Publish a "Coverage" page showing what lemmas are *not* in the Atlas because they don't appear in the indexed corpora. | C1.17, C2.19 | M |
| 2.8 | **Genre-control the diachronic view.** Add a per-corpus genre tag (translation literature, narrative prose, liturgical poetry, court Aramaic) and a checkbox to filter or normalize for it. Add disclosure that raw frequency comparisons across genres confound style with chronology. | C1.7 | M |
| 2.9 | **Disclose chronology as editorial.** Replace the hard-coded chronological order with a dropdown: "Standard chronology (default)", "Late Targum Onkelos", "User-defined." Document the dating debates in a `/about#dating` section with cited references. | C1.14 | S |

**Deliverable:** v3.1 release with published evaluation metrics, calibrated
confidence labels, validated cognate subset, and a real test suite. This is
the version that becomes credible enough for a JOSS submission attempt.

---

## Phase 3 — Scholarly grounding (Months 2–4, runs in parallel with Phase 2)

People-and-relationships work. Slow because it's not coding.

| # | Item | Critique | Effort |
|---|---|---|---|
| 3.1 | **Recruit 1–2 named academic collaborators.** Target a Semitic studies / digital humanities scholar at one of: VU Amsterdam (ETCBC), Hebrew Union College (CAL), Beth Mardutho, Notre Dame, Leiden, Tübingen. Even an advisory role moves the credibility needle dramatically. Email pitch with the Phase-2 evaluation results in hand. | C1.11, C1.15, C2.17 | L, **D** |
| 3.2 | **Replace Targum Onkelos via Sefaria with Sperber's critical edition** (or another named, citable critical text). Document the editorial choice and any apparatus available. | C1.10 | M |
| 3.3 | **Document the Peshitta NT edition lineage.** Trace the BFBS text through dukhrana.com to specific BFBS edition (Pusey-Gwilliam? 1920?). Document what gets lost vs. the Mosul or Leiden critical editions. | C1.9, C2.2 | S |
| 3.4 | **External Hebrew/Arabic UI review.** Find one Hebrew-native and one Arabic-native scholar to walk through the RTL interface for an hour each. Capture bugs (BiDi, number formatting, punctuation directionality, mixed-script line breaks) and fix. | C1.18, C2.15 | M, **D** |
| 3.5 | **Submit to JOSS** once Phase 2 is complete. The paper.md is a starting point but needs: explicit methodology, evaluation results, statement-of-need that addresses why CAL/ETCBC/Dukhrana aren't enough, and named co-authors. | C1.11 | M, **D** |

---

## Phase 4 — Infrastructure & sustainability (Months 2–6)

| # | Item | Critique | Effort |
|---|---|---|---|
| 4.1 | **Real persistence for annotations + bookmarks.** Migrate from localStorage to a real backend (SQLite for solo users, Postgres on Render if accounts needed). Add export/import so users can move their data. Until accounts exist, ship a prominent "DATA IS LOCAL — EXPORT REGULARLY" notice on every annotation/bookmark action. | C1.19, C2.6 | L |
| 4.2 | **API versioning + stability contract.** Move all endpoints to `/api/v1/...`. Document deprecation policy (1-year minimum notice). Add response-shape tests so changes to schemas are intentional. | C1.16 | M |
| 4.3 | **Rate limiting + basic abuse protection.** Flask-Limiter or similar. 100 req/min/IP for the public API. Higher tier with token-based auth for institutional users. | C1.16 | S |
| 4.4 | **Accessibility audit.** Run axe-core on every page. Fix WCAG AA violations: color contrast, ARIA labels, keyboard navigation, focus rings, screen reader semantics for tables and visualizer. Document accessibility statement on `/about`. | (gap) | M |
| 4.5 | **Long-term hosting strategy.** Decide: stay on Render Hobby, or move to institutional hosting (university lab page) once Phase 3.1 has a partner. Even a static fallback (S3-hosted snapshot of the most-cited tool pages) protects against tool death. | C1.15, C2.25 | M, **D** |
| 4.6 | **Succession plan.** Write `docs/SUCCESSION.md` documenting: who has access to the Render account, the GitHub repo, the Zenodo deposit, the domain. Designate a "in case of bus" successor. Make GitHub repo accessible to the successor. Without this, the tool dies the day the maintainer steps away. | C2.25 | S |

---

## Phase 5 — Refactoring debt (Months 3–6, opportunistic)

Not blocking adoption, but compounds if ignored.

| # | Item | Critique | Effort |
|---|---|---|---|
| 5.1 | **Templates: extract the inline 4-language conditional pattern** `{% if lang == 'es' %}...{% elif lang == 'he' %}...{% endif %}` into a single `t()` helper or i18n filter. Currently every new feature requires 4 inline conditionals. | C1.18 | M |
| 5.2 | **Split `app.py`** into per-feature blueprints (`reader/`, `concordance/`, `diachronic/`, `api/`). Currently a single-file monolith. | (gap) | M |
| 5.3 | **Cite modal: fix BibTeX `@misc` → `@software`.** Match APA convention `[Computer software]` over `[Web application]`. SBL output should match SBL Press 2nd ed. §6.4.6 strictly (not approximate). | C1.20 | S |
| 5.4 | **GitHub `Cite this repository` validation.** Use a CFF validator to ensure CITATION.cff produces well-formed BibTeX. Fix license declaration in CFF to reflect mixed-license reality (after Phase 0.1). | C2.16 | S |

---

## Phase 6 — Corpus expansion (Months 6–12+)

This is the real growth path. Each addition is a meaningful research contribution
in its own right and removes the "thin slice" critique.

| # | Corpus | Provenance | Effort | Why this one |
|---|---|---|---|---|
| 6.1 | **Targum Jonathan to the Prophets** | Sefaria | L | Doubles Targum coverage; closes the obvious gap |
| 6.2 | **Targum Pseudo-Jonathan + Targum Neofiti** | Sefaria, CAL | L | Most expansive Pentateuchal Targums |
| 6.3 | **Qumran Aramaic** (Targum Job, Genesis Apocryphon, 1QapGen, 4QTobit) | DSS-Eb editions | L | Pre-Christian Aramaic, fills the gap between BA and Targum Onkelos |
| 6.4 | **Imperial Aramaic / Elephantine** | TAD (Porten-Yardeni) | L–XL | Pushes coverage to the 5th–4th c. BCE; non-literary corpus is methodologically valuable |
| 6.5 | **Babylonian Talmud** (Sokoloff DJBA-aligned) | CAL or Bar-Ilan | XL | Largest Aramaic corpus in existence; a real "Atlas" must include it |
| 6.6 | **Rest of Ephrem's corpus** (Hymns on Faith, Heresies, Paradise, Nativity, Letters) | Digital Syriac Corpus | L | Removes the "Ephrem ≈ Carmina Nisibena" misnomer |
| 6.7 | **Christian Palestinian Aramaic** | DSC, Goshen-Gottstein | L | Distinct dialect; fills a coverage hole |
| 6.8 | **Mandaic literature** (Ginza Rabba, Book of John) | Drower-Macuch | XL, **D** | Different alphabet — major engineering lift, but a real differentiator |
| 6.9 | **Old Aramaic inscriptions** (Tel Dan, Sefire, Bar-Rakib, Zakkur) | KAI, TSSI | M–L | Pushes start of timeline to 9th c. BCE |
| 6.10 | **Samaritan Aramaic** | Tal, Macuch | L | Relatively small but distinctive dialect |

After 6.1–6.5, the "5,039 roots across 5 corpora" headline becomes
"~15,000 roots across 12 corpora" — at which point the *Atlas* framing is
genuinely earned.

> **Critique mapping note:** Phase 6 collectively addresses C1.3 (the
> corpus selection is a thin slice of "Aramaic literature"). No single
> entry can fix that critique; the cumulative effect of 6.1–6.10 does.

---

## Items not in critique that surfaced while writing this

- **6.x research-tool requests.** Verb conjugation tables, noun pattern tables,
  syntactic queries (genitive constructions, construct chains, participle
  predicates). Many Aramaicists will ask for these next. Track in a separate
  features backlog.
- **CSV/TSV bulk export of the entire root index** so researchers can take a
  snapshot offline. Currently no way to dump the whole dataset. Cite the v3.0
  Zenodo deposit zip — but that's source code, not data.
- **Mobile experience.** v3.0 sidebar layout collapses awkwardly on phones.
  Not blocking adoption (no scholar reads in the field), but "open the app to
  check a verse on phone" is a legitimate use.
- **Data freshness signal.** When the user lands, show "Data version: v3.0,
  built 2026-05-08" so reproducibility is obvious.

---

## Decisions you need to make

These are points where I won't act without your input.

| ID | Question |
|---|---|
| 0.8 | Pay $7/mo for Render Hobby? (Easy yes, but technically a budget decision.) |
| 1.4 | Keep "Atlas" framing and add real geographic data, or rebrand? |
| 1.9 | Tip jar: keep visible, demote to footer, or remove entirely? |
| 3.1 | Which institutional partner to approach first? Email pitch ready? |
| 3.4 | Hebrew/Arabic reviewers: do you have candidates, or should I draft an outreach email? |
| 3.5 | JOSS submission target: end of Phase 2, or wait until Phase 3 partner is named? |
| 4.5 | Long-term hosting: stay solo on Render, or seek institutional anchor? |
| 6.8 | Mandaic: include in v4, or keep as stretch goal? Multi-script lift is significant. |

---

## Critical-path summary

- **Days 1–7:** Phase 0 (legal compliance + honesty hotfix). Ships as v3.0.1.
- **Weeks 2–4:** Phase 1 quick wins. Ships as v3.0.2 or rolls into v3.1.
- **Weeks 4–10:** Phase 2 validation work. Ships as v3.1 with eval results.
- **Months 2–4:** Phase 3 partner outreach (parallel with Phase 2).
- **Months 2–6:** Phase 4 infrastructure (parallel with Phase 3).
- **Months 3–6:** Phase 5 refactoring (opportunistic, between other work).
- **Months 6–12+:** Phase 6 corpus expansion (post-v3.1 credibility achieved).

The critical leverage point is **Phase 2 + Phase 3.1 together**: published
evaluation metrics + named academic collaborator. Either alone is insufficient;
both together is the moment this transitions from "interesting solo project"
to "tool real Aramaicists may cite."

---

*Living document; edit freely. Last updated 2026-05-09.*
