# Aramaic Root Atlas -- API Documentation

Base URL: `http://localhost:5001`

All endpoints return JSON. The server initializes lazily on first request (loading corpora, building root index), so the first call may take several seconds.

---

## Quick Start

```bash
# Start the server
python3 app.py  # listens on port 5001

# Get corpus statistics
curl http://localhost:5001/api/stats

# Look up a root by Latin transliteration
curl "http://localhost:5001/api/roots?q=SH-L-M"

# Search for a word in English translations
curl "http://localhost:5001/api/search?q=peace&lang=en"

# Get a single verse with word-level data
curl "http://localhost:5001/api/verse?ref=Matthew+1:1"

# Browse books in the Peshitta NT
curl "http://localhost:5001/api/books?corpus=peshitta_nt"

# Read a chapter with Spanish translation
curl "http://localhost:5001/api/chapter/Genesis/1?trans=es"
```

---

## Root Input Format

Roots are triliteral (occasionally biliteral) Semitic consonant patterns. The API accepts roots in several formats via the `q` parameter:

| Format | Example | Notes |
|--------|---------|-------|
| Dash-separated Latin | `SH-L-M` | Preferred. Case-insensitive. |
| Syriac Unicode | `ܫܠܡ` | Direct Syriac script (U+0710--U+074F). |
| Hebrew Unicode | `שלמ` | Converted internally to Syriac equivalent. |
| Arabic Unicode | `سلم` | Converted internally to Syriac equivalent. |

**Common Latin consonant mappings:**

| Latin | Syriac | Name |
|-------|--------|------|
| `'` or `A` | ܐ | Aleph |
| `B` | ܒ | Beth |
| `G` | ܓ | Gamal |
| `D` | ܕ | Dalath |
| `H` | ܗ | He |
| `W` | ܘ | Waw |
| `Z` | ܙ | Zain |
| `X` | ܚ | Heth |
| `T` | ܛ | Teth |
| `Y` | ܝ | Yodh |
| `K` | ܟ | Kaph |
| `L` | ܠ | Lamadh |
| `M` | ܡ | Mim |
| `N` | ܢ | Nun |
| `S` | ܣ | Semkath |
| `E` | ܥ | Ayin |
| `P` | ܦ | Pe |
| `TZ` | ܨ | Tsade |
| `Q` | ܩ | Qoph |
| `R` | ܪ | Resh |
| `SH` | ܫ | Shin |
| `TH` | ܬ | Taw |

The API also tries Semitic sound-correspondence variants automatically (e.g., TH/T, S/SH) if the exact root is not found.

---

## Common Query Parameters

Several parameters are shared across multiple endpoints:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | string | `en` | UI language. One of: `en`, `es`, `he`, `ar`. Affects glosses and book names. |
| `corpus` | string | _(all)_ | Filter by corpus ID. One of: `peshitta_nt`, `peshitta_ot`, `biblical_aramaic`, `targum_onkelos`. Omit to search all. |
| `trans` | string | value of `lang` | Translation track for verse text. One of: `en`, `es`, `he`, `ar`. |
| `script` | string | `latin` | Transliteration script. One of: `latin`, `syriac`, `hebrew`, `arabic`. |

---

## Endpoints

### GET /api/stats

Return aggregate corpus statistics.

**Parameters:** None.

**Response:**

```json
{
  "corpora": [
    {
      "id": "peshitta_nt",
      "label": "Peshitta NT",
      "verses": 7440,
      "words": 101469
    },
    {
      "id": "peshitta_ot",
      "label": "Peshitta OT",
      "verses": 23072,
      "words": 309889
    },
    {
      "id": "biblical_aramaic",
      "label": "Biblical Aramaic",
      "verses": 269,
      "words": 4880
    },
    {
      "id": "targum_onkelos",
      "label": "Targum Onkelos",
      "verses": 5846,
      "words": 82684
    }
  ],
  "total_verses": 36627,
  "total_words": 498922,
  "total_unique": 72566,
  "root_count": 5039
}
```

---

### GET /api/roots

Look up a triliteral root and return all attested word forms, cognates, and cross-corpus attestation.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | yes | -- | Root query (see Root Input Format above). |
| `corpus` | string | no | _(all)_ | Filter results to a single corpus. |
| `lang` | string | no | `en` | Language for glosses. |

