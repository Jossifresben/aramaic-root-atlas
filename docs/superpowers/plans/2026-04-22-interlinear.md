# Interlinear Reader Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a dedicated `/interlinear` page that renders any Aramaic passage as a word-by-word RTL grid (Syriac → transliteration → gloss → root → stem), with passage-range selection, corpus/script controls, and TEI XML / plain text / CSV export.

**Architecture:** A new `GET /api/interlinear` endpoint aggregates per-word data (already extracted in the reader) across a verse range in one call. A new `templates/interlinear.html` page fetches that endpoint on demand and renders an RTL flex grid. Three client-side export functions build TEI XML, tab-delimited text, and CSV from the in-memory JSON.

**Tech Stack:** Flask (Python), Jinja2, vanilla JS, existing CSS variables and `.stem-badge` classes. All linguistic data comes from `_extractor` and `_cognate_lookup` — no new data sources.

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Modify | `data/i18n.json` | Add 10 new UI strings in EN/ES/HE/AR |
| Modify | `app.py` | Add `GET /api/interlinear` endpoint + `GET /interlinear` page route |
| Modify | `templates/base.html` | Add Interlinear link to Research dropdown |
| Modify | `static/style.css` | Add `.interlinear-*` CSS classes for word grid |
| Create | `templates/interlinear.html` | Full page: controls, word grid renderer, export |

---

## Task 1 — Add i18n keys

**Files:**
- Modify: `data/i18n.json`

- [ ] **Step 1: Add English keys** — insert after the last `pp_col_rarity` key in the `"en"` block (line ~1072):

```json
"il_title": "Interlinear Reader",
"il_subtitle": "Word-by-word alignment across all corpora",
"il_from": "From",
"il_to": "To",
"il_analyze": "Analyze",
"il_translation_toggle": "Show translation",
"il_export_tei": "Export TEI XML",
"il_export_txt": "Export Plain Text",
"il_export_csv": "Export CSV",
"il_truncated_warning": "Passage truncated at 500 verses. Narrow your range for full export."
```

- [ ] **Step 2: Add Spanish keys** — insert after `pp_col_rarity` in the `"es"` block (line ~536):

```json
"il_title": "Lectura Interlineal",
"il_subtitle": "Alineación palabra por palabra en todos los corpus",
"il_from": "Desde",
"il_to": "Hasta",
"il_analyze": "Analizar",
"il_translation_toggle": "Mostrar traducción",
"il_export_tei": "Exportar TEI XML",
"il_export_txt": "Exportar texto plano",
"il_export_csv": "Exportar CSV",
"il_truncated_warning": "Pasaje truncado en 500 versículos. Acota el rango para exportación completa."
```

- [ ] **Step 3: Add Hebrew keys** — insert after `pp_col_rarity` in the `"he"` block (line ~1608):

```json
"il_title": "קריאה אינטרלינארית",
"il_subtitle": "יישור מילה-במילה בכל הקורפוסים",
"il_from": "מ",
"il_to": "עד",
"il_analyze": "נתח",
"il_translation_toggle": "הצג תרגום",
"il_export_tei": "ייצא TEI XML",
"il_export_txt": "ייצא טקסט רגיל",
"il_export_csv": "ייצא CSV",
"il_truncated_warning": "הקטע קוצר ל-500 פסוקים. צמצם את הטווח לייצוא מלא."
```

- [ ] **Step 4: Add Arabic keys** — insert after `pp_col_rarity` in the `"ar"` block (line ~1888):

```json
"il_title": "القراءة المتوازية",
"il_subtitle": "محاذاة كلمة بكلمة عبر جميع المدونات",
"il_from": "من",
"il_to": "إلى",
"il_analyze": "تحليل",
"il_translation_toggle": "عرض الترجمة",
"il_export_tei": "تصدير TEI XML",
"il_export_txt": "تصدير نص عادي",
"il_export_csv": "تصدير CSV",
"il_truncated_warning": "تم اقتطاع المقطع عند 500 آية. قلّص النطاق للتصدير الكامل."
```

- [ ] **Step 5: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('data/i18n.json')); print('OK')"
```

Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add data/i18n.json
git commit -m "feat(interlinear): add i18n keys for interlinear reader"
```

---

## Task 2 — Add `/api/interlinear` endpoint

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Add the endpoint** — insert this block anywhere after the `api_verse` function (around line 555, before `_translit_to_dash`). The endpoint aggregates the same per-word extraction logic already used in the `read()` route:

```python
@app.route('/api/interlinear')
def api_interlinear():
    """Word-by-word interlinear data for a passage range.

    Query params:
        book       — book name (required)
        ch_start   — start chapter int (required)
        v_start    — start verse int (default 1)
        ch_end     — end chapter int (default ch_start)
        v_end      — end verse int (default 9999 = last verse)
        corpus     — corpus filter (optional)
        script     — latin|syriac|hebrew|arabic (default latin)
        lang       — en|es|he|ar (default en, controls gloss language)
        trans      — translation track (default = lang)
    """
    _init()
    book = request.args.get('book', '').strip()
    if not book:
        return jsonify({'error': 'Missing book parameter'}), 400

    ch_start = int(request.args.get('ch_start', 1))
    v_start_param = int(request.args.get('v_start', 1))
    ch_end = int(request.args.get('ch_end', ch_start))
    v_end_param = int(request.args.get('v_end', 9999))
    corpus_filter = request.args.get('corpus', '') or None
    script = request.args.get('script', 'latin')
    lang = request.args.get('lang', 'en')
    trans = request.args.get('trans', lang)

    from aramaic_core.characters import detect_script as _ds, transliterate_hebrew

    verses_out = []
    truncated = False
    total = 0

    for chapter in range(ch_start, ch_end + 1):
        rows = _corpus.get_chapter_verses(book, chapter, corpus_filter)
        for v_num, ref, syriac in rows:
            # Apply verse-range filter at chapter boundaries
            if chapter == ch_start and v_num < v_start_param:
                continue
            if chapter == ch_end and v_num > v_end_param:
                continue
            if total >= 500:
                truncated = True
                break
            total += 1

            words = syriac.split() if syriac else []
            word_data = []
            for w in words:
                # Per-word transliteration honoring the script param
                text_script = _ds(w)
                if text_script == 'hebrew':
                    t = transliterate_hebrew(w)
                elif script == 'syriac':
                    t = w
                elif script == 'hebrew':
                    t = transliterate_syriac_to_hebrew(w)
                elif script == 'arabic':
                    t = transliterate_syriac_to_arabic(w)
                else:
                    t = transliterate_syriac(w)

                # Root, stem, gloss
                result = _extractor.lookup_word_root_with_confidence(w)
                root_translit = ''
                root_key = ''
                gloss = ''
                stem = None
                confidence = 0.0

                if result:
                    root_syr, conf = result
                    confidence = round(conf, 2)
                    root_translit = _translit_to_dash(root_syr)
                    root_key = root_translit.lower()
                    stem = _extractor.lookup_word_stem(w)
                    # Multilingual gloss: prefer cognate entry, fall back to extractor
                    cog = _cognate_lookup.lookup_syriac(root_syr) if _cognate_lookup else None
                    if cog:
                        gloss = _pick_gloss(cog, lang)
                    else:
                        gloss = _extractor.get_root_gloss(root_syr) or ''

                word_data.append({
                    'syriac': w,
                    'translit': t,
                    'root': root_translit,
                    'root_key': root_key,
                    'gloss': gloss,
                    'stem': stem,
                    'confidence': confidence,
                })

            translation = _corpus.get_verse_translation(ref, trans) or ''
            if not translation and trans != 'en':
                translation = _corpus.get_verse_translation(ref, 'en') or ''

            verses_out.append({
                'ref': ref,
                'chapter': chapter,
                'verse': v_num,
                'words': word_data,
                'translation': translation,
            })

        if truncated:
            break

    return jsonify({
        'book': book,
        'corpus': corpus_filter or '',
        'verses': verses_out,
        'truncated': truncated,
    })
```

- [ ] **Step 2: Verify the endpoint works**

Start the server (`python3 app.py`) then:

```bash
curl "http://localhost:5001/api/interlinear?book=Matthew&ch_start=5&v_start=1&ch_end=5&v_end=3&lang=en" | python3 -m json.tool | head -60
```

Expected: JSON with `"verses"` array, each verse having `"words"` array with `syriac`, `translit`, `root`, `gloss`, `stem`, `confidence` fields.

- [ ] **Step 3: Verify truncation flag**

```bash
curl "http://localhost:5001/api/interlinear?book=Psalms&ch_start=1&ch_end=50&lang=en" | python3 -c "import sys,json; d=json.load(sys.stdin); print('truncated:', d['truncated'], 'verses:', len(d['verses']))"
```

