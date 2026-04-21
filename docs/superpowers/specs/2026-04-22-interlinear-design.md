# Interlinear Reader — Design Spec

**Date:** 2026-04-22  
**Scope:** Dedicated `/interlinear` page with passage-range selection, word-by-word RTL layout, and scholarly export (TEI XML, plain text, CSV).  
**Audience:** Academic scholars and linguists studying Aramaic vocabulary and morphology across corpora.

---

## 1. Goals

- Give scholars a classic interlinear view (Syriac → transliteration → gloss → root → stem) for any passage range across all four corpora.
- Make it export-ready in formats expected by the academic community (TEI XML, tab-delimited plain text, CSV).
- Reuse all existing word-level data — no new linguistic computation required.

---

## 2. Page — `/interlinear`

### Control Bar

| Control | Values |
|---------|--------|
| Book dropdown | Same book list as the reader; filtered by selected corpus |
| From `chapter:verse` | Text input, e.g. `5:1` |
| To `chapter:verse` | Text input, e.g. `5:12` |
| Corpus selector | Biblical Aramaic → Targum Onkelos → Peshitta NT → Peshitta OT |
| Script toggle | Latin / Syriac / Hebrew / Arabic |
| Syriac font | Estrangela / Eastern / Western (reuses `--syriac-font` CSS var) |
| Analyze button | Fetches `/api/interlinear` and renders |

After render, **← prev chapter** and **next chapter →** links appear below the control bar. Left/right arrow keys also navigate chapters.

A link to `/interlinear` is added to the **Research** dropdown in `base.html`, after the Concordance entry.

### Interlinear Display

Each verse renders as a labeled block:

```
Matthew 5:1                          [verse reference — deep-link anchor id="v5-1"]

┌────────┬────────┬────────┬────────┬────────┐   ← words flow RTL (row-reverse)
│ ܝܫܘܥ  │ ܚܙܐ    │ ܙܒܢܐ  │ ܕܝܢ    │ ܒܗܘ    │   row 1: Syriac (large RTL font)
│ Yeshuʿ│ ḥza    │ zabna  │ den    │ b-haw  │   row 2: transliteration
│ Jesus  │ saw    │ time   │ but    │ in that│   row 3: gloss (italic)
│ Y-SH-ʿ│ Ḥ-Z-Y  │ Z-B-N  │ D-Y-N  │ B-H-W  │   row 4: root (linked → /visualize)
│        │ [Peal] │        │        │        │   row 5: stem badge (verbal forms only)
└────────┴────────┴────────┴────────┴────────┘

  When Jesus saw the crowds…   [translation — toggleable, RTL if he/ar track]
```