**Response (200):**

```json
{
  "root": "\u072b\u0720\u0721",
  "root_transliteration": "shlm",
  "root_academic": "\u0161lm",
  "total_occurrences": 312,
  "root_display": "\u072b\u0720\u0721 / \u05e9\u05dc\u05de",
  "root_scripts": ["syriac", "hebrew"],
  "corpus_attestation": {
    "peshitta_nt": 85,
    "peshitta_ot": 220,
    "biblical_aramaic": 7,
    "targum_onkelos": 42
  },
  "matches": [
    {
      "form": "\u072b\u0720\u0721\u0710",
      "transliteration": "shlma",
      "count": 94,
      "references": ["Matthew 10:13", "Matthew 10:34"],
      "gloss_en": "peace",
      "gloss_es": "paz"
    }
  ],
  "cognates": {
    "gloss_en": "peace, completeness, wholeness",
    "gloss_es": "paz, totalidad, integridad",
    "sabor_raiz_en": "the fullness that comes when nothing is missing",
    "sabor_raiz_es": "la plenitud que llega cuando nada falta",
    "hebrew": [
      {
        "word": "\u05e9\u05b8\u05c1\u05dc\u05d5\u05b9\u05dd",
        "transliteration": "shalom",
        "meaning_en": "peace, welfare, completeness",
        "meaning_es": "paz, bienestar, integridad"
      }
    ],
    "arabic": [
      {
        "word": "\u0633\u064e\u0644\u0650\u0645\u064e",
        "transliteration": "salima",
        "meaning_en": "to be safe, unharmed",
        "meaning_es": "estar a salvo, ileso"
      }
    ]
  }
}
```

**Notes:**
- `references` is capped at 20 per word form to limit response size.
- `root_display` shows the root in all scripts where it is attested (e.g., Syriac + Hebrew for cross-corpus roots).
- `root_scripts` lists which scripts the root appears in across corpora.
- `cognates` is only present if cognate data exists for the root.

**Error Responses:**

| Status | Body | Cause |
|--------|------|-------|
| 400 | `{"error": "Missing query parameter q"}` | No `q` parameter provided. |
| 400 | `{"error": "Could not parse root: XYZ"}` | Input could not be mapped to Syriac consonants. |
| 404 | `{"error": "Root not found: K-T-B"}` | Root is not attested in any loaded corpus. |

---

### GET /api/books

Return the list of books and their chapter counts, optionally filtered by corpus.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `corpus` | string | no | _(all)_ | Filter to a single corpus ID. |

**Response (200):**

```json
{
  "books": [
    {"name": "Matthew", "chapters": 28},
    {"name": "Mark", "chapters": 16}
  ],
  "corpus": "peshitta_nt"
}
```

**Notes:**
- `corpus` in the response echoes the filter applied (or `null` if none).
- Book names are in English. Use the `lang` parameter with page routes for localized names.

---

### GET /api/chapter/\<book\>/\<chapter\>

Return all verses in a chapter with Syriac text and a translation.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `book` | path | yes | -- | Book name in English (e.g., `Genesis`, `Matthew`). |
| `chapter` | path (int) | yes | -- | Chapter number (1-based). |
| `corpus` | string | no | _(all)_ | Filter to a single corpus. |
| `trans` | string | no | `en` | Translation language: `en`, `es`, `he`, `ar`. |

**Response (200):**

```json
{
  "book": "Genesis",
  "chapter": 1,
  "verses": [
    {
      "verse": 1,
      "reference": "Genesis 1:1",
      "syriac": "\u0712\u072a\u0713\u072b\u071d\u072c ...",
      "translation": "In the beginning, God created...",
      "corpus_id": "peshitta_ot"
    }
  ]
}
```

**Notes:**
- If the requested translation track is unavailable for a verse, the English translation is returned as fallback.
- `corpus_id` indicates which corpus each verse belongs to.

---

### GET /api/search

Full-text search across translation tracks.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | yes | -- | Search query text. |
| `lang` | string | no | `en` | Which translation track to search in (`en`, `es`, `he`, `ar`). |
| `corpus` | string | no | _(all)_ | Filter to a single corpus. |

**Response (200):**