Expected: `truncated: True verses: 500`

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat(interlinear): add GET /api/interlinear endpoint"
```

---

## Task 3 — Add page route and navbar link

**Files:**
- Modify: `app.py`
- Modify: `templates/base.html`

- [ ] **Step 1: Add the page route to `app.py`** — insert after `collocations_page` (around line 2447):

```python
@app.route('/interlinear')
def interlinear_page():
    _init()
    lang = _get_lang()
    books = _corpus.get_books()
    return render_template(
        'interlinear.html',
        lang=lang,
        trans=_get_trans(),
        script=_get_script(),
        t=lambda k, l=None: _t(k, lang),
        books=books,
        initial_book=request.args.get('book', ''),
        initial_ch_start=request.args.get('ch_start', ''),
        initial_v_start=request.args.get('v_start', ''),
        initial_ch_end=request.args.get('ch_end', ''),
        initial_v_end=request.args.get('v_end', ''),
    )
```

- [ ] **Step 2: Add navbar link in `templates/base.html`** — insert after the `passage-profile` link (line ~57), before the `<hr>` separator:

```html
<a href="/interlinear?lang={{ lang }}">{{ t('il_title', lang) if t else 'Interlinear Reader' }}</a>
```

The Research dropdown block should then read:
```html
<a href="/hapax?lang={{ lang }}">{{ t('hapax_title', lang) if t else 'Hapax Legomena' }}</a>
<a href="/concordance?lang={{ lang }}">{{ t('concordance_title', lang) if t else 'Concordance' }}</a>
<a href="/diachronic?lang={{ lang }}">{{ t('diachronic_title', lang) if t else 'Diachronic Analysis' }}</a>
<a href="/collocations?lang={{ lang }}">{{ t('coll_title', lang) if t else 'Collocations' }}</a>
<a href="/semantic-fields?lang={{ lang }}">{{ t('sf_title', lang) if t else 'Semantic Fields' }}</a>
<a href="/parse?lang={{ lang }}">{{ t('parse_title', lang) if t else 'Word Parser' }}</a>
<a href="/passage-profile?lang={{ lang }}">{{ t('pp_title', lang) if t else 'Passage Profile' }}</a>
<a href="/interlinear?lang={{ lang }}">{{ t('il_title', lang) if t else 'Interlinear Reader' }}</a>
<hr class="nav-drop-sep">
<a href="/bookmarks?lang={{ lang }}">{{ t('bookmarks_title', lang) if t else 'Bookmarks' }}</a>
<a href="/annotations?lang={{ lang }}">{{ t('ann_page_title', lang) if t else 'Research Notes' }}</a>
```

- [ ] **Step 3: Verify the page route loads**

Visit `http://localhost:5001/interlinear` — should return HTTP 200 (even before the template exists it will error with TemplateNotFound, not a 500 on the route itself). After creating the template in Task 5, re-verify.

- [ ] **Step 4: Commit**

```bash
git add app.py templates/base.html
git commit -m "feat(interlinear): add /interlinear page route and navbar link"
```

---

## Task 4 — Add CSS for interlinear word grid

**Files:**
- Modify: `static/style.css`

- [ ] **Step 1: Append the CSS block** — add at the end of `static/style.css`:

```css
/* ── Interlinear Reader ─────────────────────────────────────── */
.interlinear-controls {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: flex-end;
    margin-bottom: 1.5rem;
}
.interlinear-controls label {
    font-size: 0.8rem;
    color: var(--muted);
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}
.interlinear-controls input,
.interlinear-controls select {
    font-size: 0.9rem;
    padding: 0.35rem 0.5rem;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--card-bg);
    color: var(--text);
}
.interlinear-controls input[type="text"] {
    width: 90px;
}
.il-range-sep {
    font-size: 1.1rem;
    color: var(--muted);
    padding-bottom: 0.2rem;
    align-self: flex-end;
}
.il-analyze-btn {
    padding: 0.45rem 1.1rem;
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: var(--radius);
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    align-self: flex-end;
}
.il-analyze-btn:hover { opacity: 0.88; }

.il-export-bar {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 1.25rem;
}
.il-export-btn {
    padding: 0.3rem 0.8rem;
    font-size: 0.8rem;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--card-bg);
    color: var(--text);
    cursor: pointer;
}
.il-export-btn:hover { background: var(--accent-light); }

.il-translation-toggle {
    font-size: 0.8rem;
    color: var(--muted);
    cursor: pointer;
    user-select: none;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    margin-left: auto;
}

.il-truncated-warn {
    background: #fef9c3;
    color: #713f12;
    border: 1px solid #fde68a;
    border-radius: var(--radius);
    padding: 0.5rem 0.75rem;
    font-size: 0.85rem;
    margin-bottom: 1rem;
}
.dark-mode .il-truncated-warn {
    background: #422006;
    color: #fef3c7;
    border-color: #78350f;
}

.il-nav {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.il-nav a {
    font-size: 0.9rem;
    color: var(--accent);
    text-decoration: none;
}
.il-nav a:hover { text-decoration: underline; }

.interlinear-body { margin-top: 0.5rem; }

.interlinear-verse {
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}
.interlinear-ref {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.6rem;
}
.interlinear-words {
    display: flex;
    flex-direction: row-reverse;
    flex-wrap: wrap;
    gap: 0.3rem 0.6rem;
    margin-bottom: 0.6rem;
}
.il-word {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0.3rem 0.45rem;
    border: 1px solid transparent;
    border-radius: var(--radius);
    min-width: 56px;
    text-align: center;
    transition: background 0.12s;
}
.il-word:hover {
    background: var(--accent-light);
    border-color: var(--border);
}
.il-syriac {
    font-family: var(--syriac-font);
    font-size: 1.4rem;
    line-height: 1.6;
    direction: rtl;
}
.il-translit {
    font-size: 0.75rem;
    font-family: monospace;
    color: var(--muted);
    margin-top: 0.05rem;
}
.il-translit.il-rtl-script {
    font-family: 'Noto Sans Hebrew', 'Noto Sans Arabic', serif;
    font-size: 0.9rem;
    direction: rtl;
}
.il-gloss {
    font-size: 0.72rem;
    font-style: italic;
    color: var(--text-secondary, #888);
    margin-top: 0.05rem;
}
.il-root {
    font-size: 0.68rem;
    font-family: monospace;
    text-decoration: none;
    margin-top: 0.05rem;
    font-weight: 600;
}
.il-root-high { color: var(--accent); }
.il-root-med  { color: var(--text-secondary, #888); }
.il-root-low  { color: var(--muted); }
.il-root-none { color: var(--muted); font-style: italic; font-weight: 400; }
.il-root:hover { text-decoration: underline; }
.il-stem { margin-top: 0.15rem; }

.interlinear-translation {
    font-size: 0.88rem;
    color: var(--text-secondary, #888);
    padding-left: 0.6rem;
    border-left: 2px solid var(--border);
    margin-top: 0.25rem;
    line-height: 1.5;
}
.interlinear-translation[dir="rtl"] {
    border-left: none;
    border-right: 2px solid var(--border);
    padding-left: 0;
    padding-right: 0.6rem;
    text-align: right;
}
.interlinear-translation.il-trans-hidden { display: none; }

@media (max-width: 600px) {
    .il-syriac { font-size: 1.2rem; }
    .il-word { min-width: 46px; padding: 0.2rem 0.3rem; }
}
```

- [ ] **Step 2: Verify CSS is syntactically valid** — restart the server, open `http://localhost:5001/interlinear` and check the browser console for CSS errors. (The page will 500 until the template is created in Task 5, but the CSS will be parsed.)

- [ ] **Step 3: Commit**

```bash
git add static/style.css
git commit -m "feat(interlinear): add CSS for interlinear word grid"
```

---

## Task 5 — Create `templates/interlinear.html`

**Files:**
- Create: `templates/interlinear.html`

- [ ] **Step 1: Create the template file** with the full content below:

```html
{% extends "base.html" %}
{% block title %}{{ t('il_title', lang) }} — Aramaic Root Atlas{% endblock %}

{% block content %}
<div class="container" style="max-width:1100px;margin:2rem auto;padding:0 1rem;">

  <h1 class="page-title">{{ t('il_title', lang) }}</h1>
  <p class="page-subtitle" style="color:var(--muted);margin-bottom:1.5rem;">{{ t('il_subtitle', lang) }}</p>

  <!-- Controls -->
  <div class="interlinear-controls" id="il-controls">

    <label>{{ t('nav_corpus', lang) if t else 'Corpus' }}
      <select id="il-corpus">
        <option value="">{{ t('all_corpora', lang) if t else 'All Corpora' }}</option>
        <option value="biblical_aramaic">{{ t('corpus_ba', lang) if t else 'Biblical Aramaic' }}</option>
        <option value="targum_onkelos">{{ t('corpus_to', lang) if t else 'Targum Onkelos' }}</option>
        <option value="peshitta_nt">{{ t('corpus_nt', lang) if t else 'Peshitta NT' }}</option>
        <option value="peshitta_ot">{{ t('corpus_ot', lang) if t else 'Peshitta OT' }}</option>
      </select>
    </label>

    <label>{{ t('browse_book', lang) if t else 'Book' }}
      <select id="il-book">
        <option value="">— select —</option>
        {% for bname, bch in books %}
        <option value="{{ bname }}"{% if bname == initial_book %} selected{% endif %}>{{ bn(bname, lang) }}</option>
        {% endfor %}
      </select>
    </label>

    <label>{{ t('il_from', lang) }}
      <input type="text" id="il-ch-start" placeholder="ch:v" value="{{ initial_ch_start }}{% if initial_v_start %}:{{ initial_v_start }}{% endif %}" style="width:80px;">
    </label>

    <span class="il-range-sep">—</span>

    <label>{{ t('il_to', lang) }}
      <input type="text" id="il-ch-end" placeholder="ch:v" value="{{ initial_ch_end }}{% if initial_v_end %}:{{ initial_v_end }}{% endif %}" style="width:80px;">
    </label>

    <label>{{ t('settings_script', lang) if t else 'Script' }}
      <select id="il-script">
        <option value="latin"{% if script == 'latin' %} selected{% endif %}>Latin</option>
        <option value="syriac"{% if script == 'syriac' %} selected{% endif %}>Syriac</option>
        <option value="hebrew"{% if script == 'hebrew' %} selected{% endif %}>Hebrew</option>
        <option value="arabic"{% if script == 'arabic' %} selected{% endif %}>Arabic</option>
      </select>
    </label>

    <label>{{ t('settings_font', lang) if t else 'Font' }}
      <select id="il-font">
        <option value="estrangela">Estrangela</option>
        <option value="eastern">Eastern</option>
        <option value="western">Western</option>
      </select>
    </label>

    <button class="il-analyze-btn" onclick="loadInterlinear()">{{ t('il_analyze', lang) }}</button>

  </div>

  <!-- Nav + Export bar (shown after load) -->
  <div id="il-nav" class="il-nav" style="display:none;"></div>

  <div id="il-action-bar" style="display:none;margin-bottom:1rem;">
    <div class="il-export-bar">
      <button class="il-export-btn" onclick="exportTEI()">{{ t('il_export_tei', lang) }}</button>
      <button class="il-export-btn" onclick="exportTXT()">{{ t('il_export_txt', lang) }}</button>
      <button class="il-export-btn" onclick="exportCSV()">{{ t('il_export_csv', lang) }}</button>
      <label class="il-translation-toggle">
        <input type="checkbox" id="il-show-trans" checked onchange="toggleTranslation()">
        {{ t('il_translation_toggle', lang) }}
      </label>
    </div>
  </div>

  <div id="il-truncated" class="il-truncated-warn" style="display:none;">
    {{ t('il_truncated_warning', lang) }}
  </div>

  <div id="il-body" class="interlinear-body"></div>

</div>
{% endblock %}

{% block scripts %}
<script>
var LANG = '{{ lang }}';
var TRANS = '{{ trans }}';
var _ilData = null;  // last API response, used by export functions

function parseChVerse(s) {
    // Parse "5:1" or "5" into {ch, v}
    s = s.trim();
    var parts = s.split(':');
    return { ch: parseInt(parts[0]) || 1, v: parseInt(parts[1]) || 1 };
}

function loadInterlinear() {
    var book    = document.getElementById('il-book').value;
    var corpus  = document.getElementById('il-corpus').value;
    var script  = document.getElementById('il-script').value;
    var fromStr = document.getElementById('il-ch-start').value.trim();
    var toStr   = document.getElementById('il-ch-end').value.trim();

    if (!book) { alert('Please select a book.'); return; }
    if (!fromStr) { alert('Please enter a start chapter (e.g. 5:1).'); return; }

    var from = parseChVerse(fromStr);
    var to   = toStr ? parseChVerse(toStr) : { ch: from.ch, v: 9999 };

    // Update Syriac font CSS variable
    var fontMap = { estrangela: "'Noto Sans Syriac', serif",
                    eastern:    "'Noto Sans Syriac Eastern', serif",
                    western:    "'Noto Sans Syriac Western', serif" };
    var font = document.getElementById('il-font').value;
    document.documentElement.style.setProperty('--syriac-font', fontMap[font] || fontMap.estrangela);

    var url = '/api/interlinear?book=' + encodeURIComponent(book)
            + '&ch_start=' + from.ch + '&v_start=' + from.v
            + '&ch_end='   + to.ch   + '&v_end='   + to.v
            + '&corpus=' + encodeURIComponent(corpus)
            + '&script=' + encodeURIComponent(script)
            + '&lang='   + encodeURIComponent(LANG)
            + '&trans='  + encodeURIComponent(TRANS);

    document.getElementById('il-body').innerHTML =
        '<p style="color:var(--muted);padding:1rem;">Loading…</p>';
    document.getElementById('il-action-bar').style.display = 'none';
    document.getElementById('il-nav').style.display = 'none';
    document.getElementById('il-truncated').style.display = 'none';

    fetch(url)
        .then(function(r) { return r.json(); })
        .then(function(data) {
            _ilData = data;
            renderInterlinear(data, book, from.ch, to.ch, script);
        })
        .catch(function(e) {
            document.getElementById('il-body').innerHTML =
                '<p style="color:red;">Error loading data: ' + e.message + '</p>';
        });
}

function confClass(c) {
    if (c >= 0.8) return 'il-root-high';
    if (c >= 0.5) return 'il-root-med';
    if (c > 0)    return 'il-root-low';
    return 'il-root-none';
}

function renderInterlinear(data, book, chStart, chEnd, script) {
    var showTrans = document.getElementById('il-show-trans').checked;
    var rtlScript = (script === 'hebrew' || script === 'arabic');
    var html = '';

    data.verses.forEach(function(v) {
        html += '<div class="interlinear-verse" id="v' + v.chapter + '-' + v.verse + '">';
        html += '<div class="interlinear-ref">' + escHtml(v.ref) + '</div>';
        html += '<div class="interlinear-words">';

        v.words.forEach(function(w) {
            html += '<div class="il-word">';
            // Row 1: Syriac
            html += '<span class="il-syriac">' + escHtml(w.syriac) + '</span>';
            // Row 2: Transliteration
            html += '<span class="il-translit' + (rtlScript ? ' il-rtl-script' : '') + '">'
                  + escHtml(w.translit) + '</span>';
            // Row 3: Gloss
            html += '<span class="il-gloss">' + escHtml(w.gloss || '—') + '</span>';
            // Row 4: Root (linked to visualizer)
            if (w.root) {
                html += '<a class="il-root ' + confClass(w.confidence) + '" '
                      + 'href="/visualize/' + encodeURIComponent(w.root_key) + '?lang=' + LANG + '" '
                      + 'target="_blank" rel="noopener">' + escHtml(w.root) + '</a>';
            } else {
                html += '<span class="il-root il-root-none">—</span>';
            }
            // Row 5: Stem badge (verbal forms only)
            if (w.stem) {
                html += '<span class="il-stem"><span class="stem-badge stem-'
                      + escHtml(w.stem.toLowerCase()) + '" style="font-size:.6rem;">'
                      + escHtml(w.stem) + '</span></span>';
            } else {
                html += '<span class="il-stem"></span>';
            }
            html += '</div>';
        });

        html += '</div>'; // .interlinear-words

        // Translation line
        var transDir = (TRANS === 'he' || TRANS === 'ar') ? ' dir="rtl"' : '';
        html += '<div class="interlinear-translation' + (showTrans ? '' : ' il-trans-hidden') + '"'
              + transDir + '>' + escHtml(v.translation || '') + '</div>';

        html += '</div>'; // .interlinear-verse
    });

    document.getElementById('il-body').innerHTML = html || '<p style="color:var(--muted);">No verses found for this range.</p>';

    // Show/hide truncation warning
    if (data.truncated) {
        document.getElementById('il-truncated').style.display = 'block';
    }

    // Chapter nav
    var navHtml = '';
    if (chStart > 1) {
        var prev = chStart - 1;
        navHtml += '<a href="#" onclick="jumpChapter(' + prev + ');return false;">← Ch ' + prev + '</a>';
    }
    if (chEnd >= chStart) {
        var next = chEnd + 1;
        navHtml += '<a href="#" onclick="jumpChapter(' + next + ');return false;">Ch ' + next + ' →</a>';
    }
    document.getElementById('il-nav').innerHTML = navHtml;
    document.getElementById('il-nav').style.display = navHtml ? 'flex' : 'none';
    document.getElementById('il-action-bar').style.display = 'block';
}

function jumpChapter(ch) {
    document.getElementById('il-ch-start').value = ch + ':1';
    document.getElementById('il-ch-end').value   = ch + ':9999';
    loadInterlinear();
}

function toggleTranslation() {
    var show = document.getElementById('il-show-trans').checked;
    document.querySelectorAll('.interlinear-translation').forEach(function(el) {
        el.classList.toggle('il-trans-hidden', !show);
    });
}

// ── Export functions ────────────────────────────────────────────

function escHtml(s) {
    if (!s) return '';
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function downloadBlob(content, filename, mime) {
    var blob = new Blob([content], { type: mime });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
}

function exportFilename(ext) {
    if (!_ilData) return 'aramaic-atlas-interlinear.' + ext;
    var book = (_ilData.book || 'passage').replace(/\s+/g, '-').toLowerCase();
    return 'aramaic-atlas-interlinear-' + book + '.' + ext;
}

function exportTEI() {
    if (!_ilData || !_ilData.verses.length) return;
    var lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<TEI xmlns="http://www.tei-c.org/ns/1.0">',
        '  <teiHeader><fileDesc><titleStmt>',
        '    <title>Aramaic Root Atlas — Interlinear: ' + escHtml(_ilData.book) + '</title>',
        '  </titleStmt></fileDesc></teiHeader>',
        '  <text><body>',
        '    <div type="book" n="' + escHtml(_ilData.book) + '">'
    ];
    _ilData.verses.forEach(function(v) {
        // Build TEI ab id: e.g. Matt.5.1
        var abId = _ilData.book.replace(/\s+/g, '.') + '.' + v.chapter + '.' + v.verse;
        lines.push('      <ab n="' + escHtml(v.ref) + '" xml:id="' + escHtml(abId) + '">');
        v.words.forEach(function(w, i) {
            var cert = w.confidence >= 0.8 ? 'high' : w.confidence >= 0.5 ? 'medium' : 'low';
            var pos  = w.stem ? 'v' : 'n';
            var attrs = ' xml:id="' + escHtml(abId) + '.' + (i+1) + '"'
                      + (w.root_key ? ' lemma="' + escHtml(w.root_key) + '"' : '')
                      + ' pos="' + pos + '"'
                      + (w.stem ? ' ana="' + escHtml(w.stem) + '"' : '')
                      + (w.root ? ' cert="' + cert + '"' : '');
            lines.push('        <w' + attrs + '>' + escHtml(w.syriac) + '</w>');
        });
        lines.push('      </ab>');
    });
    lines.push('    </div>', '  </body></text>', '</TEI>');
    downloadBlob(lines.join('\n'), exportFilename('xml'), 'application/xml');
}

function exportTXT() {
    if (!_ilData || !_ilData.verses.length) return;
    var lines = [];
    _ilData.verses.forEach(function(v) {
        lines.push('# ' + v.ref);
        v.words.forEach(function(w) {
            lines.push([w.syriac, w.translit, w.gloss, w.root, w.stem || ''].join('\t'));
        });
        if (v.translation) lines.push('= ' + v.translation);
        lines.push('');
    });
    downloadBlob(lines.join('\n'), exportFilename('txt'), 'text/plain;charset=utf-8');
}

function exportCSV() {
    if (!_ilData || !_ilData.verses.length) return;
    var rows = [['book','chapter','verse','position','syriac','translit','root','gloss','stem','confidence']];
    _ilData.verses.forEach(function(v) {
        v.words.forEach(function(w, i) {
            rows.push([
                _ilData.book, v.chapter, v.verse, i+1,
                w.syriac, w.translit, w.root, w.gloss, w.stem || '', w.confidence
            ].map(function(c) { return '"' + String(c||'').replace(/"/g,'""') + '"'; }));
        });
    });
    downloadBlob(rows.map(function(r){return r.join(',');}).join('\n'),
                 exportFilename('csv'), 'text/csv;charset=utf-8');
}

// Keyboard: left/right arrows → prev/next chapter
document.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') return;
    if (!_ilData) return;
    var chStart = parseInt(document.getElementById('il-ch-start').value) || 1;
    var chEnd   = parseInt(document.getElementById('il-ch-end').value)   || chStart;
    if (e.key === 'ArrowLeft')  jumpChapter(chEnd + 1);
    if (e.key === 'ArrowRight') { if (chStart > 1) jumpChapter(chStart - 1); }
});

// Auto-load if initial params are provided
{% if initial_book and initial_ch_start %}
window.addEventListener('DOMContentLoaded', function() { loadInterlinear(); });
{% endif %}
</script>
{% endblock %}
```