**Layout rules:**
- Word cells use `display: flex; flex-direction: column` inside an RTL flex container (`flex-direction: row-reverse; flex-wrap: wrap`).
- Row 1 uses `var(--syriac-font)` at ~1.4rem.
- Row 2 uses monospace, ~0.8rem. For Hebrew/Arabic script mode, uses `Noto Sans Hebrew`/`Noto Sans Arabic` at ~1rem and RTL direction (matching the reader's `verse-translit--rtl` class).
- Row 4 root links open `/visualize/<root_key>` in a new tab.
- Row 5 stem badge uses existing `.stem-badge` CSS color palette (Peal / Ethpeel / Pael / etc.).
- Low-confidence roots (< 0.5) shown with muted color; medium (0.5–0.8) with standard color; high (≥ 0.8) full weight.
- Words with no extracted root show a `—` placeholder in rows 4–5.
- Verse reference is rendered as a left-margin label with a named anchor for deep-linking (e.g., `#v5-1`).

---

## 3. API — `GET /api/interlinear`

**Parameters:**

| Param | Default | Description |
|-------|---------|-------------|
| `book` | required | Book name (e.g., `Matthew`) |
| `ch_start` | required | Start chapter (int) |
| `v_start` | `1` | Start verse (int) |
| `ch_end` | `ch_start` | End chapter (int) |
| `v_end` | last verse | End verse (int) |
| `corpus` | auto-detected | `peshitta_nt`, `peshitta_ot`, `biblical_aramaic`, `targum_onkelos` |
| `script` | `latin` | `latin`, `syriac`, `hebrew`, `arabic` |
| `lang` | `en` | `en`, `es`, `he`, `ar` (controls gloss language) |

**Response shape:**
```json
{
  "book": "Matthew",
  "corpus": "peshitta_nt",
  "verses": [
    {
      "ref": "Matthew 5:1",
      "chapter": 5,
      "verse": 1,
      "words": [
        {
          "syriac": "ܝܫܘܥ",
          "translit": "Yeshuʿ",
          "root": "Y-SH-ʿ",
          "root_key": "y-sh-'",
          "gloss": "Jesus",
          "stem": null,
          "confidence": 0.95
        }
      ],
      "translation": "When Jesus saw the crowds…"
    }
  ]
}
```

**Implementation notes:**
- All word-level data already exists in `_extractor`. This endpoint is a multi-verse aggregation of the logic already used in `/api/verse`.
- Transliteration branches on `script` param using the same functions as the reader fix (`transliterate_syriac_to_hebrew`, `transliterate_syriac_to_arabic`, etc.).
- Gloss language follows `lang` param (not `trans`), consistent with the collocations/semantic-fields fix.
- Passage limits: cap at 10 chapters or 500 verses to prevent timeout; return a `truncated: true` flag if exceeded.

---

## 4. Export Formats

Three client-side export buttons below the rendered passage:

### TEI XML
Standard scholarly markup. Each verse is a `<ab>` element; each word is a `<w>` element:
```xml
<div type="book" n="Matthew">
  <ab n="Matt.5.1">
    <w xml:id="Matt.5.1.1" lemma="y-sh-'" pos="n" cert="high">ܝܫܘܥ</w>
    <w xml:id="Matt.5.1.2" lemma="h-z-y" pos="v" ana="Peal" cert="high">ܚܙܐ</w>
  </ab>
</div>
```
- `cert` maps confidence tiers: `high` ≥ 0.8, `medium` 0.5–0.8, `low` < 0.5.
- `pos` is `v` for verbal forms (stem present), `n` otherwise.
- Downloaded as `aramaic-atlas-interlinear-<book>-<range>.xml`.

### Plain Text
Tab-separated, one word per line, blank line between verses. Column order: `syriac TAB translit TAB gloss TAB root TAB stem`. Verse reference on its own line prefixed with `#`. Compatible with AntConc, R, Python.

### CSV
Columns: `book, chapter, verse, position, syriac, translit, root, gloss, stem, confidence`. Downloaded as `aramaic-atlas-interlinear-<book>-<range>.csv`.

---

## 5. Files Changed

### New files
- `templates/interlinear.html`

### Modified files

| File | Change |
|------|--------|
| `app.py` | Add `GET /api/interlinear` endpoint + `GET /interlinear` page route |
| `templates/base.html` | Add `/interlinear` link to Research dropdown |
| `static/style.css` | Add `.interlinear-*` CSS classes for word grid layout |
| `data/i18n.json` | ~10 new keys: `il_title`, `il_subtitle`, `il_from`, `il_to`, `il_analyze`, `il_export_tei`, `il_export_txt`, `il_export_csv`, `il_translation_toggle`, `il_truncated_warning` |

---

## 6. i18n Keys

| Key | English |
|-----|---------|
| `il_title` | Interlinear Reader |
| `il_subtitle` | Word-by-word alignment across all corpora |
| `il_from` | From |
| `il_to` | To |
| `il_analyze` | Analyze |
| `il_translation_toggle` | Show translation |
| `il_export_tei` | Export TEI XML |
| `il_export_txt` | Export Plain Text |
| `il_export_csv` | Export CSV |
| `il_truncated_warning` | Passage truncated at 500 verses. Narrow your range for full export. |

---

## 7. Out of Scope (v2)

- Parallel corpus column (Targum alongside Peshitta) — noted as a natural extension once the single-corpus view is solid.
- Inline annotation panel per verse — can be added later using the existing annotations infrastructure.
- Server-side PDF export.