```json
{
  "query": "peace",
  "count": 42,
  "results": [
    {
      "reference": "Matthew 10:13",
      "text": "...let your peace come upon it...",
      "transliteration": "wshlmkwn ...",
      "corpus_id": "peshitta_nt"
    }
  ]
}
```

**Notes:**
- Results are capped at 50.
- Search is case-insensitive substring matching within the chosen translation track.
- Each result includes a `transliteration` field with the Latin transliteration of the Syriac text.

**Error Responses:**

| Status | Body | Cause |
|--------|------|-------|
| 400 | `{"error": "Missing query parameter q"}` | No search term provided. |

---

### GET /api/chapter-roots

Return all roots found in a chapter, sorted by frequency. Used by the chapter root summary panel.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `book` | string | yes | -- | Book name in English (e.g., `Matthew`, `Genesis`). |
| `chapter` | int | yes | -- | Chapter number (1-based). |
| `corpus` | string | no | _(all)_ | Filter to a single corpus. |
| `lang` | string | no | `en` | Language for glosses. |

**Response (200):**

```json
{
  "book": "Matthew",
  "chapter": 5,
  "roots": [
    {
      "root": "\u0710\u0721\u072a",
      "translit": "A-M-R",
      "gloss": "to say, speak",
      "count": 7,
      "confidence": 0.95,
      "forms": ["\u0710\u0721\u072a", "\u0710\u0721\u072a\u072c"]
    }
  ],
  "total_roots": 42
}
```

**Notes:**
- Roots are sorted by descending `count` (frequency within the chapter).
- `confidence` is the root extraction confidence score (0.0--1.0). High >= 0.8, Medium 0.5--0.8, Low < 0.5.
- `forms` lists the distinct word forms attested for each root in the chapter.

**Error Responses:**

| Status | Body | Cause |
|--------|------|-------|
| 400 | `{"error": "Missing book or chapter"}` | Required parameters missing. |
| 404 | `{"error": "No verses found"}` | Book/chapter not in any loaded corpus. |

---

### GET /api/verse

Return a single verse with word-level data, transliterations, and all available translations. Used by the verse detail modal.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ref` | string | yes | -- | Verse reference in `Book Chapter:Verse` format (e.g., `Psalms 1:1`). |
| `lang` | string | no | `en` | UI language. |
| `trans` | string | no | value of `lang` | Primary translation track. |

**Response (200):**

```json
{
  "reference": "Psalms 1:1",
  "reference_display": "Psalms 1:1",
  "words": ["\u0719\u0718\u0712\u071d\u0717\u0710", "..."],
  "words_translit": ["twbyh", "..."],
  "words_translit_academic": ["\u1e6dwbih", "..."],
  "translation_en": "Blessed is the man...",
  "translation_es": "Bienaventurado el hombre...",
  "translation_he": "...",
  "translation_ar": "...",
  "prev_ref": "Job 42:17",
  "next_ref": "Psalms 1:2"
}
```

**Notes:**
- `words`, `words_translit`, and `words_translit_academic` are parallel arrays (same length, same order).
- `prev_ref` and `next_ref` enable forward/back navigation in the verse modal. They are `null` at corpus boundaries.
- All four translation tracks are returned regardless of the `trans` parameter.

**Error Responses:**

| Status | Body | Cause |
|--------|------|-------|
| 400 | `{"error": "Missing ref parameter"}` | No `ref` provided. |
| 404 | `{"error": "Verse not found: Foo 1:1"}` | Reference does not match any loaded verse. |

---

### GET /api/suggest

Autocomplete endpoint returning roots that match a Latin-letter prefix. Used by the search box.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prefix` | string | yes | -- | Latin-letter prefix to match (e.g., `SH`, `K-T`). Case-insensitive. |

**Response (200):**

```json
[
  {
    "root": "\u072b\u0720\u0721",
    "translit": "SH-L-M",
    "count": 312
  },
  {
    "root": "\u072b\u0720\u071d",
    "translit": "SH-L-Y",
    "count": 45
  }
]
```

**Notes:**
- Returns at most 20 suggestions.
- Results are ordered by index position (effectively alphabetical by transliteration).
- The prefix `A` also matches roots beginning with Aleph (`'`).
- The prefix `O` is normalized to `E` (both map to Ayin).
- Returns an empty array `[]` if `prefix` is empty or no matches are found.