- [ ] **Step 2: Verify the page renders**

Visit `http://localhost:5001/interlinear` — page title, control bar, and all dropdowns should appear.

- [ ] **Step 3: Load a passage and verify the word grid**

1. Select "Peshitta NT" corpus, book "Matthew", From `5:1`, To `5:3`
2. Click Analyze
3. Verify: three verse blocks render with Syriac text flowing right-to-left, transliteration row, gloss row, root row (linked), and stem badge for verbal forms

- [ ] **Step 4: Verify Hebrew transliteration font**

1. Switch Script to "Hebrew", click Analyze again
2. The transliteration row should use larger Hebrew characters with RTL direction

- [ ] **Step 5: Verify root links**

Click any root in the word grid — should open `/visualize/<root_key>` in a new tab

- [ ] **Step 6: Verify export**

1. Click "Export TEI XML" — downloads `.xml` file; open it and verify `<w lemma=...>` elements are present
2. Click "Export Plain Text" — downloads `.txt` file; open and verify tab-separated columns
3. Click "Export CSV" — downloads `.csv` file; open and verify header row + data rows

- [ ] **Step 7: Verify chapter navigation**

1. Load Matthew 5:1–5:3
2. Click "Ch 6 →" — reloads with chapter 6
3. Click "← Ch 5" — returns to chapter 5
4. Press ArrowLeft/Right keyboard keys — same navigation

