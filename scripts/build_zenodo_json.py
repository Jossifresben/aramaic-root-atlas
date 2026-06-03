#!/usr/bin/env python3
"""Build .zenodo.json with a rich, sectioned HTML description.

Mirrors the well-structured v3.0.x Zenodo abstract (Corpora, Research
Tools, Cognates, Programmatic Access, Localization, Methodology, What's
New, Companion Projects, Acknowledgements, Citation), updated for v3.1.0.
Zenodo's description sanitizer strips h1–h6, so section headings use
<p><strong>…</strong></p>; lists use <ul><li>. Run from repo root.
"""
import json, os

VERSION = "3.1.1"

description = """
<p><strong>Aramaic Root Atlas</strong> is an open-access web application for cross-corpus analysis of triliteral roots across approximately 1,500 years of Aramaic literary history. Version 3.1 indexes <strong>5,666 roots</strong> across <strong>47,358 verses</strong> and <strong>685,848 words</strong> from <strong>six corpora</strong> spanning the Achaemenid, Roman, and Late Antique periods, unified under a single consonantal root index with cross-script (Syriac &harr; Hebrew square) normalization.</p>

<p>The Atlas addresses a structural gap in computational Aramaic studies: existing philological tools provide deep analysis within a single corpus or dialect, but no unified resource lets researchers trace a Semitic root across the major Aramaic literary traditions in a single interface, with diachronic frequency normalization, comparative cognate visualization, and programmatic access. The tool is freely available at <a href="https://aramaic-root-atlas.onrender.com">aramaic-root-atlas.onrender.com</a> and licensed Apache-2.0.</p>

<p><strong>Corpora</strong></p>
<ul>
<li><strong>Peshitta New Testament</strong> &mdash; 7,440 verses, 101,469 words; ~3rd&ndash;5th c. CE; Syriac script; BFBS Peshitta (public domain).</li>
<li><strong>Peshitta Old Testament</strong> &mdash; 23,072 verses, 309,889 words; ~2nd&ndash;4th c. CE; Syriac script; ETCBC / Leiden Peshitta Institute (CC-BY-NC).</li>
<li><strong>Targum Onkelos</strong> &mdash; 5,846 verses, 82,684 words; ~1st&ndash;3rd c. CE Jewish Aramaic; Hebrew square script; Sefaria API (CC-BY-SA). The Targum to the Torah.</li>
<li><strong>Targum Jonathan</strong> &mdash; 9,296 verses, 157,449 words; ~1st&ndash;4th c. CE Jewish Aramaic; Hebrew square script; Sefaria API (CC-BY-SA). The Targum to the Prophets: Joshua&ndash;II Kings, Isaiah, Jeremiah, Ezekiel, and the Twelve. <em>New in v3.1.</em></li>
<li><strong>Biblical Aramaic</strong> &mdash; 269 verses, 4,880 words; ~6th&ndash;2nd c. BCE; Hebrew square script; Westminster Leningrad Codex via Sefaria (CC-BY-SA). Daniel 2:4b&ndash;7:28, Ezra 4:8&ndash;6:18, Ezra 7:12&ndash;26, Genesis 31:47, Jeremiah 10:11.</li>
<li><strong>Hymns of Ephrem of Nisibis</strong> &mdash; 1,435 verses, 29,477 words; ~4th c. CE Patristic Syriac; Syriac script; Digital Syriac Corpus (CC-BY).</li>
</ul>

<p><strong>Research Tools</strong></p>
<ul>
<li><strong>Root Explorer</strong> &mdash; lookup by Latin transliteration, Syriac Unicode, Hebrew, or Arabic. Returns all attested word forms with frequency, corpus distribution, Hebrew/Arabic cognates, Greek NT equivalents, sister roots, semantic bridges, paradigmatic verse citation, and a D3.js force-directed family visualization.</li>
<li><strong>Verb Stem (Binyan) Analysis</strong> &mdash; every word form classified into Peal, Ethpeel, Pael, Ethpaal, Aphel, Shafel, Ettaphal. Stem-distribution charts and full paradigm tables per root.</li>
<li><strong>KWIC Concordance</strong> &mdash; all attestations of any root in a configurable left-context | keyword | right-context layout, groupable by form or stem, exportable as CSV, JSON, plain text, or TEI XML.</li>
<li><strong>Diachronic Analysis</strong> &mdash; normalized frequency per 1,000 words across the six corpora in chronological order. A "frequency shifts" view ranks roots by the magnitude of cross-corpus change to identify lexical innovation and archaism.</li>
<li><strong>Hapax Legomena Finder</strong> &mdash; filters roots and forms by attestation frequency (1&ndash;5&times;) per corpus or across the full collection.</li>
<li><strong>Collocations</strong> &mdash; pointwise mutual information (PMI) computed for root co-occurrence at verse or chapter scope, surfacing statistically significant lexical associations.</li>
<li><strong>Semantic Fields</strong> &mdash; every root classified into 15 semantic domains (legal/covenant, cultic, kinship, war, knowledge, etc.) via large-language-model classification with manual curation.</li>
<li><strong>Word Parser</strong> &mdash; full morphological breakdown of any Syriac word: proclitic and verbal prefixes, root, pronominal and number suffixes &mdash; with stem badge, confidence score, Hebrew/Arabic cognates, and per-corpus attestation counts. Accepts Syriac Unicode or Latin transliteration input.</li>
<li><strong>Passage Lexical Profile</strong> &mdash; aggregate statistics for any book + chapter range: unique roots, lexical density, hapax counts, rarity distribution, stem distribution, top-15 roots, and a per-verse density sparkline.</li>
<li><strong>Parallel Viewer</strong> &mdash; side-by-side display of texts from different corpora covering the same passage, revealing translation choices. v3.1 unlocks synoptic comparison of the Peshitta Old Testament with Targum Jonathan across the Prophets (e.g. Isaiah 6 in Syriac alongside the Jewish Aramaic Targum).</li>
<li><strong>Passage Constellation</strong> &mdash; interactive force-directed graph of all roots and their relationships within a selected passage.</li>
<li><strong>Researcher Annotations</strong> &mdash; inline notes on verses and roots; tag-based filtering; exportable as JSON, CSV, or Markdown.</li>
<li><strong>Bookmarks</strong> &mdash; save verses and roots with tags; export as CSV/JSON/BibTeX/Zotero RDF; copy formatted citations.</li>
</ul>

<p><strong>Cognates and Cross-Linguistic Data</strong></p>
<p>The Atlas indexes <strong>1,604 Hebrew/Arabic cognate root entries</strong> with bilingual glosses, sister-root relationships, and semantic-bridge annotations linking outlier cognates back to their Semitic core. A separate layer of <strong>405 Greek New Testament cognates</strong> maps Aramaic roots onto their Greek equivalents (e.g. SH-L-M &rarr; &epsilon;&iota;&rho;&eta;&nu;&eta; "peace") for translation-technique studies. The SEDRA Syriac lexicon (Beth Mardutho Syriac Institute) is queried as a secondary confidence source for Syriac tokens, rescuing approximately 20% of medium-confidence extractions to high confidence.</p>

<p><strong>Programmatic Access</strong></p>
<p>A full JSON API exposes every analytical feature: root family data, KWIC concordances, hapax lists, diachronic frequencies, collocations, semantic fields, paradigm tables, word morphology, and passage profiles. REST endpoints are documented in an interactive Swagger UI at <code>/api-docs</code>, with parameter examples, response schemas, and try-it-out, plus a complete OpenAPI 3.0.3 specification at <code>/static/swagger.json</code> for client generation. Every <code>/api/X</code> path is also served at <code>/api/v1/X</code> under a published stability and 12-month deprecation policy, and public endpoints are rate-limited (600 req/min, 60 req/sec per IP) with <code>X-RateLimit-*</code> headers.</p>

<p><strong>Localization</strong></p>
<p>Full quadrilingual interface in English, Spanish, Hebrew, and Arabic, with right-to-left layout support throughout. Every analysis page, navigation label, button, dropdown, and table header is translated. Five translation tracks are available in the verse reader (WEB, Reina-Valera 1909, WLC, Van Dyck, SBLGNT).</p>

<p><strong>Methodology</strong></p>
<p>Triliteral roots are extracted via a rule-based morphological pipeline applied to each corpus's native script, with corpus-specific affix sets for Syriac and Hebrew square script; routing is by per-word script detection, so Hebrew-square corpora share one stripper. Each extraction receives a three-tier confidence score (High &ge; 0.8, Medium 0.5&ndash;0.8, Low &lt; 0.5) based on stem-pattern conformity, prefix/suffix legitimacy, and SEDRA lexicon corroboration where applicable. Cross-script root normalization ensures that Hebrew &#1499;&#1514;&#1489;, Syriac &#1827;&#1817;&#1810;, and Arabic &#1603;&#1578;&#1576; resolve to the same root key, enabling transparent cross-corpus comparison.</p>

<p><strong>What's New in v3.1.0</strong></p>
<ul>
<li><strong>New corpus &mdash; Targum Jonathan to the Prophets</strong> (Sefaria, CC-BY-SA): 9,296 verses and 157,449 words across 21 books, doubling Targumic coverage.</li>
<li>Unlocks synoptic comparison of the <strong>Peshitta Old Testament with Targum Jonathan</strong> across the Prophets in the Parallel Viewer.</li>
<li>Root index grows 5,249 &rarr; <strong>5,666</strong>; cognate entries 1,584 &rarr; <strong>1,604</strong> &mdash; newly attested Targum-Jonathan vocabulary enriched with Hebrew and Arabic cognates (LLM-generated, scoped to roots attested only in Targum Jonathan; flagged unverified pending lexicographer review).</li>
<li>Distinct corpus color, full UI/i18n integration across all four languages, and Swagger coverage for the new corpus.</li>
<li>Integration fixes: cross-corpus book-name alignment (Samuel/Kings), root-card layout, diachronic label rendering, corrected page titles and breadcrumb, and a "five corpora" &rarr; "six" reconciliation across the entire interface.</li>
<li><strong>v3.1.1 patch:</strong> de-duplicated cognate entries that shared a root key (1,655 &rarr; 1,604), so each root resolves to its richest curated Hebrew/Arabic cognate set; fixed a fetch edge case that left stray brackets on two Joshua tokens.</li>
</ul>

<p><strong>Companion Projects</strong></p>
<p><strong>Peshitta Constellations</strong> (DOI <a href="https://doi.org/10.5281/zenodo.19358529">10.5281/zenodo.19358529</a>) &mdash; companion project focused on the Peshitta New Testament; supplied curated root-card seed data (paradigmatic verse citations, sister-root and semantic-bridge relationships, root-flavor descriptions) that populate the root family visualizer in this project.</p>

<p><strong>Acknowledgements</strong></p>
<p>Corpus data is drawn from the ETCBC Peshitta corpus (Eep Talstra Centre for Bible and Computer, Vrije Universiteit Amsterdam), the Westminster Leningrad Codex, Targum Onkelos, and Targum Jonathan via Sefaria, and the Digital Syriac Corpus for Ephrem's Hymns of Nisibis. Translations are sourced from bible.helloao.org. The SEDRA lexicon is provided by the Beth Mardutho Syriac Institute. Cognate data was generated and curated with the Anthropic Claude API. Curated root-card seed data is drawn from the companion project Peshitta Constellations.</p>

<p><strong>How to Cite</strong></p>
<p>Fresco Benaim, Jose. (2026). <em>Aramaic Root Atlas: A Cross-Corpus Triliteral Root Explorer</em> (v3.1.1). Zenodo. <a href="https://doi.org/10.5281/zenodo.19358625">https://doi.org/10.5281/zenodo.19358625</a></p>
<p>The concept DOI <a href="https://doi.org/10.5281/zenodo.19358625">10.5281/zenodo.19358625</a> always resolves to the latest version. BibTeX, Chicago, MLA, APA, and SBL formats are available with one click on every analysis page in the live application and via the <code>CITATION.cff</code> in the repository.</p>

<p><strong>License and Source</strong></p>
<p>Apache License 2.0 (source code); bundled corpus data is licensed per upstream provider (see <code>LICENSE-DATA.md</code>). Source code: <a href="https://github.com/Jossifresben/aramaic-root-atlas">github.com/Jossifresben/aramaic-root-atlas</a>.</p>
""".strip()

meta = {
    "title": "Aramaic Root Atlas: A Cross-Corpus Triliteral Root Explorer",
    "upload_type": "software",
    "access_right": "open",
    "license": "Apache-2.0",
    "version": VERSION,
    "language": "eng",
    "creators": [
        {"name": "Fresco Benaim, Jose", "orcid": "0009-0000-2026-0836"}
    ],
    "keywords": [
        "Aramaic", "Syriac", "Peshitta", "Biblical Aramaic",
        "Targum Onkelos", "Targum Jonathan", "triliteral roots",
        "Semitic linguistics", "computational linguistics",
        "digital humanities", "corpus linguistics", "cognates"
    ],
    "related_identifiers": [
        {"identifier": "10.5281/zenodo.19358625", "relation": "isVersionOf", "scheme": "doi"},
        {"identifier": "10.5281/zenodo.19358529", "relation": "references", "scheme": "doi"},
        {"identifier": "https://github.com/Jossifresben/aramaic-root-atlas", "relation": "isSupplementTo", "scheme": "url"},
        {"identifier": "https://aramaic-root-atlas.onrender.com", "relation": "isIdenticalTo", "scheme": "url"}
    ],
    "description": description,
}

out = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".zenodo.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"wrote {out} ({len(description)} chars description)")
