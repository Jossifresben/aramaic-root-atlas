# Data Licensing — Aramaic Root Atlas

The **source code** in this repository is licensed under **Apache License 2.0**
(see [LICENSE](LICENSE)).

The **bundled corpus and reference data** under `data/` is **not** uniformly
Apache-2.0. Each file or sub-directory carries the upstream provider's license,
listed below. Downstream users who copy or redistribute these files must comply
with the most-restrictive license that applies to each file they reuse.

If you want to reuse the *code only* under Apache-2.0, exclude the `data/`
directory from your copy.

---

## `data/corpora/peshitta_nt.csv`

- **Content:** Syriac Peshitta New Testament, 7,440 verses, 101,469 words.
- **Upstream source:** BFBS Peshitta edition (public domain), digitized via
  [dukhrana.com](https://dukhrana.com) (Stephen Silver) and the
  [SEDRA project](https://sedra.bethmardutho.org) (Beth Mardutho Syriac Institute).
- **License:** **Public Domain** (PD) — the underlying text is out of copyright.
- **Attribution requested:** dukhrana.com and Beth Mardutho per their site
  notices.

## `data/corpora/peshitta_ot.csv`

- **Content:** Syriac Peshitta Old Testament, 23,072 verses, 309,889 words.
- **Upstream source:** [ETCBC/peshitta](https://github.com/ETCBC/peshitta), Eep
  Talstra Centre for Bible and Computer (Vrije Universiteit Amsterdam), based
  on the Leiden Peshitta Institute critical edition.
- **License:** **CC-BY-NC 4.0** (Creative Commons Attribution-NonCommercial).
- **Use restriction:** **Non-commercial use only.** Commercial use requires
  separate licensing from the upstream rights holders.
- **Attribution required:** "Peshitta OT data via ETCBC, based on the Leiden
  Peshitta Institute edition."

## `data/corpora/biblical_aramaic.csv`

- **Content:** Aramaic portions of the Hebrew Bible (Daniel 2:4b–7:28, Ezra
  4:8–6:18, Ezra 7:12–26, Genesis 31:47, Jeremiah 10:11), 269 verses, 4,880 words.
- **Upstream source:** [Sefaria API](https://www.sefaria.org), based on the
  Westminster Leningrad Codex (WLC).
- **License:** **CC-BY-SA 4.0** (Creative Commons Attribution-ShareAlike).
- **Use restriction:** Derivative works **must be licensed under CC-BY-SA 4.0
  or a compatible share-alike license.**
- **Attribution required:** "Biblical Aramaic text via Sefaria, based on the
  Westminster Leningrad Codex (CC-BY-SA)."

## `data/corpora/targum_onkelos.csv`

- **Content:** Targum Onkelos (Pentateuch only), 5,846 verses, 82,684 words.
- **Upstream source:** [Sefaria API](https://www.sefaria.org).
- **License:** **CC-BY-SA 4.0**.
- **Use restriction:** Same as Biblical Aramaic — derivative works must be
  CC-BY-SA.
- **Attribution required:** "Targum Onkelos via Sefaria (CC-BY-SA)."

## `data/corpora/targum_jonathan.csv`

- **Content:** Targum Jonathan to the Prophets (Former and Latter Prophets,
  21 books), 9,296 verses, 157,449 words.
- **Upstream source:** [Sefaria API](https://www.sefaria.org).
- **License:** **CC-BY-SA 4.0**.
- **Use restriction:** Same as Biblical Aramaic and Targum Onkelos —
  derivative works must be CC-BY-SA.
- **Attribution required:** "Targum Jonathan via Sefaria (CC-BY-SA)."

## `data/corpora/ephrem_nisibis.csv`

- **Content:** Ephrem the Syrian, *Hymns on Nisibis* (*Carmina Nisibena*),
  1,435 verses, 29,477 words. **Note:** this is one collection of Ephrem's
  surviving works; 38 further documents are indexed as `ephrem_works.csv`
  (below); collections not yet digitized by the Digital Syriac Corpus
  (Hymns on Faith, on Heresies, on Paradise, etc.) are not indexed.
- **Upstream source:** [Digital Syriac Corpus](https://syriaccorpus.org)
  (srophe/syriac-corpus), TEI XML.
- **License:** **CC-BY 4.0**.
- **Attribution required:** "Ephrem, *Hymns on Nisibis*, via Digital Syriac
  Corpus (CC-BY)."

## `data/corpora/targum_writings.csv`

- **Content:** Targums to the Writings (Ketuvim), 7,022 verses, 96,169 words
  across 10 books (Psalms, Job, Proverbs, Ruth, Lamentations, Ecclesiastes,
  Song of Songs, Esther [Targum Rishon], 1–2 Chronicles).
- **Upstream source:** [Sefaria API](https://www.sefaria.org) — Mikraot
  Gedolot versions ("Aramaic Targum to …") and the Wikisource version for
  the two Chronicles targums.
- **License:** **Public Domain** (each version's `license` field verified at
  fetch time; `scripts/fetch_targum_writings.py` aborts on any non-PD/CC
  license).
- **Deliberate exclusion:** *Targum Sheni on Esther* — its only Sefaria
  version ("Berlin, 1898") carries license "unknown"; excluded until
  clarified.
- **Attribution:** not legally required; "Targums to the Writings via
  Sefaria" is requested as a courtesy.

## `data/corpora/ephrem_works.csv`

- **Content:** Ephrem the Syrian, 38 documents beyond the Carmina Nisibena:
  the prose refutations (*To Hypatius* 1–5, *Against Domnus*, *Against
  Marcion*, *Against Bardaisan*, *On Virginity (Prose)*, *Against Mani*) and
  *Hymns on the Nativity* 1–28. 1,330 verses, 76,999 words.
- **Upstream source:** [Digital Syriac Corpus](https://syriaccorpus.org)
  (srophe/syriac-corpus), TEI XML. Editions: Beck CSCO 186 (1959); Mitchell
  *Prose Refutations* vols. 1–2 (1912/1921); Overbeck (1865).
- **License:** **CC-BY 4.0** (verified programmatically in all 38 TEI
  headers).
- **Attribution required:** "Ephrem via Digital Syriac Corpus (CC-BY)."

## `data/translations/translations_*.json`

- **Content:** English (WEB), Spanish (Reina-Valera 1909), Hebrew (WLC),
  Arabic (Van Dyck), Greek (SBLGNT) Bible texts.
- **Upstream source:** [bible.helloao.org](https://bible.helloao.org).
- **Per-track license:**
  - WEB: **Public Domain**
  - Reina-Valera 1909: **Public Domain** (pre-1928)
  - WLC: derived from CC-BY-SA Westminster sources
  - Van Dyck: **Public Domain** (1865)
  - SBLGNT: **CC-BY-SA 4.0** (Holmes 2010, Society of Biblical Literature)

## `data/roots/cognates.json`

- **Content:** 1,642 cognate root entries (Hebrew and/or Arabic)
  and 405 Greek NT parallel entries.
- **Provenance:** Initial set extracted from scholarly sources; **the rest
  generated via the Anthropic Claude API and partially curated** (493 in
  Phase 1, 84 for Targum Jonathan in v3.1, 38 for the v3.3 corpora). Not
  yet systematically validated against authoritative lexicons (HALOT, BDB,
  Sokoloff, Brockelmann, Lane, Wehr).
- **License:** Apache-2.0 (the same license as the source code), with the
  caveat that LLM-generated content may not be eligible for copyright in some
  jurisdictions; treat as public-domain-ish for academic reuse.
- **Note:** See README § Limitations & Caveats.

## `data/roots/sedra_cache.json`

- **Content:** 12,534 cached lookups from the SEDRA Syriac lexicon.
- **Upstream source:** SEDRA, Beth Mardutho Syriac Institute, via their public
  API.
- **License:** SEDRA terms of use apply. Cached for performance; users
  redistributing this cache should consult Beth Mardutho's
  [terms](https://sedra.bethmardutho.org).

## `data/roots/known_roots.json`, `stopwords.json`, `word_glosses_override.json`

- **Provenance:** Curated by the Aramaic Root Atlas author.
- **License:** Apache-2.0 (same as source code).

---

## Summary table

| File | License | Commercial use? | Share-alike? | Attribution? |
|---|---|---|---|---|
| `peshitta_nt.csv` | Public Domain | ✅ Yes | n/a | requested |
| `peshitta_ot.csv` | CC-BY-NC 4.0 | ❌ No | n/a | required |
| `biblical_aramaic.csv` | CC-BY-SA 4.0 | ✅ Yes | required | required |
| `targum_onkelos.csv` | CC-BY-SA 4.0 | ✅ Yes | required | required |
| `targum_jonathan.csv` | CC-BY-SA 4.0 | ✅ Yes | required | required |
| `ephrem_nisibis.csv` | CC-BY 4.0 | ✅ Yes | n/a | required |
| `targum_writings.csv` | Public Domain | ✅ Yes | n/a | requested |
| `ephrem_works.csv` | CC-BY 4.0 | ✅ Yes | n/a | required |
| `translations_*.json` (mixed) | mostly PD; SBLGNT is CC-BY-SA | ✅ mostly | mixed | mixed |
| `cognates.json` | Apache-2.0 | ✅ Yes | n/a | requested |
| `sedra_cache.json` | SEDRA terms | see Beth Mardutho | n/a | required |

---

## Practical guidance

1. **If you fork this repo for a non-commercial academic project**, you can use
   everything as-is, attributing each upstream provider.
2. **If you fork for a commercial product**, you cannot ship `peshitta_ot.csv`
   without separately licensing it from ETCBC. Consider replacing it with
   another Peshitta OT source.
3. **If you redistribute modified versions of the Sefaria-derived data**
   (`biblical_aramaic.csv`, `targum_onkelos.csv`, `targum_jonathan.csv`), your
   derivatives must be CC-BY-SA-licensed.
4. **If you use the API only** (no data redistribution), the per-corpus
   licenses don't bind you — but you should still attribute the underlying
   sources in any publication that draws on the data.

---

*Last updated: 2026-05-09. If you spot a licensing inaccuracy, please open an
issue.*