- [ ] **Step 8: Verify truncation warning**

```bash
curl "http://localhost:5001/api/interlinear?book=Psalms&ch_start=1&ch_end=50&lang=en" | python3 -c "import sys,json; d=json.load(sys.stdin); print('truncated:', d['truncated'])"
```

Expected: `truncated: True`

Load Psalms 1–50 in the browser — yellow truncation warning should appear.

- [ ] **Step 9: Commit**

```bash
git add templates/interlinear.html
git commit -m "feat(interlinear): add interlinear reader template with export"
```

---

## Task 6 — Final integration check

- [ ] **Step 1: Verify navbar link appears**

Open `http://localhost:5001` and click the Research dropdown — "Interlinear Reader" should appear after Passage Profile.

- [ ] **Step 2: Verify deep-link URL works**

Visit `http://localhost:5001/interlinear?book=Matthew&ch_start=5&v_start=1&ch_end=5&v_end=12&lang=en` — page should auto-analyze and render on load.

- [ ] **Step 3: Verify multilingual gloss**

Load Matthew 5:1–5 with `lang=es` — glosses in the word cells should be in Spanish where available.

- [ ] **Step 4: Verify Biblical Aramaic corpus**

Select corpus "Biblical Aramaic", book "Daniel", From `2:4`, To `2:7`, Analyze — Hebrew-script Aramaic should render in Syriac font area; transliteration (Latin mode) should show correct Latin transliteration.

