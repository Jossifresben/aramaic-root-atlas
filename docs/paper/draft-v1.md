# The Aramaic Root Atlas: A Cross-Script Concordance for Eight Aramaic Corpora

**Jose Fresco Benaim**
Independent Researcher
ORCID: [0009-0000-2026-0836](https://orcid.org/0009-0000-2026-0836)

Concept DOI: [10.5281/zenodo.19358625](https://doi.org/10.5281/zenodo.19358625)
Live application: <https://aramaic-root-atlas.onrender.com>
Source code: <https://github.com/Jossifresben/aramaic-root-atlas>

---

## Abstract

The Aramaic Root Atlas is an open-source web application and JSON API that lets a researcher type one consonantal root and instantly see every occurrence of it across eight Aramaic corpora spanning roughly 1,400 years — without doing the script normalization or cross-corpus stitching by hand. It indexes 55,710 verses and 859,016 words drawn from the Peshitta New Testament, the Peshitta Old Testament, the Biblical Aramaic of Daniel and Ezra, Targum Onkelos, Targum Jonathan to the Prophets, the Targums to the Writings, and the works of Ephrem the Syrian (the *Hymns on Nisibis*, the Nativity hymns, and the prose refutations). Texts written in Syriac script and texts written in Hebrew square script are reduced to a single canonical consonantal key, so that Syriac ܫܠܡ, Hebrew שלם, and the transliteration `SH-L-M` all resolve to the same root and return a unified, cross-corpus attestation table. Across these corpora the Atlas indexes 6,061 distinct roots. Around that lookup it provides a keyword-in-context concordance with academic export, a hapax legomena finder, PMI collocations, verb-stem (binyan) paradigm tables, a root-family graph, a parallel viewer, semantic-field tags, and a fully versioned REST API documented with an OpenAPI 3.0.3 specification. The interface is quadrilingual (English, Spanish, Hebrew, Arabic) with right-to-left support. The Atlas is not a lexicon and makes no lexicographic claims; it is a convenience layer over corpora that already exist in scattered, mutually incompatible forms. This paper describes the resource, walks through three concrete uses, and states its limitations plainly. [CITE: Zenodo concept DOI 10.5281/zenodo.19358625]

---

## 1. Statement of need

Aramaic literature survives in many corpora, in at least two scripts, under at least four licenses, behind as many different interfaces. The Peshitta Old Testament lives in the ETCBC linguistic database and is queried through Text-Fabric tooling [CITE: ETCBC Peshitta / Text-Fabric]. Syriac lexical data lives in SEDRA at Beth Mardutho [CITE: Kiraz, SEDRA]. The Comprehensive Aramaic Lexicon (CAL) covers the dialect spread but in its own transliteration and its own query model [CITE: CAL]. Biblical Aramaic and the Targums are most easily reached through Sefaria, in Hebrew square script [CITE: Sefaria]. Ephrem's hymns are TEI XML files in the Digital Syriac Corpus [CITE: Digital Syriac Corpus]. A scholar who simply wants to know *where a given root occurs across all of these* must visit each resource in turn, translate the root into each one's input conventions, mentally normalize Syriac script against Hebrew square script so the "same" root is recognized as the same, reconcile incompatible reference formats, and tabulate the result by hand. None of that work is intellectually interesting; all of it is error-prone; and it must be repeated for every root. The Aramaic Root Atlas exists to do that stitching once, in software, so the answer to "where does √šlm occur across eight Aramaic corpora?" is a single query rather than an afternoon.

## 2. Resource description

### 2.1 Corpora

The Atlas indexes eight corpora totalling 55,710 verses and 859,016 words. Each is loaded from a CSV file in the repository and retains its native script. The corpora and their bundled licenses are:

| Corpus | Verses | Words | Script | Source | Data license |
|---|---:|---:|---|---|---|
| Peshitta New Testament | 7,440 | 101,469 | Syriac | BFBS Peshitta (via dukhrana.com, SEDRA) | Public domain |
| Peshitta Old Testament | 23,072 | 309,889 | Syriac | ETCBC / Leiden Peshitta Institute | CC-BY-NC |
| Biblical Aramaic | 269 | 4,880 | Hebrew square | Westminster Leningrad Codex via Sefaria | CC-BY-SA |
| Targum Onkelos | 5,846 | 82,684 | Hebrew square | Sefaria | CC-BY-SA |
| Targum Jonathan | 9,296 | 157,449 | Hebrew square | Sefaria | CC-BY-SA |
| Targums to the Writings | 7,022 | 96,169 | Hebrew square | Sefaria | Public domain |
| Ephrem, *Hymns on Nisibis* | 1,435 | 29,477 | Syriac | Digital Syriac Corpus | CC-BY |
| Ephrem, other works | 1,330 | 76,999 | Syriac | Digital Syriac Corpus | CC-BY |
| **Total** | **55,710** | **859,016** | | | |

The corpora span from the Biblical Aramaic of Daniel and Ezra (composed in the Achaemenid-to-Hellenistic window) through the Jewish Aramaic Targums and the Christian Syriac of the Peshitta and Ephrem (late antiquity), with the Targums to the Writings extending the arc into the early medieval period — about 1,400 years of attested usage. Because the source licenses differ, the repository licenses code and data separately: the source code is Apache-2.0, and each corpus file carries the license of its upstream provider (see §6). The most restrictive bundled term is CC-BY-NC on the Peshitta OT, which downstream reusers must respect per file.

### 2.2 Cross-script root normalization

The keystone feature is that Syriac-script and Hebrew-square-script texts are reduced to one shared root key. A word is routed by per-word script detection to a script-appropriate affix stripper, reduced to its consonantal skeleton, and — for Hebrew-square roots — mapped onto the corresponding Syriac consonants so that a single canonical key is produced. The practical consequence is that Syriac ܫܠܡ from the Peshitta and Hebrew שלם from Targum Jonathan are recognized as occurrences of the *same* root and counted together. Root input is equally script-agnostic: the lookup accepts dash-separated Latin transliteration (`SH-L-M`), bare Latin (`SHLM`), Syriac Unicode (ܫܠܡ), Hebrew (שלם), or Arabic (سلم), auto-detecting and normalizing each to the canonical key. This is the manual step the resource removes: the user never has to decide whether two graphically different strings denote the same root, because the index already did.

### 2.3 Features

Around the cross-corpus lookup, the Atlas provides:

- **Root explorer** — one query returns all attested word forms with per-form frequency, a cross-corpus attestation table (counts per corpus), English/Spanish glosses, Hebrew and Arabic cognates, Greek New Testament parallels, and the root rendered in each script in which it is attested.
- **KWIC concordance** — every attestation of a root in a configurable left-context | keyword | right-context layout, groupable by word form or verb stem, with export to CSV, JSON, plain text, and TEI XML.
- **Hapax legomena finder** — roots and forms filtered by attestation count (1–5 occurrences) per corpus or across the whole collection.
- **PMI collocations** — pointwise mutual information for roots co-occurring within the same verse or chapter, surfacing statistically salient lexical pairings.
- **Root-family visualizer** — a D3.js force-directed graph of a root's word forms, cognates, sister roots (sharing two of three consonants), and semantic bridges.
- **Verb-stem (binyan) paradigm tables** — word forms classified into Peal, Ethpeel, Pael, Ethpaal, Aphel, Shafel, and Ettaphal, with per-root stem distributions.
- **Parallel viewer** — texts from different corpora covering the same passage placed side by side; this includes synoptic comparison of the Peshitta Old Testament against the Jewish Aramaic Targums across the Prophets (Targum Jonathan) and the Writings — Psalms, Job, Proverbs, the Megillot, and Chronicles (Targums to the Writings).
- **Semantic-field tags** — every root assigned to one of fifteen coarse semantic domains (legal/covenant, cultic, kinship, war, knowledge, and so on).
- **Passage tools** — a lexical profile (unique roots, lexical density, hapax counts, stem distribution, per-verse density) for any book-and-chapter range, and a passage "constellation" graph of the roots in a selected span.
- **REST API** — every analytical surface is reachable as JSON. Endpoints are documented with an interactive Swagger UI at `/api-docs` and a complete OpenAPI 3.0.3 specification at `/static/swagger.json`. Every `/api/X` path is also served at `/api/v1/X` under a published versioning policy, and responses carry `X-RateLimit-*` headers.
- **Quadrilingual UI** — the full interface (navigation, buttons, table headers, tool pages) is localized in English, Spanish, Hebrew, and Arabic, with right-to-left layout for Hebrew and Arabic. Five reader translation tracks are available (WEB, Reina-Valera 1909, WLC, Van Dyck, SBLGNT).

The Atlas additionally indexes 1,642 Hebrew/Arabic cognate root entries and 405 Greek New Testament parallels, and queries the SEDRA Syriac lexicon as a secondary signal when scoring Syriac extractions. The honest status of the cognate layer is stated in §5.

## 3. Three uses

### 3.1 A lexicographer's day: one root, eight corpora, one screen

A lexicographer is writing the entry for √šlm and needs the distribution of the root across the traditions she works in. She opens the Atlas and types `SH-L-M` into the root box. One screen comes back. At the top, the root is shown in every script in which it is attested — Syriac ܫܠܡ and Hebrew שלם — with a note that both resolve to the canonical key `sh-l-m`. Below it, a cross-corpus attestation table gives the count in each of the eight corpora at once: the Peshitta NT and OT in Syriac, Biblical Aramaic, Targum Onkelos, Targum Jonathan, and the Targums to the Writings in Hebrew square, and Ephrem's hymns and prose works. She does not transliterate the root eight times, does not switch tools when she crosses from Syriac into Hebrew square, and does not reconcile the result by hand — the columns are already aligned on one key. Beside the table she sees the attested word forms ranked by frequency, the Hebrew and Arabic cognates (and, for roots that have one, a Greek New Testament parallel), and a one-click path into the KWIC concordance to read each occurrence in context. The afternoon of manual collation described in §1 has become a single look at a single page.

### 3.2 Nine manual steps versus one API call

Consider the same question — *the cross-corpus distribution of √šlm* — answered the old way and the Atlas way.

**The manual way, before the Atlas:**

1. Open CAL and search the root in CAL's transliteration scheme.
2. Switch to SEDRA / Beth Mardutho for the Syriac attestations, entering the root in Syriac script through a different interface.
3. For the Peshitta Old Testament, query the ETCBC database through its own Text-Fabric tooling.
4. For Biblical Aramaic, switch again to a Hebrew-script resource (Sefaria), because the script is different.
5. For the two Targums, query Sefaria separately, in Hebrew square script.
6. For Ephrem, locate the relevant Digital Syriac Corpus TEI XML and search the files directly.
7. Manually normalize across scripts so that Syriac ܫܠܡ and Hebrew שלם are treated as one root.
8. Reconcile the differing reference and citation formats and de-duplicate overlapping hits.
9. Tabulate the per-corpus counts by hand.

**The Atlas way:**

```bash
curl 'https://aramaic-root-atlas.onrender.com/api/v1/roots?q=SH-L-M'
```

The response is JSON containing, among other fields, a `corpus_attestation` object keyed by corpus identifier (`peshitta_nt`, `peshitta_ot`, `biblical_aramaic`, `targum_onkelos`, `targum_jonathan`, `targum_writings`, `ephrem_nisibis`, `ephrem_works`) with the occurrence count in each; a `matches` array of the attested word forms with their transliterations, per-form counts, sample references, and glosses; the `root_scripts` in which the root is attested; and the `root_display` forms in each script. The nine steps collapse into one call whose output is already cross-script-normalized and already tabulated per corpus. [CITE: live API response — capture exact JSON for √šlm at submission time]

### 3.3 Downstream reuse: the Atlas as a data source for another project

Because every analytical surface is exposed as versioned JSON, the Atlas can feed other software rather than only serving human readers. Suppose a researcher building a separate study of translation technique wants, for a list of a few hundred roots, the per-corpus frequencies and the Greek New Testament parallel where one exists. Rather than scraping pages, they iterate their root list against `/api/v1/roots?q=<root>` and read `corpus_attestation` and the Greek field directly out of each response; for context windows they call `/api/v1/concordance?root=<root>`, and for normalized cross-corpus frequencies in chronological order they call `/api/v1/diachronic/root?root=<root>`. The OpenAPI 3.0.3 specification at `/static/swagger.json` lets them generate a typed client; the `/api/v1/` prefix gives them a stability contract so their pipeline does not break on the next release; and the `X-RateLimit-*` headers tell their client how to pace itself. The Atlas thus functions as a small reusable Aramaic data service, not only as a website. [CITE: OpenAPI spec at /static/swagger.json]

## 4. Figures

![The root explorer for √šlm, showing the canonical-key header, eight corpus attestation badges, and the occurrences table.](figures/fig1-shlm-root-explorer.png)

**Figure 1.** *The root explorer for √šlm (`SH-L-M`) — one root in, every corpus out, already aligned on one key.* The header renders the root in every script in which it is attested — Syriac ܫܠܡ and Hebrew square שלם — beside the canonical Latin key `SH-L-M`, making the cross-script unification visible at a glance. Immediately below, a row of eight corpus attestation badges gives the occurrence count in each indexed corpus at once: Biblical Aramaic (11×), Ephrem Nisibis (34×), Ephrem — Other Works (66×), Peshitta NT (315×), Peshitta OT (50×), Targum Jonathan (740×), Targum Onkelos (288×), and Targum Writings (496×) — the counts sum to the 2,000 total shown on the *Occurrences* tab. The occurrences table lists each attested word form (in both Syriac and Hebrew square script — e.g. ܫܠܡ *shlm* "peace," שלמה *shlmh* "peace, complete," ܒܫܠܡ *bshlm* "in peace") with its transliteration, gloss, and the full reference list spanning all eight corpora, exportable as CSV. This single page is the answer to the question that §1 described as an afternoon of manual collation.

![Continuation of the √šlm occurrences table, showing additional attested word forms across corpora and scripts.](figures/fig1b-shlm-occurrences-cont.png)

![Further √šlm word forms with glosses and cross-corpus references.](figures/fig1c-shlm-occurrences-forms.png)

**Figures 1b–1c.** *Scrolling the same occurrences table.* The √šlm entry resolves to some 300 distinct attested word forms across the eight corpora, in both scripts, each linked to its full reference list. These continuation views illustrate that the cross-corpus alignment is not a summary count but a fully enumerated, navigable concordance: every form, every reference, on one key.

![The Hebrew Cognates tab for √šlm.](figures/fig2-shlm-hebrew-cognates.png)

![The Arabic Cognates tab for √šlm.](figures/fig3-shlm-arabic-cognates.png)

**Figure 2 (a–b).** *Comparative-Semitic cognates for √šlm — Hebrew and Arabic tabs.* The same corpus-badge header persists while the user switches to the Hebrew and Arabic cognate tabs. The Hebrew tab lists שָׁלוֹם *shalom* "peace," שָׁלֵם *shalem* "complete," שִׁלֵּם *shilem* "to pay," and שְׁלִימוּת *sh'limūt* "wholeness, integrity"; the Arabic tab lists سَلَام *salām* "peace," إِسْلَام *islām* "submission/Islam," مُسْلِم *muslim* "Muslim," سَلِيم *salīm* "sound, complete," تَسْلِيم *taslīm* "surrender, delivery," and سَلَامَة *salāmah* "safety, integrity." This comparative layer is convenient but, as stated in §5, **LLM-generated and not yet verified against authoritative lexicons** — it surfaces candidate cognates for the reader to check, not adjudicated etymologies.

![The Root Card for √šlm: key verse, stem distribution, paradigm table, and diachronic-analysis bars.](figures/fig4-shlm-root-card.png)

**Figure 3.** *The Root Card for √šlm.* A second view of the same root assembles the analytical surfaces on one card: a **key verse** (2 Samuel 12:24 in the Targum, with שלמה highlighted and the gloss "…She bore a son, and he called his name Solomon"); a **stem distribution** bar chart (Peal 174×, Aphel 187×) with an expandable **paradigm table** grouping the attested forms by verb stem (Aphel 41 forms, Peal 32 forms); and a **diachronic-analysis** panel showing the per-corpus frequency as horizontal bars in chronological order (Biblical Aramaic 11, Targum Onkelos 288, Targum Jonathan 740, Peshitta NT 315, Peshitta OT 50, Ephrem — Nisibis 34, Ephrem — Other Works 66, Targum Writings 496). The diachronic bars make the cross-corpus distribution legible at a glance — though, per §5, such comparisons confound genre and register with chronology and should be read as suggestive, not evidential.

> *Figures captured against the live v3.3.0 application, 2026-07-12 (root explorer and root card for `SH-L-M`, all eight corpus badges visible). Source images: `docs/paper/figures/`.*

## 5. Honesty: what this resource is not

This section is placed in the body, not an appendix, because the limitations bound what the resource may be cited for.

- **The cognate layer is LLM-generated and unverified.** The 1,642 Hebrew/Arabic cognate root entries and the 405 Greek New Testament parallels were generated with a large language model and have *not* been systematically checked against authoritative lexicons (HALOT, BDB, Sokoloff DJBA/DJPA, Brockelmann, Lane, Wehr, BDAG). They are flagged unverified and should be treated as leads for verification, not as cognate claims. [CITE: docs/VALIDATION.md §5]
- **Confidence tiers are heuristic, not calibrated.** Each extraction carries a High / Medium / Low indicator reflecting which extraction path produced it, not a measured probability of correctness. A displayed score is a rubric output, not an empirical accuracy figure.
- **No published benchmark.** No precision/recall study against a hand-annotated gold standard has been published. The fraction of correct extractions, and the fraction the system misses, are not yet measured.
- **The corpus is a biblical-and-patristic slice, not "Aramaic literature."** The eight corpora cover Christian biblical/patristic Syriac plus Jewish biblical Aramaic and the Targumic family (Onkelos, Jonathan, and the Writings). The Babylonian and Jerusalem Talmuds, the Palestinian Targums, Qumran Aramaic, Imperial and Old Aramaic inscriptions, Christian Palestinian Aramaic, Mandaic, Samaritan Aramaic, and the majority of Ephrem's surviving works (those not yet digitized by the Digital Syriac Corpus) are not indexed. The word "Atlas" describes the interface, not exhaustive coverage.
- **The triliteral framing strains non-CCC roots.** The index forces a consonantal-triliteral shape onto every word. Geminate, hollow (II-w/y), weak (III-w/y, III-ʾ, I-ʾ), and quadriliteral roots are accordingly approximated or scored low rather than represented in their proper morphological class.
- **Verb-stem badges are best-effort from unvocalized text.** Stem classification from consonantal text is genuinely ambiguous in many cases; the binyan badge is a prior, not a determination.
- **Diachronic ordering confounds genre with chronology, and some dates are debated.** Frequency differences across the corpora reflect genre, register, dialect, and translation source as much as historical change, and the chronological ordering is an editorial choice (e.g. the dating of Targum Onkelos is contested). Diachronic views are suggestive starting points, not evidence.

In short: the Atlas is a convenience layer for *finding* and *aligning* attestations that already exist in the source corpora. It is reliable for that. It is not a lexicon, not a morphological gold standard, and not a source of validated etymologies.

## 6. Availability and reuse

- **Source code:** <https://github.com/Jossifresben/aramaic-root-atlas>
- **Live application:** <https://aramaic-root-atlas.onrender.com>
- **Archived release / concept DOI:** [10.5281/zenodo.19358625](https://doi.org/10.5281/zenodo.19358625) (resolves to the latest version; this paper describes v3.3.0). [CITE: Zenodo deposit, v3.3.0]
- **Code license:** Apache-2.0.
- **Data licenses:** bundled corpus data is licensed per upstream provider — Peshitta NT public domain; Peshitta OT CC-BY-NC; Biblical Aramaic, Targum Onkelos, and Targum Jonathan CC-BY-SA; the Targums to the Writings public domain; Ephrem CC-BY. Downstream reusers must respect the most restrictive license that applies to each file (see `LICENSE-DATA.md`).
- **Dependencies:** Python 3.8+ with Flask, requests, gunicorn, and flask-limiter (see `requirements.txt`); D3.js v7 and Noto Sans Syriac (OFL-1.1) are loaded client-side. The `aramaic_core/` engine has no Flask dependency and can be reused as a library.
- **Run locally:** `pip install -r requirements.txt` then `python3 app.py` (serves on `http://localhost:5002`).
- **API documentation:** interactive Swagger UI at `/api-docs`; OpenAPI 3.0.3 specification at `/static/swagger.json`.

**How to cite.** Fresco Benaim, Jose. (2026). *The Aramaic Root Atlas: A Cross-Script Concordance for Eight Aramaic Corpora* (v3.3.0). Zenodo. <https://doi.org/10.5281/zenodo.19358625>. A `CITATION.cff` is included in the repository, and every analysis page in the live application exports BibTeX, Chicago, MLA, APA, and SBL formats.

## Author

**Jose Fresco Benaim**, Independent Researcher. ORCID: [0009-0000-2026-0836](https://orcid.org/0009-0000-2026-0836). Website: <https://jossifresco.com>.

## Acknowledgements

Corpus data is drawn from the ETCBC Peshitta corpus (Eep Talstra Centre for Bible and Computer, Vrije Universiteit Amsterdam) [CITE: ETCBC], the Westminster Leningrad Codex, Targum Onkelos, Targum Jonathan, and the Targums to the Writings via Sefaria [CITE: Sefaria], and the Digital Syriac Corpus for Ephrem's works [CITE: Digital Syriac Corpus]. Translation tracks are sourced from bible.helloao.org. The SEDRA lexicon is provided by the Beth Mardutho Syriac Institute [CITE: Kiraz, SEDRA]. Cognate data was generated and curated with the Anthropic Claude API. Curated root-card seed data is drawn from the companion project Peshitta Constellations [CITE: Peshitta Constellations, DOI 10.5281/zenodo.19358529].

## References

[CITE: assemble bibliography — entries needed for ETCBC/Peshitta, Sefaria, SEDRA (Kiraz), Digital Syriac Corpus, CAL, Text-Fabric, SBLGNT (Holmes 2010), and the Peshitta Constellations companion deposit. A starter `paper.bib` exists in the repository with ETCBC, Sefaria, SEDRA, and DSC entries; CAL and Text-Fabric entries still need to be added.]