---

### GET /api/proximity-search

Find verses (or chapters) where two roots co-occur. Used for studying semantic relationships.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `root1` | string | yes | -- | First root (same formats as `/api/roots?q=`). |
| `root2` | string | yes | -- | Second root. |
| `scope` | string | no | `verse` | Co-occurrence scope: `verse` or `chapter`. |
| `corpus` | string | no | _(all)_ | Filter to a single corpus. |
| `lang` | string | no | `en` | Language for glosses. |
| `trans` | string | no | value of `lang` | Translation track for verse text. |
| `script` | string | no | `latin` | Transliteration script for verse output. |

**Response (200, scope=verse):**

```json
{
  "root1": "SH-L-M",
  "root2": "M-L-K",
  "root1_syriac": "\u072b\u0720\u0721",
  "root2_syriac": "\u0721\u0720\u071f",
  "gloss1": "peace, completeness",
  "gloss2": "to reign, king",
  "scope": "verse",
  "count": 15,
  "results": [
    {
      "ref": "Genesis 14:18",
      "syriac": "...",
      "translit": "...",
      "translation": "And Melchizedek king of Salem...",
      "forms1": ["\u072b\u0720\u0721"],
      "forms2": ["\u0721\u0720\u071f\u0710"],
      "corpus_id": "peshitta_ot"
    }
  ]
}
```

**Response (200, scope=chapter):**

```json
{
  "root1": "SH-L-M",
  "root2": "M-L-K",
  "scope": "chapter",
  "count": 8,
  "results": [
    {"ref": "Genesis 14", "type": "chapter"}
  ]
}
```

**Notes:**
- Verse-scope results are capped at 100.
- Chapter-scope results are capped at 50.
- `forms1` and `forms2` list the specific word forms of each root found in that verse.
- Translation text is truncated to 200 characters.
- Semitic sound-correspondence variants are tried automatically.

**Error Responses:**

| Status | Body | Cause |
|--------|------|-------|
| 400 | `{"error": "Two roots required"}` | One or both roots missing. |
| 400 | `{"error": "Invalid root input"}` | Input could not be parsed. |
| 200 | `{"error": "Root not found: ...", "results": []}` | One root is not in the index (returns 200 with empty results). |

---

### GET /api/passage-constellation

Return root constellation data for a passage: all roots, their cognates, semantic bridges, and inter-root connections. Powers the D3.js force-graph visualization.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `book` | string | yes | -- | Book name in English. |
| `chapter` | int | yes | -- | Chapter number. |
| `v_start` | int | yes | -- | Start verse (1-based). |
| `v_end` | int | no | value of `v_start` | End verse (inclusive). |
| `corpus` | string | no | _(all)_ | Filter to a single corpus. |
| `lang` | string | no | `en` | Language for glosses and labels. |
| `trans` | string | no | value of `lang` | Translation track. |
| `script` | string | no | `latin` | Transliteration script for words. |

**Response (200):**

```json
{
  "reference": "Matthew 5:1-5",
  "total_roots": 12,
  "verses": [
    {
      "ref": "Matthew 5:1",
      "verse_num": 1,
      "words": [
        {
          "syriac": "\u071f\u0715",
          "translit": "kd",
          "root": "K-D",
          "root_syriac": "\u071f\u0715"
        }
      ],
      "translation": "Seeing the multitudes, he went up..."
    }
  ],
  "roots": [
    {
      "root_translit": "SH-L-M",
      "root_syriac": "\u072b\u0720\u0721",
      "gloss": "peace, completeness",
      "frequency": 3,
      "word_forms": [
        {"syriac": "\u072b\u0720\u0721\u0710", "translit": "shlma"}
      ],
      "hebrew": [
        {
          "word": "\u05e9\u05b8\u05c1\u05dc\u05d5\u05b9\u05dd",
          "translit": "shalom",
          "meaning": "peace, welfare",
          "outlier": false
        }
      ],
      "arabic": [
        {
          "word": "\u0633\u064e\u0644\u0650\u0645\u064e",
          "translit": "salima",
          "meaning": "to be safe",
          "outlier": false
        }
      ],
      "bridges": [
        {
          "target_root": "sh-l-kh",
          "bridge_concept": "sending forth from wholeness"
        }
      ]
    }
  ],
  "connections": [
    {
      "source": "SH-L-M",
      "target": "SH-L-KH",
      "concept": "sending forth from wholeness"
    },
    {
      "source": "K-T-B",
      "target": "K-TH-B",
      "concept": "Sister roots (2/3)",
      "type": "sister"
    }
  ]
}
```