- [ ] **Step 5: Final commit**

```bash
git add -p  # confirm nothing stray is staged
git commit -m "feat(interlinear): interlinear reader complete — passage-range, RTL grid, TEI/TXT/CSV export"
```

---

## Self-Review Checklist

- [x] **Spec coverage:**
  - Control bar (book, corpus, from/to, script, font) ✓ Task 5
  - RTL word grid (5 rows per word) ✓ Tasks 4+5
  - `/api/interlinear` endpoint ✓ Task 2
  - Page route + navbar link ✓ Task 3
  - TEI XML export ✓ Task 5 `exportTEI()`
  - Plain text export ✓ Task 5 `exportTXT()`
  - CSV export ✓ Task 5 `exportCSV()`
  - Chapter navigation + keyboard arrows ✓ Task 5
  - 500-verse truncation cap ✓ Task 2
  - Translation toggle ✓ Task 5
  - Deep-link URL auto-load ✓ Task 5
  - Multilingual gloss via `_pick_gloss` ✓ Task 2
  - i18n keys (10 × 4 languages) ✓ Task 1

- [x] **No placeholders:** All steps contain actual code or exact commands.

- [x] **Type consistency:** `_translit_to_dash`, `_extractor.lookup_word_root_with_confidence`, `_extractor.lookup_word_stem`, `_extractor.get_root_gloss`, `_cognate_lookup.lookup_syriac`, `_pick_gloss`, `_corpus.get_chapter_verses` — all used consistently across Tasks 2 and 5, matching existing `app.py` call sites.
