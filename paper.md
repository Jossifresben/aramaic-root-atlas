---
title: 'Aramaic Root Atlas: A Cross-Corpus Triliteral Root Explorer for Aramaic Studies'
tags:
  - Aramaic
  - Syriac
  - linguistics
  - digital humanities
  - biblical studies
  - diachronic linguistics
  - triliteral roots
authors:
  - name: Jose Fresco Benaim
    orcid: 0009-0000-2026-0836
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 8 May 2026
bibliography: paper.bib
---

# Summary

The Aramaic Root Atlas is an open-access web application for cross-corpus analysis of triliteral roots across approximately 1,500 years of Aramaic literary history. It indexes 5,039 roots across five corpora — Biblical Aramaic (~6th–2nd c. BCE), Targum Onkelos (~1st–3rd c. CE), the Peshitta Old Testament (~2nd–4th c. CE), the Peshitta New Testament (~3rd–5th c. CE), and the Hymns of Ephrem the Syrian (~4th c. CE) — totalling 38,062 passages and 528,399 words in Syriac and Hebrew square script. Each word form is linked to its extracted triliteral root, gloss, confidence score, and verb stem (binyan), accessible directly from a verse reader. The tool is designed for scholars, students, and linguists studying Aramaic vocabulary across dialects and genres, and is freely available at https://aramaic-root-atlas.onrender.com.

# Statement of Need

Aramaic is a Semitic language family spanning over three millennia, with major literary corpora written in mutually related but distinct dialects: Biblical Aramaic (Imperial Aramaic), Jewish Palestinian Aramaic, Syriac, and Babylonian Aramaic. Existing philological tools — such as Accordance [@accordance], Logos [@logos], and the ETCBC linguistic database [@etcbc] — provide deep analysis within a single corpus or dialect but do not support cross-corpus, diachronic root comparison across the major Aramaic traditions in a unified interface.

The Aramaic Root Atlas addresses this gap by providing:

1. **Cross-corpus root lookup**: a single query surfaces attestations of a root (e.g., K-T-B "to write") across all five corpora simultaneously, with normalized frequency, word forms, and cross-attestation badges.
2. **Diachronic frequency analysis**: normalized occurrence rates across corpora ordered chronologically, enabling researchers to identify emerging, stable, or declining roots across Aramaic literary history.
3. **Script-independent root normalization**: Syriac (ܟܬܒ) and Hebrew square script (כתב) resolve to the same root key, enabling transparent cross-script comparison.
4. **Programmatic access**: a full JSON API supporting all analytical features, including a KWIC concordance, hapax legomena finder, proximity search, and verb stem (binyan) paradigm tables.

# Functionality

The Atlas provides the following research tools:

**Root Explorer**: look up any triliteral root by Latin transliteration (e.g., `SH-L-M`), Syriac Unicode, Hebrew, or Arabic script. Results include all attested word forms with frequency, corpus distribution, Hebrew and Arabic cognates, Greek NT equivalents, and semantic bridges to related roots via a D3.js force-directed visualization.

**Interlinear Reader**: any passage in any of the five corpora can be rendered word-for-word with Syriac text, transliteration, gloss, root, and verb stem. The SEDRA Syriac lexicon [@sedra] is queried as a secondary confidence source for Syriac tokens where the statistical extractor score falls below 0.5, rescuing approximately 20% of medium-confidence tokens to high confidence.

**Diachronic Analysis**: root frequency is normalized per 10,000 words within each corpus, then displayed as a bar chart in chronological corpus order. A Frequency Shifts view ranks roots by the magnitude of their cross-corpus change, enabling identification of lexical innovation and archaism.

**KWIC Concordance**: all attestations of a root are displayed in keyword-in-context layout (configurable window width), grouped by word form or verb stem, with export to CSV, JSON, plain text, and TEI XML.

**Hapax Legomena Finder**: a frequency slider (1–10 occurrences) surfaces rare and unique attestations across any corpus or the full collection.

**Passage Lexical Profile**: for any book and chapter range, the tool computes unique root count, lexical density, hapax count, stem distribution, and a verse-by-verse density chart.

**Collocations**: Pointwise Mutual Information (PMI) is computed for root co-occurrences at verse or chapter scope, surfacing statistically significant lexical associations.

**Parallel Viewer**: texts from different corpora covering the same passage (e.g., Genesis 1 in Peshitta OT, Targum Onkelos, and Biblical Aramaic) are displayed side-by-side.

The interface is fully localized in English, Spanish, Hebrew, and Arabic, with right-to-left support. Five translation tracks (WEB, Reina-Valera 1909, WLC, Van Dyck, SBLGNT) are available in the verse reader. All analysis pages generate academic citations in BibTeX, Chicago, MLA, APA, and SBL formats.

# Acknowledgements

Corpus data is drawn from the ETCBC Peshitta corpus [@etcbc], the Westminster Leningrad Codex and Targum Onkelos via Sefaria [@sefaria], and the Digital Syriac Corpus [@dsc] for Ephrem's Hymns of Nisibis. Translations are sourced from bible.helloao.org. The SEDRA lexicon is provided by the Beth Mardutho Syriac Institute [@sedra]. Cognate data was generated and curated with the Claude API (Anthropic).

# References