**Notes:**
- `roots` are sorted by descending frequency within the passage.
- `connections` include both semantic bridges (from cognate data) and "sister roots" (roots sharing 2+ consonants in the same position).
- `word.root` is `null` for function words and particles where no root could be extracted.
- The `outlier` field on cognates flags semantic outliers that are etymologically related but have diverged in meaning.

**Error Responses:**

| Status | Body | Cause |
|--------|------|-------|
| 400 | `{"error": "Missing book, chapter, or v_start"}` | Required path parameters missing. |
| 404 | `{"error": "No verses found"}` | No verses matched the specified range. |

---

### GET /api/root-family

Return full root family data for the visualizer: word forms, cognates, sister roots, semantic bridges, and cross-corpus attestation.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `root` | string | yes | -- | Root query (same formats as `/api/roots?q=`). |
| `lang` | string | no | `en` | UI language. |
| `script` | string | no | `latin` | Transliteration script. |
| `trans` | string | no | value of `lang` | Translation track for glosses and paradigmatic verse. |

**Response (200):**

```json
{
  "root": "\u072b\u0720\u0721",
  "root_translit": "SH-L-M",
  "gloss": "peace, completeness, wholeness",
  "sabor": "the fullness that comes when nothing is missing",
  "total_occurrences": 312,
  "corpus_attestation": {
    "peshitta_nt": 85,
    "peshitta_ot": 220,
    "biblical_aramaic": 7,
    "targum_onkelos": 42
  },
  "syriac_words": [
    {
      "form": "\u072b\u0720\u0721\u0710",
      "translit": "shlma",
      "meaning": "peace",
      "count": 94,
      "corpus_counts": {"peshitta_nt": 30, "peshitta_ot": 64}
    }
  ],
  "hebrew_cognates": [...],
  "arabic_cognates": [...],
  "greek_cognates": [
    {
      "word": "\u03b5\u1f30\u03c1\u03ae\u03bd\u03b7",
      "transliteration": "eir\u0113n\u0113",
      "meaning": "peace"
    }
  ],
  "bridges": [...],
  "sister_roots": [
    {
      "root": "\u072b\u0720\u071d",
      "translit": "SH-L-Y",
      "gloss": "to be quiet, at rest",
      "count": 45
    }
  ],
  "paradigm_verse": {
    "ref": "Matthew 10:13",
    "text": "...",
    "translation": "..."
  }
}
```

**Error Responses:**

| Status | Body | Cause |
|--------|------|-------|
| 400 | `{"error": "Missing root parameter"}` | No `root` provided. |
| 400 | `{"error": "Invalid root"}` | Input could not be parsed. |

---

### GET /api/parallel

