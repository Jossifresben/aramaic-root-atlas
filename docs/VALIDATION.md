# Validation, Coverage, and Methodological Caveats

This document collects every quantitative and methodological disclosure
about the Aramaic Root Atlas in one place. Researchers using the tool
for academic work should read this before drawing scholarly conclusions
from any of the analytics surfaces (concordance, diachronic, semantic
fields, etc.).

The companion roadmap [`docs/ROADMAP-v3.1.md`](ROADMAP-v3.1.md) tracks
when each gap below will be closed.

---

## 1. No precision/recall study has been published

The root-extraction pipeline (`aramaic_core/extractor.py`) is **rule-
based and statistical**, not machine-learned. Each extracted root
carries a heuristic confidence indicator (High / Medium / Low) that
reflects which extraction path produced it (lexicon match vs. affix
stripping vs. weak-letter expansion), **not** measured correctness
against a gold standard.

- **No precision number is published.** The fraction of "High"
  attributions that are actually correct under expert review is unknown.
- **No recall number is published.** The fraction of correct attributions
  that the system finds vs. misses is unknown.
- **The score is not calibrated.** A "0.84" reflects the rubric, not a
  probability. Two extractions with the same score may have very
  different correctness rates.

**Planned remediation:** Phase 2.1 of the roadmap is to hand-annotate
300 verses (60 per corpus, stratified by frequency) using ETCBC's
lemmatization where it overlaps and expert review where it doesn't,
then publish per-corpus precision, recall, and F1.

---

## 2. Recall floor: 5,249 roots vs. published lexicons

The Atlas indexes **5,249 root types** attested across its 5 corpora
(roughly 528,399 words). For comparison, published Aramaic lexicons
contain substantially more entries:

| Lexicon | Approximate root count | Coverage |
|---|---:|---|
| Brockelmann, *Lexicon Syriacum* | ~7,000 | Classical Syriac |
| Sokoloff, *Dictionary of Jewish Babylonian Aramaic* (DJBA) | ~6,000 | Babylonian Aramaic |
| Sokoloff, *Dictionary of Jewish Palestinian Aramaic* (DJPA) | ~3,500 | Palestinian Aramaic |
| Costaz, *Dictionnaire syriaque-français* | ~5,500 | Classical Syriac |
| CAL (Comprehensive Aramaic Lexicon) | tens of thousands across all dialects | All Aramaic dialects |
| **Aramaic Root Atlas v3.0+** | **5,249** | 5 specific corpora |

The Atlas's 5,249 reflects roots **attested in its specific 5 corpora**,
not a coverage ceiling for Aramaic generally. Roots present in the
Babylonian Talmud, Palestinian Targums, Mandaic, Christian Palestinian
Aramaic, the rest of Ephrem's surviving works, or Old/Imperial Aramaic
inscriptions are **not counted** because those corpora are not yet
indexed (see Phase 6 of the roadmap).

---

## 3. Diachronic comparisons confound genre with chronology

The diachronic view compares normalized frequencies across the 5
corpora in chronological order. This **does not isolate diachronic
change** because the corpora differ on multiple confounding axes
simultaneously:

| Axis | Across the 5 corpora |
|---|---|
| Genre | court narrative + apocalyptic prose (BA), literal Torah translation (TgO), translation literature (Peshitta NT/OT), liturgical poetry (Ephrem) |
| Register | scribal court Aramaic, halakhic translation, ecclesial translation, hymnic |
| Dialect | Imperial / Standard Late Aramaic / Classical Syriac / Babylonian-influenced Syriac |
| Translation source | none / Hebrew / Greek / none |
| Period | ~6th-2nd c. BCE / 1st-3rd c. CE / 2nd-5th c. CE / 4th c. CE |

A root frequency that appears to "rise" or "fall" across the
chronological axis may reflect any of these other factors. Concretely:
the high frequency of *brk* (bless) in Ephrem's hymns reflects
**liturgical genre**, not historical drift in the use of "bless."

**Recommendation for users:** Treat diachronic charts as
**suggestive starting points**, not as evidence for diachronic claims.
For substantive arguments about lexical change over time, control for
genre, register, and translation source before drawing conclusions.

**Planned remediation:** Phase 2.8 of the roadmap is to add per-corpus
genre tags and a UI control to filter or normalize for genre, plus
a banner-style disclosure on the diachronic page.

---

## 4. Chronology is editorial, not consensus

The chronological ordering displayed in the diachronic view is:

> Biblical Aramaic → Targum Onkelos → Peshitta NT → Peshitta OT → Ephrem of Nisibis

This reflects an editorial choice. **Several of these dates are
debated** in the scholarly literature:

- **Targum Onkelos** dating spans 1st–5th c. CE depending on which
  redactional layer is treated as definitive. Some scholars date the
  final form as late as the 5th c. CE (later than the Peshitta NT).
- **Peshitta OT** was redacted between the 2nd and 4th c. CE, with
  individual books showing earlier or later strata.
- **Peshitta NT** translation was complete by the early 5th c. CE
  (Rabbula), but earlier Old Syriac strata exist (Curetonianus,
  Sinaiticus).

Users who disagree with the standard ordering should interpret the
diachronic charts accordingly. We document the editorial choice
prominently rather than hide it.

**Planned remediation:** Phase 2.9 of the roadmap is to expose
chronology as a user-selectable preference (Standard / Late TgO /
User-defined) and add an explicit disclosure of the dating debate
on the about page.

---

## 5. Cognates are LLM-generated and unvalidated

The 1,584 Hebrew/Arabic cognate root entries and the 405 Greek NT
cognate entries in `data/roots/cognates.json` were generated using
the Anthropic Claude API and have **not been systematically validated**
against authoritative lexicons:

- **Hebrew:** HALOT (Koehler-Baumgartner-Stamm), BDB (Brown-Driver-Briggs)
- **Arabic:** Lane, Wehr (Hans Wehr Modern Standard Arabic)
- **Aramaic:** Sokoloff DJBA, Sokoloff DJPA, Brockelmann
- **Greek NT:** BDAG (Bauer-Danker-Arndt-Gingrich)

LLM-generated cognates can include:
- Phonologically plausible but historically unrelated forms (false
  cognates / paronomasia)
- Real cognates with incorrect or oversimplified glosses
- Direction-confused entries (e.g. Greek translation equivalents
  presented as Aramaic-to-Greek "cognates" when the Peshitta NT is
  in fact a translation **from** Greek)
- "Semantic bridges" with no published etymological basis

**Use cognates as starting points for verification, not as
authoritative claims.**

**Planned remediation:** Phase 2.4 of the roadmap is to systematically
audit each entry against the relevant lexicon, marking each with a
`verified_in: <citation>` field or `unverified: true` flag. Target:
≥80% verification before claiming "1,584 cognate root entries" without caveat.

---

## 6. Triliteral framing is a poor fit for non-CCC roots

The extraction engine forces a triliteral (CCC) shape onto every word.
This is a poor fit for the actual morphology of:

- **Geminate verbs** (e.g. *qll* "to be light"; *bzz* "to plunder")
- **II-w/y hollow verbs** (e.g. *qwm* "to rise"; *šym* "to place")
- **III-w/y weak verbs** (e.g. *bnh*/*bny* "to build")
- **III-ʾ verbs** (e.g. *brʾ* "to create")
- **I-ʾ verbs** (e.g. *ʾmr* "to say")
- **Quadriliteral verbs** (e.g. *targem* "to translate"; *parnes* "to provide")

Currently these forms either:
- Get force-fit into a CCC pattern with an inserted weak letter, or
- Receive a "Low" confidence score and may be silently mis-extracted.

**Planned remediation:** Phase 2.0 of the roadmap is to add explicit
non-triliteral pattern classes to `aramaic_core/extractor.py`, so
geminate, hollow, weak, and quadriliteral roots are first-class
citizens with their own correct surface representations.

---

## 7. Stem (binyan) classification is genuinely ambiguous

Aramaic stem classification (Pe'al, Ethpe'el, Pa'el, Ethpa'al, Aph'el,
Shaph'el, Ettaph'al) requires vocalization or syntactic context that
**is often unavailable** in the consonantal text the Atlas processes.

Consequence: many word forms could plausibly be classified as multiple
stems, and the badge displayed in the UI represents a best-effort
guess, not a determinate classification.

**Use stem badges as priors**, not ground truth. For arguments that
depend on a specific stem (e.g. "this verb is Pa'el here, not Pe'al"),
verify against vocalized manuscript witnesses or specialist
commentaries.

---

## 8. Translation tracks introduce silent translator bias

The reverse-search ("Search by meaning") and full-text search modes
search **translations**, not the original Aramaic. Translation tracks
used:

| Language | Edition | Year | Notes |
|---|---|---:|---|
| English | World English Bible (WEB) | derived from ASV 1901 | Public domain |
| Spanish | Reina-Valera | 1909 | Public domain; archaic Spanish |
| Hebrew | Westminster Leningrad Codex (WLC) | electronic | Primary text for Biblical Aramaic |
| Arabic | Smith-Van Dyck | 1865 | Public domain; archaic Arabic |
| Greek (NT) | SBLGNT (Holmes) | 2010 | CC-BY-SA; not the more-cited NA28 |

A search for "love" in English ranks roots whose **WEB gloss** literally
contains "love." Roots glossed as "compassion" or "mercy" by WEB may
rank lower despite being semantically closer to the underlying Aramaic.
Reina-Valera 1909 reflects 19th-century Reformed translation choices.
SBLGNT differs from NA28 in roughly 540 places.

**Recommendation:** for substantive semantic claims, cross-check
against multiple translation traditions and against the Aramaic
attestations directly (root family page → occurrences tab).

---

## 9. localStorage data is ephemeral

Researcher annotations, bookmarks, tags, and settings are stored in
the browser's localStorage. They are **lost** when:
- The user clears their browser cache
- The user switches browsers or devices
- The user uses Private/Incognito browsing
- The OS migrates / browser is reinstalled

**Use the JSON / CSV / Markdown export functions regularly** to back
up annotations and bookmarks. A real account / sync system is on the
roadmap (Phase 4.1).

---

## 10. Greek "cognates" are direction-aware

The 405 Greek NT parallel entries link Aramaic roots to single Greek
equivalents (one Greek word per root max). Two distinct relationships
are conflated under "cognate":

1. **Translation equivalents** — the Peshitta NT translates *from*
   Greek, so an Aramaic word like *šlm* corresponds to *eirēnē* in
   the same context. This is a translation-pair relationship, not
   etymological cognate-ship.
2. **Aramaisms in the Greek NT** — transliterated terms like *rabbi*,
   *talithā kūm*, *maranatha* are genuine Aramaic in the Greek source.
   These are the only true Greek↔Aramaic cognate-ish pairs.

The current cognate-data structure does not distinguish these. Users
should treat the Greek field as a **translation hint** rather than as
an etymological claim, except for the Aramaism cases (which are easy
to spot as transliterated rather than translated terms).

---

## 11. Corpus selection is a thin slice of "Aramaic literature"

The 5 indexed corpora cover roughly:

- Christian biblical and patristic Syriac (Peshitta NT, Peshitta OT,
  Hymns on Nisibis)
- Jewish Aramaic biblical material (Daniel, Ezra) and one Pentateuchal
  Targum (Onkelos)

**Not yet indexed:**
- Babylonian Talmud (the largest Aramaic corpus by volume)
- Jerusalem Talmud (Galilean Aramaic)
- Targum Pseudo-Jonathan, Targum Neofiti, Cairo Geniza Targum fragments
- Targum Jonathan to the Prophets
- ~95% of Ephrem's surviving works (Hymns on Faith, Heresies, Paradise,
  Nativity, etc.)
- Christian Palestinian Aramaic
- Mandaic literature
- Samaritan Aramaic
- Qumran Aramaic (Targum Job, 1QapGen, 4QTobit, etc.)
- Imperial / Achaemenid Aramaic (Elephantine, Persepolis)
- Old Aramaic inscriptions (Tel Dan, Sefire, Bar-Rakib, Zakkur)

Calling the current 5 corpora "the major corpora of Aramaic literature"
overstates coverage. **A more accurate framing**: the Atlas indexes
**a representative biblical-and-patristic slice** of Aramaic.

**Planned remediation:** Phase 6 of the roadmap is corpus expansion,
prioritizing Targum Jonathan to the Prophets, Qumran Aramaic, the
rest of Ephrem, and the Babylonian Talmud.

---

## 12. The number "5,249 roots" — what to make of it

The README front-page sticker "5,249 roots" is a count of distinct root
keys that survived extraction across the 5 corpora. It is:

- **Lower-bound, not authoritative.** Real roots may be missing if
  every attestation in the indexed corpora was mis-extracted
  (false negatives are not measured — see §1).
- **Inflated by extraction errors.** A 65% false-positive rate on
  candidate root patterns was reported in the original cognate-
  generation pass (1,127 cognates from 3,212 candidate patterns;
  2,085 candidates rejected as non-roots). The current 5,249 number
  includes some surviving noise that hasn't been pruned.
- **Not a coverage claim.** Compare to ~7,000 in Brockelmann's
  Syriac-only lexicon (§2).

The number is a **fact about the index**, not a claim about Aramaic.
Treat as such.

> **Note (2026-05-09 reconciliation):** earlier release docs cited
> "5,039 roots" — that number was from the v3.0 release and stale by
> v3.0.3. Live `/api/stats` returns 5,249. The increase reflects new
> cognate generation that surfaced additional roots without changing
> the underlying corpus. Earlier docs also overcounted Greek NT
> cognates as "2,192" — actual count is 405 (one Greek word per root
> at most). All current-state references have been corrected.

---

*Last updated: 2026-05-09. Maintained alongside `CHANGELOG.md` —
when validation work in Phase 2 lands, this document will be updated
with measured precision/recall numbers and the corresponding entries
will move from "planned" to "delivered."*
