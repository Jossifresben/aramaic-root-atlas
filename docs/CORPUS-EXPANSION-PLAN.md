# Corpus Expansion Plan

> Detailed plan for growing the Aramaic Root Atlas from its current 5
> corpora to comprehensive coverage of the Aramaic literary tradition.
> Builds on Phase 6 of `docs/ROADMAP-v3.1.md`. Last updated 2026-05-10.

## Where we are today (v3.0.3)

5 corpora, **528,399 words**, **5,249 roots**:
Peshitta NT · Peshitta OT · Biblical Aramaic · Targum Onkelos ·
Hymns on Nisibis (Carmina Nisibena, ~5% of Ephrem's surviving works).

This is **Christian biblical and patristic Syriac** plus **a thin
sliver of Jewish biblical Aramaic and one Pentateuchal Targum**. It
does not include Talmudic Aramaic, the Palestinian Targums, Targum
Jonathan to the Prophets, ~95% of Ephrem's surviving corpus, Christian
Palestinian Aramaic, Mandaic, Samaritan Aramaic, Qumran Aramaic, or
the Imperial / Old Aramaic inscriptional record.

## The corpus universe — what's not yet indexed

| Corpus | Period | Approx. words | Script | Best digital source | License | Friction |
|---|---|---:|---|---|---|---|
| **Targum Jonathan to the Prophets** ✅ *added 2026-05-29* | 2nd–4th c. CE | 157,449 (actual; earlier ~290k estimate was high) | Hebrew square | Sefaria API | CC-BY-SA | Low |
| **Targum Pseudo-Jonathan** (Pentateuch) | 4th–8th c. CE | ~200,000 | Hebrew square | Sefaria API | CC-BY-SA | Low |
| **Targum Neofiti** (Pentateuch) | 1st–4th c. CE | ~180,000 | Hebrew square | Sefaria / CAL | mixed | Medium |
| **Cairo Geniza Targum fragments** | 9th–13th c. CE (mss) | ~30,000 | Hebrew square | Klein editions / CAL | varies | Medium |
| **Rest of Ephrem** (Hymns on Faith, Heresies, Paradise, Nativity, etc.) | 4th c. CE | ~500,000 | Syriac | Digital Syriac Corpus | CC-BY | Low |
| **Christian Palestinian Aramaic** (CPA) | 5th–13th c. CE | ~150,000 | CPA-Estrangela | DSC + Goshen-Gottstein | CC-BY (partial) | Medium |
| **Qumran Aramaic** (Targum Job, 1QapGen, 4QTobit, Enoch) | 3rd c. BCE–1st c. CE | ~40,000 | Hebrew square (Qumran) | DSSEL / Lim, García Martínez | restricted | Medium |
| **Imperial / Achaemenid Aramaic** (Elephantine, Aḥiqar, Bar-Rakib, Behistun) | 6th–4th c. BCE | ~100,000 | Imperial Aramaic | TAD (Porten-Yardeni) / CAL | restricted | Medium |
| **Jerusalem Talmud** (Galilean Aramaic) | 4th–5th c. CE | ~750,000 | Hebrew square | Bar-Ilan / Sefaria | restricted (BI), CC-BY-SA (Sefaria) | High |
| **Babylonian Talmud** (DJBA-aligned) | 5th–7th c. CE | ~2,500,000 | Hebrew square | Bar-Ilan / Sefaria / CAL | restricted (BI), CC-BY-SA (Sefaria) | High |
| **Old Aramaic inscriptions** (Tel Dan, Sefire, Zakkur, Bar-Rakib, KAI) | 9th–7th c. BCE | ~5,000 | Old Aramaic / Phoenician | KAI / TSSI / CAL | print | Medium |
| **Samaritan Aramaic** (Targum, Memar Marqah, hymns) | 4th–11th c. CE | ~100,000 | Samaritan script | Tal lexicon / CAL | print → digital partial | High (script) |
| **Mandaic** (Ginza Rabba, Book of John, Qulasta) | 3rd–8th c. CE (mss later) | ~250,000 | Mandaic script (U+0840–085F) | Drower-Macuch / Häberl | print → digital partial | High (script + lexicon) |

After Phase 6A+B, the Atlas grows from 5 corpora / 528k words to ~9
corpora / ~1.7M words. After all phases, ~16 corpora / ~5.5M words.

---

## Phased rollout

Each phase ships as its own minor version with its own Zenodo deposit,
so progress is incrementally citable.

### Phase 6A — Easy wins, ship as v3.1 (4–6 weeks of calendar time, ~5 days of focused work)

Reuses existing infrastructure: Sefaria fetch script, Hebrew-square
affix module, DSC TEI parser. No new alphabet, no new dialect module.

| # | Add | Source | Why first |
|---|---|---|---|
| 6A.1 ✅ | **Targum Jonathan to the Prophets** *(done 2026-05-29: 9,296v / 157,449w; roots 5,249→5,666; cognates 1,584→1,655 via Opus 4.8, ~$2)* | Sefaria API | Doubles Targum coverage; closes the most obvious gap |
| 6A.2 | **Rest of Ephrem** (~95% of his surviving works) | Digital Syriac Corpus | Removes the "Ephrem ≈ Carmina Nisibena" misnomer |

**Outcome:** 5 → 6 corpora (or 7 if we keep Ephrem-rest separate from
Carmina Nisibena). Words 528k → ~1,300k. Roots ~5,250 → ~6,800.

### Phase 6B — Targumic completion + Qumran, ship as v3.2 (1.5–2 months)

| # | Add | Source | Notes |
|---|---|---|---|
| 6B.1 | **Targum Pseudo-Jonathan** | Sefaria | Same Hebrew square pipeline |
| 6B.2 | **Targum Neofiti** | Sefaria + CAL alignment for missing books | Best-quality Palestinian Targum |
| 6B.3 | **Qumran Aramaic corpus** | Lim, García Martínez DSS reader; CAL has some | Small but huge for diachronic depth — pre-Christian Aramaic with secure dating |
| 6B.4 | **Cairo Geniza Targum fragments** (stretch) | Klein editions | Smaller but methodologically valuable |

**Outcome:** complete Targumic family + secure pre-Christian baseline.

### Phase 6C — Imperial / Old Aramaic + CPA, ship as v3.3 (2–3 months)

| # | Add | Source | Notes |
|---|---|---|---|
| 6C.1 | **Christian Palestinian Aramaic** | DSC + Goshen-Gottstein | Distinct dialect; needs lightweight CPA affix module |
| 6C.2 | **Imperial Aramaic** — Elephantine, Aḥiqar, Bar-Rakib, Behistun | TAD (Porten-Yardeni) — partially CAL | Pushes timeline back to 5th c. BCE; non-literary register |
| 6C.3 | **Old Aramaic inscriptions** (Tel Dan, Sefire, Zakkur, Hadad, KAI) | KAI / TSSI; CAL has digitized | Tiny corpus (~5k words), but anchors the chronology at 9th c. BCE |

**Outcome:** timeline now spans **9th c. BCE → 4th c. CE** (1,300 years
documented continuously). The "Atlas" framing is genuinely earned.

### Phase 6D — Talmudic corpora, ship as v3.4 (3–6 months)

The biggest payoff and the biggest engineering lift. The Babylonian
Talmud is the largest Aramaic corpus in existence; without it,
"Aramaic literature" is an overclaim.

| # | Add | Source | Notes |
|---|---|---|---|
| 6D.1 | **Babylonian Talmud (Bavli)** | Sefaria (CC-BY-SA, complete) or CAL (restricted) | ~2.5M words. Needs Babylonian Aramaic affix module. Performance: 2.5M words may need lazy loading or pre-computed inverted indices. |
| 6D.2 | **Jerusalem Talmud (Yerushalmi)** | Sefaria + Bar-Ilan; Sokoloff DJPA for lexicon alignment | ~750k words. Galilean Aramaic — distinct dialect. |

**Outcome:** the most comprehensive single index of Aramaic outside
CAL itself. JOSS submission becomes credible.

### Phase 6E — Stretch / decision-needed (v4.0 candidate)

| # | Add | Source | Why this is a separate decision |
|---|---|---|---|
| 6E.1 | **Samaritan Aramaic** | Tal lexicon; ASOR digitization efforts | Samaritan script (U+0800–U+083F) — needs new script module + Samaritan-Aramaic affix rules |
| 6E.2 | **Mandaic** | Drower-Macuch; Häberl | Mandaic script (U+0840–U+085F) — major engineering lift: new alphabet support throughout the stack, distinct dialect, separate lexicon |

These two require committing to multi-script infrastructure (no longer
just Syriac + Hebrew square). Worth doing only if institutional buy-in
exists (Phase 3.1 partner), since the engineering cost is comparable
to all of Phase 6A–C combined.

---

## Per-corpus engineering checklist

For each new corpus the work decomposes into:

1. **Data acquisition** — API fetch script in `scripts/fetch_<corpus>.py` (mirroring existing patterns)
2. **CSV emission** in our existing schema: `book,chapter,verse,word_id,form,transliteration,gloss,root,confidence,stem`
3. **Affix-stripping module** (`aramaic_core/affixes_<dialect>.py`) — only needed for distinct dialects (not for Targum-family which already uses Hebrew square)
4. **Lexicon coverage check** — does SEDRA / our cognate file cover this dialect? If no, generate via Claude API with explicit lexicon prompts (HALOT for Hebrew loans; DJBA for Babylonian; DJPA for Palestinian)
5. **Chronological positioning** — where does this corpus go in the diachronic ordering? (probably needs the editorial-chronology dropdown from Roadmap 2.9)
6. **Genre tag** — for the genre-control Phase 2.8 work
7. **UI label + 4-language i18n key**
8. **Test coverage** — paradigmatic-root regression, smoke tests on the new endpoints
9. **Docs:** `CHANGELOG.md` Data Changes entry, `docs/SOURCES.md` per-corpus section, `LICENSE-DATA.md` per-file licensing

For Phase 6A (Tier-1 corpora), this is roughly **3–5 days per corpus**.

For Phase 6D Bavli, it's likely **2–3 weeks** of focused work plus
performance + storage planning.

---

## Cost breakdown

Three categories: LLM API (Anthropic), engineering session time, and
infrastructure (Render). Hosting is already paid; the new spend is API.

### Pricing assumptions

All cost estimates below assume:

- **Prompt caching is enabled.** Every cognate-generation call shares
  ~1,700 tokens of preamble (system prompt + format spec + few-shot
  examples + HALOT/Wehr/Sokoloff lexicon snippets). Cached read is
  ~10× cheaper than fresh input on Sonnet, ~10× cheaper on Opus.
- Sonnet 4.6 for standard work; Opus 4.7 only where genuinely needed
  (under-documented dialects, affix-rule design, lexicon validation,
  non-triliteral disambiguation); Haiku 4.5 for bulk classification.
- "Engineering API" = my own session-time cost during integration
  (also Anthropic; mostly Sonnet). Heavily reduced by prompt caching
  across sessions.

Pricing (as of v4.7 release):

| Model | Input (regular) | Input (cached read) | Output |
|---|---:|---:|---:|
| **Opus 4.7** | $15/M | $1.50/M | $75/M |
| **Sonnet 4.6** | $3/M | $0.30/M | $15/M |
| **Haiku 4.5** | $1/M | $0.10/M | $5/M |

### Per-task LLM tier guidance

| Task | Recommended model | Why |
|---|---|---|
| **Standard cognate generation** (most Aramaic dialects) | Sonnet 4.6 | Good enough quality; ~5× cheaper than Opus |
| **Cognate generation for under-documented dialects** (Mandaic, Samaritan, Old Aramaic, Imperial) | **Opus 4.7** | Lexicon nuance + comparative-Semitic reasoning; Sonnet hallucinates more often here |
| **Affix-stripping rule design** for a new dialect (one-time per corpus) | **Opus 4.7** | Multi-step linguistic reasoning; few-shot from existing modules |
| **Cognate cross-validation against HALOT/BDB/Sokoloff** | **Opus 4.7** | Comparative lexicography; Sonnet over-confident |
| **Non-triliteral root disambiguation** (Phase 2.0) | **Opus 4.7** | Genuinely hard morphology; Sonnet errors compound |
| **Semantic-field classification** (already done this way) | Haiku 4.5 | Coarse categorical; bulk |
| **Gloss generation, fetch-script code, doc/CHANGELOG writing** | Sonnet 4.6 | Routine engineering |
| **Bulk yes/no validation** ("does this gloss match the Aramaic?") | Haiku 4.5 | Cheapest; high-volume |

### Per-cognate cost (with prompt caching)

Assumes ~1,700 tokens cached preamble + ~300 tokens fresh input per
call + ~500 tokens output:

| Model | Per cognate (no cache) | Per cognate (cached) | Savings |
|---|---:|---:|---:|
| Opus 4.7 | ~$0.067 | **~$0.045** | 33% |
| Sonnet 4.6 | ~$0.014 | **~$0.009** | 36% |
| Haiku 4.5 | ~$0.005 | **~$0.003** | 40% |

### Per-phase budget

Two columns: **Expected** is the realistic number with caching enabled
and everything working. **Risk-adjusted** adds ~50–100% buffer for
retries, dead-end debugging, regenerating one corpus, etc. Use
Risk-adjusted for budgeting; Expected for what you'll likely actually
spend.

| Phase | Words added | New roots est. | Cognate API (cached) | Engineering API (cached) | **Expected** | **Risk-adj.** |
|---|---:|---:|---:|---:|---:|---:|
| **6A** Tg Jonathan + rest of Ephrem | ~790,000 | ~1,800 | ~$25 | $10–25 | **$35–50** | **$85–135** |
| **6B** TgPJ + Neofiti + Qumran + Geniza | ~410,000 | ~700 (high TgO overlap) | ~$7 | $30–80 | **$40–90** | **$210–410** |
| **6C** CPA + Imperial + Old Aramaic | ~255,000 | ~2,000 | ~$36 | $100–300 | **$140–340** | **$554–1,554** |
| **6D** Babylonian Talmud + Yerushalmi | ~3,250,000 | ~6,000 | ~$90 | $200–600 (perf refactor included) | **$300–700** | **$1,635–3,135** |
| **6E** Samaritan + Mandaic | ~350,000 | ~2,500 | ~$113 (mostly Opus — sparse lexicon) | $300–800 | **$420–920** | **$1,667–3,167** |

### Cumulative scenarios

| Strategy | What you get | Expected (cached) | Risk-adjusted | Recurring hosting delta |
|---|---|---:|---:|---:|
| **6A only** (v3.1) | Closes loudest "thin slice" critique; doubles Targum coverage | **~$45** | ~$110 | $0 |
| **6A + 6B** (v3.2) | Full Targumic family + Qumran baseline | **~$110** | ~$415 | $0 |
| **6A → 6C** (v3.3) | Full Aramaic timeline 9th BCE → 4th CE; "Atlas" framing earned | **~$340** | ~$1,415 | $0 |
| **6A → 6D** (v3.4) | + Talmuds — most comprehensive Aramaic index outside CAL | **~$840** | ~$4,000 | +$18/mo (Pro → Pro Plus) |
| **6A → 6E** (v4.0) | + Mandaic + Samaritan; all major Aramaic literary traditions | **~$1,650** | ~$6,400 | +$18/mo |

> **Why expected ≪ risk-adjusted:** the original plan padded for the
> case where prompt caching is off, retries happen, and a full corpus
> needs regenerating. With caching enabled and clean execution, real
> spend is roughly **1/3** of the risk-adjusted figure. Budget at
> risk-adjusted; report actuals in CHANGELOG once each phase ships.

### Optional add-ons

| Item | Why | Cost |
|---|---|---|
| **Cognate audit (sample)** — Phase 2.4 — sample 5% of cognates against HALOT/BDB/Sokoloff with Opus | Closes C1.4 / C2.20 critique without auditing all entries | ~$300 (~80 sampled entries × heavy Opus prompts at $3.50 each) |
| **Full cognate audit** (all ~13,000 cognates after 6E) | "We validated every entry" claim becomes citable | ~$2,600 |
| **Non-triliteral root pattern classes** (Phase 2.0) | Closes C1.1 critique | ~$200 API + ~$300 engineering |
| **Gold-standard test set** (Phase 2.1) — 300 verses × ~$0.50 each in Opus-assisted hand-annotation tooling | Foundation for precision/recall publication; accelerates human review | ~$150 API + your time |
| **Bavli performance refactor** (SQLite indexes for 2.5M-word search) | Required by Phase 6D to keep page loads under 1s | ~$500–1,000 engineering API |

### Render hosting trajectory

| At end of phase | Total CSV bytes | RAM at startup | Render impact |
|---|---:|---:|---|
| Today (v3.0.3) | ~70 MB | ~600 MB | None (Pro = $7/mo, no change) |
| 6A | ~140 MB | ~900 MB | None |
| 6B | ~210 MB | ~1.1 GB | None |
| 6C | ~250 MB | ~1.3 GB | None |
| 6D (Bavli adds 2.5M words) | ~600 MB | ~2.5 GB | **May need Pro Plus** (~$25/mo) for headroom |
| 6E | ~700 MB | ~3 GB | Likely Pro Plus |

Net hosting delta after full expansion: **+$18/mo** (Pro → Pro Plus),
starting at Phase 6D.

---

## Decisions waiting for the author

| Decision | Why it matters | Suggested default |
|---|---|---|
| **Lump or split releases?** Ship Phase 6A as v3.1 alone, or wait for 6B and ship together? | Affects Zenodo deposit cadence and citability | v3.1 = Phase 6A (fast win); v3.2 = 6B; etc. Each corpus addition gets its own citable version. |
| **CAL collaboration?** CAL has the best digitized text for Imperial Aramaic + several Targums | Removes years of cleanup work; requires institutional handshake | Approach Steve Kaufman / HUC; tie to Phase 3.1 institutional anchor |
| **Bavli source: Sefaria or Bar-Ilan?** | Sefaria is CC-BY-SA and complete; Bar-Ilan has better critical apparatus but restricted | Start with Sefaria for v3.4; document Bar-Ilan as "future critical-edition layer" |
| **Mandaic in v4 or stretch goal?** | Multi-script infrastructure is a 2-month engineering lift | Defer until institutional partner; not v3.x |
| **Samaritan Aramaic?** | Smaller but still requires new script support | Cluster with Mandaic decision |
| **New dialect-classifier UI?** | The Atlas needs to expose "Christian Syriac" vs "Jewish Aramaic" vs "Imperial Aramaic" as a filter once corpora multiply | Add in v3.2 alongside Targum-family expansion |

---

## Risks & mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Sefaria API rate limits or breaking changes | Medium | High (blocks 6A.1, 6B.1, 6B.2, 6D.1, 6D.2) | Cache responses to disk on fetch; pin a snapshot date; document the snapshot in `SOURCES.md` |
| Bavli storage/perf at 2.5M words | High | Medium | Pre-compute inverted indices, lazy-load chapter content, consider SQLite for the search index |
| Lexicon hallucinations during cognate generation for new dialects | High | High (already a critique) | Mark all new cognates `unverified: true` until lexicographer review (per Phase 2.4 plan) |
| New affix modules introduce extraction regressions on existing corpora | Medium | High | The 197-test suite catches paradigmatic regressions; add per-corpus regression tests when each lands |
| Babylonian Aramaic vocalization differs from Syriac → bad stem inference | High | Medium | Disclose explicitly in `docs/VALIDATION.md`; consider stem-classifier disabled for Bavli initially |
| License confusion for new corpora | Medium | High (legal) | `LICENSE-DATA.md` per-file table updated with each addition; review by you before each release |
| Diachronic chronology gets contested as we add disputed-date corpora (Pseudo-Jonathan, Jerusalem Talmud) | High | Low (already disclosed) | Editorial-chronology dropdown (Roadmap 2.9) — let the user pick the dating school |

---

## Recommended first action

**Ship Phase 6A as v3.1.** Two corpora (Targum Jonathan + rest of
Ephrem) added by reusing existing fetch + parse infrastructure.
Roughly **a week of focused work** at **~$45 expected (~$110
risk-adjusted) in API cost**, assuming prompt caching is enabled
on the cognate-generation pipeline.
Talking points for the announcement:

- "Doubled Targum coverage with Targum Jonathan to the Prophets (~290k words)"
- "Indexed 95% more of Ephrem's surviving Syriac corpus (~500k words)"
- "Total: 6 corpora, ~1.3M words, ~6,800 roots"

That single release closes the loudest "thin slice" critique with
minimal risk and forms the template for 6B–6E.

---

*Living document. Update as phases ship. Last reviewed 2026-05-10
(cost section revised: prompt caching now an explicit assumption,
Expected vs Risk-adjusted columns added).*