Return parallel texts for a verse reference across all corpora that contain it.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ref` | string | yes | -- | Verse reference (e.g., `Genesis 1:1`). |
| `lang` | string | no | `en` | UI language. |
| `trans` | string | no | value of `lang` | Translation track. |

**Response (200):**

```json
{
  "reference": "Genesis 1:1",
  "parallels": [
    {
      "corpus_id": "peshitta_ot",
      "corpus_label": "Peshitta OT",
      "text": "\u0712\u072a\u0713\u072b\u071d\u072c ...",
      "script": "syriac",
      "translation": "In the beginning..."
    },
    {
      "corpus_id": "targum_onkelos",
      "corpus_label": "Targum Onkelos",
      "text": "\u0712\u0729\u0715\u0721\u071d\u0722 ...",
      "script": "syriac",
      "translation": ""
    }
  ],
  "translation_en": "In the beginning...",
  "translation_es": "En el principio..."
}
```

**Error Responses:**

| Status | Body | Cause |
|--------|------|-------|
| 400 | `{"error": "Missing ref parameter"}` | No `ref` provided. |

---

### GET /api/heatmap

Return root frequency data across all corpora for heat map display.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | int | no | `100` | Maximum number of roots to return. Use `0` for all. |
| `sort` | string | no | `total` | Sort key: `total` (descending), `root` (alphabetical), or a corpus ID (e.g., `peshitta_nt`). |

**Response (200):**

```json
{
  "corpora": ["peshitta_nt", "peshitta_ot", "biblical_aramaic", "targum_onkelos"],
  "roots": [
    {
      "root": "\u0710\u0721\u072a",
      "root_translit": "A-M-R",
      "gloss": "to say, speak",
      "total": 4521,
      "peshitta_nt": 892,
      "peshitta_ot": 2843,
      "biblical_aramaic": 67,
      "targum_onkelos": 719
    }
  ],
  "total_roots": 5039
}
```

---

### GET /api/cognate-lookup

Reverse lookup Aramaic roots by Hebrew, Arabic, or transliterated cognate word.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `word` | string | yes | -- | Cognate word to search for (Hebrew, Arabic, or Latin transliteration, e.g., `shalom`, `salima`). |

**Response (200):**

```json
{
  "query": "shalom",
  "results": [
    {
      "root_syriac": "\u072b\u0720\u0721",
      "root_translit": "SH-L-M",
      "gloss": "peace, completeness, wholeness",
      "occurrences": 312
    }
  ]
}
```

**Notes:**
- Matches against Hebrew and Arabic cognate words and their transliterations in cognates.json.
- Search is case-insensitive.

**Error Responses:**

| Status | Body | Cause |
|--------|------|-------|
| 400 | `{"error": "Missing query parameter word"}` | No `word` parameter provided. |

---

### GET /api/reverse-search

Search roots by English or Spanish meaning. Scores and ranks results by relevance.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | yes | -- | Meaning to search for (e.g., `peace`, `escribir`). |
| `lang` | string | no | `en` | Language of the search term: `en` or `es`. |

**Response (200):**

```json
{
  "query": "peace",
  "lang": "en",
  "results": [
    {
      "root_syriac": "\u072b\u0720\u0721",
      "root_translit": "SH-L-M",
      "gloss": "peace, completeness, wholeness",
      "sabor": "the fullness that comes when nothing is missing",
      "occurrences": 312,
      "score": 0.95
    }
  ]
}
```

**Notes:**
- Returns the top 30 matches ranked by relevance score.
- Searches against gloss and sabor (root essence) fields in cognates.json.
- Higher `score` indicates a closer match to the query term.

**Error Responses:**

| Status | Body | Cause |
|--------|------|-------|
| 400 | `{"error": "Missing query parameter q"}` | No `q` parameter provided. |

---

## Page Routes (HTML)

These routes return rendered HTML pages, not JSON. They accept the common `lang`, `script`, and `trans` query parameters.

| Route | Description |
|-------|-------------|
| `GET /` | Home page with search box, corpus stats, and autocomplete. |
| `GET /browse` | Book browser with corpus filter tabs. Accepts `corpus` parameter. |
| `GET /read/<book>/<chapter>` | Verse reader with interlinear Syriac text, transliteration, and translation selector. |
| `GET /constellation` | Passage constellation visualization (D3.js force graph). Accepts `book`, `chapter`, `v_start`, `v_end`. |
| `GET /visualize/<root_key>` | Root family visualizer page (D3.js force graph + root card). `root_key` is a dash-separated Latin transliteration (e.g., `SH-L-M`). |
| `GET /parallel` | Synoptic parallel viewer for comparing texts across corpora. Accepts `book`, `chapter`. |
| `GET /heatmap` | Root frequency heat map page with interactive filter, sort, and export. |
| `GET /bookmarks` | Bookmarks page (localStorage-based verse & root favorites with tags, CSV/JSON export, copy citation). |
| `GET /about` | About page with project information, methodological notes, and credits. |

---

## Error Handling

All API errors return JSON with an `error` field:

```json
{"error": "Description of what went wrong"}
```

Standard HTTP status codes are used:
- **400** -- Bad request (missing or invalid parameters).
- **404** -- Resource not found (root, verse, or passage not in corpus).
- **200** -- Some endpoints return errors with 200 status and an empty `results` array (e.g., proximity search when one root is missing). Check the `error` field.
