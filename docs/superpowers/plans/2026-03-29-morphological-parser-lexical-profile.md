# Morphological Parser + Passage Lexical Profile — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two scholarly research features: (1) a full morphological word parser that exposes prefix/root/suffix decomposition with grammatical labels and an enhanced reader popover; (2) a passage lexical profile page that gives statistical vocabulary analysis (rarity distribution, stem breakdown, verse density) for any book+chapter range.

**Architecture:** Feature 1 adds label maps to `aramaic_core/affixes.py`, a new `/api/word-parse` Flask endpoint that wires up existing `_word_to_root/stem/score` lookups plus `generate_candidate_stems()`, a standalone `/parse` page, and an AJAX-enhanced word popover in the reader. Feature 2 adds a `/api/passage-profile` endpoint that iterates `get_chapter_verses()` across a chapter range and aggregates root statistics, plus a `passage_profile.html` page with CSS bar charts.

**Tech Stack:** Python/Flask, Jinja2, vanilla JS, CSS custom properties (already established). No new libraries needed — charts are CSS-based following the diachronic.html pattern.

**Spec:** `docs/superpowers/specs/2026-03-29-morphological-parser-lexical-profile-design.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `aramaic_core/affixes.py` | Modify | Add `PROCLITIC_LABELS`, `VERBAL_PREFIX_LABELS`, `SUFFIX_LABELS` dicts + `label_stripping_result()` helper |
| `app.py` | Modify | Add `GET /api/word-parse`, `GET /parse`, `GET /api/passage-profile`, `GET /passage-profile` |
| `templates/parse.html` | Create | Standalone word parser page |
| `templates/passage_profile.html` | Create | Passage lexical profile page |
| `templates/read.html` | Modify | Add `data-word` attribute; replace inline popover JS with AJAX fetch to `/api/word-parse` |
| `templates/base.html` | Modify | Add "Word Parser" and "Passage Profile" links in Research dropdown |
| `static/style.css` | Modify | Add morpheme box styles + widen `.word-popover` max-width |
| `data/i18n.json` | Modify | Add ~30 new keys × 4 languages |
| `tests/conftest.py` | Create | Shared Flask test-client fixture |
| `tests/test_word_parse.py` | Create | Tests for `/api/word-parse` |
| `tests/test_passage_profile.py` | Create | Tests for `/api/passage-profile` |

---

## Task 1 — Test infrastructure + failing tests for `/api/word-parse`

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_word_parse.py`

- [ ] **Step 1: Create `tests/` directory and `conftest.py`**

```python
# tests/conftest.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import app as flask_app


@pytest.fixture(scope='session')
def client():
    flask_app.app.config['TESTING'] = True
    with flask_app.app.test_client() as c:
        yield c
```

- [ ] **Step 2: Write failing tests for `/api/word-parse`**

```python
# tests/test_word_parse.py

def test_word_parse_missing_param_returns_400(client):
    r = client.get('/api/word-parse')
    assert r.status_code == 400
    assert 'error' in r.get_json()


def test_word_parse_empty_param_returns_400(client):
    r = client.get('/api/word-parse?word=')
    assert r.status_code == 400


def test_word_parse_unknown_word_returns_empty_root(client):
    # A nonsense string — no root in the index
    r = client.get('/api/word-parse?word=xyz')
    assert r.status_code == 200
    data = r.get_json()
    assert data['word'] == 'xyz'
    assert data['root'] == ''
    assert data['prefixes'] == []
    assert data['suffixes'] == []
    assert 'gloss_en' in data
    assert 'cognates' in data
    assert 'corpus_attestations' in data


def test_word_parse_response_schema(client):
    # Any Syriac input — even if no root found, shape must match
    r = client.get('/api/word-parse?word=\u072b\u0720\u0721&lang=en')  # ܫܠܡ (sh-l-m bare root form)
    assert r.status_code == 200
    data = r.get_json()
    required_keys = [
        'word', 'script', 'root', 'root_key', 'stem', 'confidence',
        'pos_guess', 'prefixes', 'suffixes',
        'gloss_en', 'gloss_es', 'gloss_he', 'gloss_ar',
        'cognates', 'corpus_attestations',
    ]
    for k in required_keys:
        assert k in data, f'Missing key: {k}'


def test_word_parse_prefix_suffix_structure(client):
    # ܘܫܠܡ = waw-proclitic + root SH-L-M
    # Regardless of whether this exact form is indexed, structure must be correct
    r = client.get('/api/word-parse?word=\u0718\u072b\u0720\u0721')  # ܘܫܠܡ
    data = r.get_json()
    assert r.status_code == 200
    for p in data.get('prefixes', []):
        assert 'char' in p, 'Prefix missing char'
        assert 'label' in p, 'Prefix missing label'
        assert isinstance(p['label'], str)
        assert len(p['label']) > 0
    for s in data.get('suffixes', []):
        assert 'char' in s, 'Suffix missing char'
        assert 'label' in s, 'Suffix missing label'


def test_word_parse_lang_param_returns_correct_gloss_key(client):
    r = client.get('/api/word-parse?word=\u072b\u0720\u0721&lang=es')
    data = r.get_json()
    assert r.status_code == 200
    # gloss_es must be present (even if it equals gloss_en as fallback)
    assert 'gloss_es' in data


def test_word_parse_pos_guess_values(client):
    r = client.get('/api/word-parse?word=\u072b\u0720\u0721')
    data = r.get_json()
    assert data['pos_guess'] in ('verb', 'noun', 'unknown')
```

- [ ] **Step 3: Run tests to confirm they all fail with `404` (route does not exist yet)**

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
python -m pytest tests/test_word_parse.py -v 2>&1 | head -40
```

Expected: All fail. `test_word_parse_missing_param_returns_400` fails because `/api/word-parse` returns 404, not 400.

---

## Task 2 — Add label maps + `label_stripping_result()` to `aramaic_core/affixes.py`

**Files:**
- Modify: `aramaic_core/affixes.py`

- [ ] **Step 1: Add label maps at the bottom of the constant definitions (after the `SUFFIXES` list, before `strip_proclitics`)**

Open `aramaic_core/affixes.py`. After the closing `]` of the `SUFFIXES` list (line ~83) and before `def strip_proclitics`, insert:

```python
# --- Human-readable label maps for morpheme display ---

PROCLITIC_LABELS: dict[str, str] = {
    # Compound proclitics first (2 chars) — must take priority over single
    '\u0718\u0712': 'and in (wb-)',
    '\u0718\u0720': 'and to (wl-)',
    '\u0718\u0721': 'and from (wm-)',
    '\u0718\u0715': 'and of (wd-)',
    '\u0715\u0712': 'that in (db-)',
    '\u0715\u0720': 'that to (dl-)',
    '\u0715\u0721': 'that from (dm-)',
    '\u0720\u0721': 'in order to (lm-)',
    # Single proclitics
    '\u0718': 'conjunction (w-)',
    '\u0715': 'relative/genitive (d-)',
    '\u0712': 'preposition in/with (b-)',
    '\u0720': 'preposition to/for (l-)',
}

VERBAL_PREFIX_LABELS: dict[str, str] = {
    '\u0710\u072B\u072C': 'reflexive (Eshtaphal)',
    '\u0710\u072C': 'reflexive/passive (Ethpeel)',
    '\u072B': 'causative (Shafel sh-)',
    '\u0721': 'participle prefix (m-)',
    '\u0722': 'imperfect 3ms (n-)',
    '\u072C': 'imperfect 2ms/3fs (t-)',
    '\u0710': 'imperfect 1s / Aphel (a-)',
}

SUFFIX_LABELS: dict[str, str] = {
    '\u072C\u0718\u0722': '2mp (-thwn)',
    '\u072C\u071D\u0722': '2fp (-thyn)',
    '\u071D\u072C\u0717': '3ms object (-yth)',
    '\u0722\u0722': '1cp (-nn)',
    '\u0717\u0718\u0722': '3mp possessive (-hwn)',
    '\u0717\u071D\u0722': '3fp possessive (-hyn)',
    '\u071F\u0718\u0722': '2mp possessive (-kwn)',
    '\u071F\u071D\u0722': '2fp possessive (-kyn)',
    '\u0718\u0717\u071D': '3fs possessive (-why)',
    '\u072C\u0717': '3ms possessive (-th)',
    '\u0722\u071D': '1s object (-ny)',
    '\u071D\u0722': 'masc. plural (-yn)',
    '\u072C\u0710': 'feminine/abstract (-tha)',
    '\u0718\u072C\u0710': 'abstract noun (-wtha)',
    '\u0718\u072C\u0717': 'abstract + 3ms (-wth)',
    '\u0717': '3ms/3fs possessive (-h)',
    '\u071D': '1s possessive / construct (-y)',
    '\u071F': '2ms possessive (-k)',
    '\u0722': '3mp / energic (-n)',
    '\u0718': '3mp perfect / plural imperative (-w)',
    '\u072C': '1s/2ms perfect / feminine (-th)',
    '\u0710': 'emphatic state / 3fs (-a)',
}


def label_stripping_result(result: 'StrippingResult') -> dict:
    """Convert a StrippingResult into dicts with human-readable labels.

    Returns:
        {
            'prefixes': [{'char': str, 'label': str}, ...],
            'suffixes': [{'char': str, 'label': str}, ...]
        }
    """
    all_prefix_labels = {**PROCLITIC_LABELS, **VERBAL_PREFIX_LABELS}

    prefixes = []
    for char in result.prefixes_removed:
        label = all_prefix_labels.get(char, char)
        prefixes.append({'char': char, 'label': label})

    suffixes = []
    for char in result.suffixes_removed:
        label = SUFFIX_LABELS.get(char, char)
        suffixes.append({'char': char, 'label': label})

    return {'prefixes': prefixes, 'suffixes': suffixes}
```

- [ ] **Step 2: Verify the new function works in isolation**

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
python3 -c "
from aramaic_core.affixes import generate_candidate_stems, label_stripping_result
candidates = generate_candidate_stems('\u0718\u072b\u0720\u0721')  # ܘܫܠܡ
for c in candidates:
    labeled = label_stripping_result(c)
    print(c.stem, labeled)
"
```

Expected output includes a candidate with `prefixes=[{'char': 'ܘ', 'label': 'conjunction (w-)'}]` and `suffixes=[]`.

- [ ] **Step 3: Commit**

```bash
git add aramaic_core/affixes.py
git commit -m "feat: add affix label maps and label_stripping_result() to affixes.py"
```

---

## Task 3 — Add `/api/word-parse` endpoint to `app.py`

**Files:**
- Modify: `app.py` (add after the existing `api_verse` endpoint, around line 533)

- [ ] **Step 1: Add the endpoint**

In `app.py`, after the `_translit_to_dash` helper function (around line 543), add:

```python
@app.route('/api/word-parse')
def api_word_parse():
    """Full morphological breakdown for a single Syriac/Aramaic word.

    Query params:
        word  — Syriac/Aramaic word string (required)
        lang  — UI language code for gloss selection: en|es|he|ar (default: en)
    """
    _init()
    word = request.args.get('word', '').strip()
    if not word:
        return jsonify({'error': 'Missing word parameter'}), 400
    lang_code = request.args.get('lang', 'en')

    from aramaic_core.affixes import generate_candidate_stems, label_stripping_result
    from aramaic_core.characters import detect_script, SYRIAC_CONSONANTS

    script = detect_script(word)

    # Look up root, stem, confidence from pre-built index
    root_syr = _extractor.lookup_word_root(word)
    stem = _extractor.lookup_word_stem(word)
    conf = _extractor.lookup_word_confidence(word) or 0.0

    # Heuristic POS guess
    _VERBAL_STEMS = frozenset({
        'peal', 'ethpeel', 'pael', 'ethpaal', 'aphel', 'shafel', 'ettaphal'
    })
    stem_lower = (stem or '').lower()
    if stem_lower in _VERBAL_STEMS:
        pos_guess = 'verb'
    elif word.endswith(('\u072C\u0710', '\u071D\u0722', '\u0718\u072C\u0710')):
        # ܬܐ, ܝܢ, ܘܬܐ — common nominal endings
        pos_guess = 'noun'
    else:
        pos_guess = 'unknown'

    # Morpheme decomposition — Syriac script only; requires a known root
    prefixes: list[dict] = []
    suffixes: list[dict] = []
    if root_syr and script == 'syriac':
        candidates = generate_candidate_stems(word)
        root_consonants = frozenset(ch for ch in root_syr if ch in SYRIAC_CONSONANTS)
        best = None
        # Pick the candidate whose remaining stem contains all root consonants
        for cand in candidates:
            cand_consonants = frozenset(ch for ch in cand.stem if ch in SYRIAC_CONSONANTS)
            if root_consonants and root_consonants.issubset(cand_consonants):
                best = cand
                break
        if best is None and candidates:
            best = candidates[0]
        if best:
            labeled = label_stripping_result(best)
            prefixes = labeled['prefixes']
            suffixes = labeled['suffixes']

    # Gloss in all four UI languages (fall back to English)
    cognate = _cognate_lookup.lookup(root_syr) if root_syr else None
    gloss_en = (cognate.gloss_en if cognate else '') or _extractor.get_root_gloss(root_syr or '') or ''
    gloss_es = (cognate.gloss_es if cognate else '') or gloss_en
    gloss_he = (cognate.gloss_he if cognate else '') or gloss_en
    gloss_ar = (cognate.gloss_ar if cognate else '') or gloss_en

    # Hebrew and Arabic cognate display strings
    cognate_data: dict[str, str] = {}
    if cognate:
        if cognate.hebrew:
            cognate_data['hebrew'] = ' / '.join(hw.word for hw in cognate.hebrew[:3])
        if cognate.arabic:
            cognate_data['arabic'] = ' / '.join(aw.word for aw in cognate.arabic[:3])

    # Corpus attestation counts for this root
    corpus_att: dict[str, int] = {}
    if root_syr:
        for entry in _extractor.get_all_roots():
            if entry.root == root_syr:
                corpus_att = dict(entry.corpus_counts)
                break

    root_translit = _translit_to_dash(root_syr) if root_syr else ''

    return jsonify({
        'word': word,
        'script': script,
        'root': root_syr or '',
        'root_key': root_translit,
        'stem': stem or '',
        'confidence': round(conf, 2),
        'pos_guess': pos_guess,
        'prefixes': prefixes,
        'suffixes': suffixes,
        'gloss_en': gloss_en,
        'gloss_es': gloss_es,
        'gloss_he': gloss_he,
        'gloss_ar': gloss_ar,
        'cognates': cognate_data,
        'corpus_attestations': corpus_att,
    })
```

- [ ] **Step 2: Run the word-parse tests — they should now pass**

```bash
python -m pytest tests/test_word_parse.py -v
```

Expected: All 7 tests pass.

- [ ] **Step 3: Quick manual smoke-test**

```bash
python3 -c "
import requests
r = requests.get('http://localhost:5001/api/word-parse?word=\u072b\u0720\u0721&lang=en')
import json; print(json.dumps(r.json(), ensure_ascii=False, indent=2))
" 2>/dev/null || echo "Start server first: python3 app.py"
```

Or if the server isn't running, test with the Flask test client directly:

```bash
python3 -c "
import sys; sys.path.insert(0,'.')
import app
app.app.config['TESTING'] = True
c = app.app.test_client()
r = c.get('/api/word-parse?word=\u072b\u0720\u0721&lang=en')
import json; print(json.dumps(r.get_json(), ensure_ascii=False, indent=2))
"
```

Expected: JSON with `root`, `root_key`, `stem`, `gloss_en`, `cognates`, `corpus_attestations` populated.

- [ ] **Step 4: Commit**

```bash
git add app.py tests/conftest.py tests/test_word_parse.py
git commit -m "feat: add /api/word-parse endpoint with full morpheme breakdown"
```

---

## Task 4 — Add `/parse` page route + `templates/parse.html`

**Files:**
- Modify: `app.py` (add page route)
- Create: `templates/parse.html`

- [ ] **Step 1: Add the page route to `app.py`**

After the `api_word_parse` function you just added, insert:

```python
@app.route('/parse')
def parse_page():
    """Standalone word parser page."""
    lang = _get_lang()
    initial_word = request.args.get('word', '')
    return render_template('parse.html', lang=lang, script=_get_script(),
                           trans=_get_trans(), t=_t_proxy, bn=_bn,
                           initial_word=initial_word)
```

- [ ] **Step 2: Create `templates/parse.html`**

```html
{% extends "base.html" %}
{% block title %}{{ t('parse_title', lang) }} — Aramaic Root Atlas{% endblock %}

{% block content %}
<div class="container" style="max-width:820px;margin:0 auto;padding:1.5rem 1rem;">
    <div style="margin-bottom:1.2rem;">
        <h1 style="font-size:1.6rem;margin:0 0 .4rem;">{{ t('parse_title', lang) }}</h1>
        <p style="color:var(--muted);margin:0;">{{ t('parse_subtitle', lang) }}</p>
    </div>

    <!-- Input row -->
    <div style="display:flex;gap:.5rem;margin-bottom:1.5rem;flex-wrap:wrap;">
        <input type="text" id="parse-input"
               placeholder="{{ t('parse_input_placeholder', lang) }}"
               value="{{ initial_word }}"
               autocomplete="off" spellcheck="false"
               dir="rtl"
               style="flex:1;min-width:200px;padding:.6rem .9rem;font-family:var(--syriac-font);font-size:1.3rem;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--fg);">
        <button onclick="analyzeWord()"
                style="padding:.6rem 1.4rem;background:var(--accent);color:#fff;border:none;border-radius:var(--radius);cursor:pointer;font-weight:600;font-size:.95rem;">
            {{ t('parse_analyze', lang) }}
        </button>
    </div>

    <!-- States -->
    <div id="parse-loading" style="display:none;text-align:center;padding:2rem;color:var(--muted);">
        <span class="material-symbols-outlined" style="font-size:2rem;animation:spin 1s linear infinite;">autorenew</span>
    </div>
    <div id="parse-empty" style="text-align:center;padding:3rem;color:var(--muted);font-style:italic;">
        {{ t('parse_input_placeholder', lang) }}
    </div>

    <!-- Results -->
    <div id="parse-results" style="display:none;">

        <!-- Morpheme row -->
        <div class="stat-card" style="padding:1.2rem;margin-bottom:1rem;">
            <div style="font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:.6rem;">
                {{ t('parse_prefixes', lang) }} · {{ t('parse_root', lang) }} · {{ t('parse_suffixes', lang) }}
            </div>
            <div id="parse-morpheme-row" class="parse-morpheme-row"></div>
        </div>

        <!-- Two-column details -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:.8rem;margin-bottom:1rem;">
            <!-- Gloss + stem + POS + confidence -->
            <div class="stat-card" style="padding:1rem;">
                <div id="parse-gloss" style="font-size:1.05rem;font-style:italic;margin-bottom:.6rem;line-height:1.4;"></div>
                <div style="display:flex;gap:.5rem;flex-wrap:wrap;align-items:center;">
                    <span id="parse-stem-badge"></span>
                    <span id="parse-pos" style="font-size:.78rem;background:var(--border);padding:2px 8px;border-radius:4px;color:var(--muted);"></span>
                    <span id="parse-conf-dot" class="wp-conf"></span>
                    <span id="parse-conf-label" style="font-size:.78rem;color:var(--muted);"></span>
                </div>
            </div>
            <!-- Cognates + corpus attestations -->
            <div class="stat-card" style="padding:1rem;">
                <div style="font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.4rem;">
                    {{ t('parse_cognates', lang) }}
                </div>
                <div id="parse-cognates" style="font-size:.9rem;margin-bottom:.7rem;direction:rtl;text-align:right;font-family:var(--syriac-font);"></div>
                <div id="parse-corpus" style="font-size:.78rem;color:var(--muted);line-height:1.6;"></div>
            </div>
        </div>

        <!-- Actions -->
        <div style="display:flex;gap:.5rem;flex-wrap:wrap;align-items:center;">
            <button id="parse-copy-btn" onclick="copyGloss()"
                    style="padding:.4rem .9rem;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--fg);cursor:pointer;font-size:.85rem;">
                {{ t('parse_copy_gloss', lang) }}
            </button>
            <a id="parse-viz-link" href="#"
               style="padding:.4rem .9rem;border:1px solid var(--border);border-radius:var(--radius);color:var(--accent);text-decoration:none;font-size:.85rem;">
                {{ t('visualize', lang) if t else 'Visualize Root' }} →
            </a>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
(function() {
    var LANG = {{ lang|tojson }};
    var _parseData = null;

    function escHtml(s) {
        return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    function confTier(c) {
        if (c >= 0.8) return {cls: 'conf-high', label: 'High'};
        if (c >= 0.5) return {cls: 'conf-med', label: 'Medium'};
        return {cls: 'conf-low', label: 'Low'};
    }

    window.analyzeWord = function() {
        var word = document.getElementById('parse-input').value.trim();
        if (!word) return;

        document.getElementById('parse-empty').style.display = 'none';
        document.getElementById('parse-results').style.display = 'none';
        document.getElementById('parse-loading').style.display = 'block';

        fetch('/api/word-parse?word=' + encodeURIComponent(word) + '&lang=' + LANG)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                _parseData = data;
                renderResults(data);
            })
            .catch(function() {
                document.getElementById('parse-loading').style.display = 'none';
                document.getElementById('parse-empty').style.display = 'block';
            });
    };

    function renderResults(data) {
        document.getElementById('parse-loading').style.display = 'none';

        // Morpheme boxes
        var morphRow = document.getElementById('parse-morpheme-row');
        morphRow.innerHTML = '';

        function makeBox(char, label, cssClass) {
            var div = document.createElement('div');
            div.className = 'wp-morph ' + cssClass;
            div.title = label;
            div.innerHTML =
                '<span class="wp-morph-char" dir="rtl">' + escHtml(char) + '</span>' +
                '<span class="wp-morph-label">' + escHtml(label) + '</span>';
            return div;
        }

        data.prefixes.forEach(function(p) {
            morphRow.appendChild(makeBox(p.char, p.label, 'wp-prefix'));
        });
        if (data.root) {
            morphRow.appendChild(makeBox(data.root, data.root_key, 'wp-root-box'));
        }
        data.suffixes.forEach(function(s) {
            morphRow.appendChild(makeBox(s.char, s.label, 'wp-suffix'));
        });
        if (!data.root && data.prefixes.length === 0 && data.suffixes.length === 0) {
            morphRow.innerHTML = '<span style="color:var(--muted);font-style:italic;font-size:.9rem;">No root identified for this word.</span>';
        }

        // Gloss
        var gloss = data['gloss_' + LANG] || data.gloss_en || '';
        document.getElementById('parse-gloss').textContent = gloss || '—';

        // Stem badge
        var stemEl = document.getElementById('parse-stem-badge');
        stemEl.className = data.stem ? 'stem-badge stem-' + data.stem.toLowerCase() : '';
        stemEl.textContent = data.stem || '';

        // POS
        document.getElementById('parse-pos').textContent = data.pos_guess !== 'unknown' ? data.pos_guess : '';

        // Confidence
        var tier = confTier(data.confidence);
        document.getElementById('parse-conf-dot').className = 'wp-conf ' + tier.cls;
        document.getElementById('parse-conf-label').textContent = tier.label;

        // Cognates
        var cogParts = [];
        if (data.cognates.hebrew) cogParts.push(data.cognates.hebrew);
        if (data.cognates.arabic) cogParts.push(data.cognates.arabic);
        document.getElementById('parse-cognates').textContent = cogParts.join(' · ') || '—';

        // Corpus attestations
        var corpNames = {
            peshitta_nt: 'Pesh. NT',
            peshitta_ot: 'Pesh. OT',
            biblical_aramaic: 'Bibl. Aram.',
            targum_onkelos: 'Targ. Onk.'
        };
        var corpParts = [];
        Object.keys(data.corpus_attestations).forEach(function(k) {
            if (data.corpus_attestations[k] > 0) {
                corpParts.push((corpNames[k] || k) + ': ' + data.corpus_attestations[k]);
            }
        });
        document.getElementById('parse-corpus').textContent = corpParts.join(' · ');

        // Viz link
        if (data.root_key) {
            document.getElementById('parse-viz-link').href =
                '/visualize/' + encodeURIComponent(data.root_key) + '?lang=' + LANG;
            document.getElementById('parse-viz-link').style.display = '';
        } else {
            document.getElementById('parse-viz-link').style.display = 'none';
        }

        document.getElementById('parse-results').style.display = 'block';
    }

    window.copyGloss = function() {
        if (!_parseData) return;
        var word = _parseData.word;
        var gloss = _parseData['gloss_' + LANG] || _parseData.gloss_en || '?';
        var morphemes = [];
        _parseData.prefixes.forEach(function(p) {
            morphemes.push(p.label.split('(')[0].trim().toUpperCase().replace(/\s+/g, '.'));
        });
        morphemes.push(_parseData.root_key || '\u221a');
        _parseData.suffixes.forEach(function(s) {
            morphemes.push(s.label.split('(')[0].trim().toUpperCase().replace(/\s+/g, '.'));
        });
        var text = word + '\n' + morphemes.join('-') + '\n"' + gloss + '"';
        navigator.clipboard.writeText(text).then(function() {
            var btn = document.getElementById('parse-copy-btn');
            var orig = btn.textContent;
            btn.textContent = '\u2713 Copied';
            setTimeout(function() { btn.textContent = orig; }, 1500);
        });
    };

    document.getElementById('parse-input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') analyzeWord();
    });

    {% if initial_word %}
    document.addEventListener('DOMContentLoaded', function() { analyzeWord(); });
    {% endif %}
})();
</script>
{% endblock %}
```

- [ ] **Step 3: Verify the page route loads**

```bash
python3 -c "
import app
app.app.config['TESTING'] = True
c = app.app.test_client()
r = c.get('/parse?lang=en')
print(r.status_code)  # expect 200
"
```

- [ ] **Step 4: Commit**

```bash
git add app.py templates/parse.html
git commit -m "feat: add standalone /parse word parser page"
```

---

## Task 5 — CSS morpheme boxes + enhanced AJAX popover in `read.html`

**Files:**
- Modify: `static/style.css` (add morpheme styles)
- Modify: `templates/read.html` (add `data-word` attr; replace popover JS)

- [ ] **Step 1: Add morpheme box CSS to `static/style.css`**

At the end of the file, append:

```css
/* ============================================================
   Morpheme boxes (word-parse popover + parse page)
   ============================================================ */

.word-popover {
    max-width: 380px;  /* was 280px */
}

.parse-morpheme-row,
.wp-morphemes {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
    direction: rtl;
}

.wp-morph {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 4px 7px;
    border-radius: 5px;
    min-width: 32px;
    text-align: center;
}

.wp-morph-char {
    font-family: var(--syriac-font);
    font-size: 1.15rem;
    font-weight: 600;
    line-height: 1.2;
}

.wp-morph-label {
    font-size: 0.58rem;
    color: var(--muted);
    line-height: 1.3;
    max-width: 72px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    direction: ltr;
    text-align: center;
}

.wp-prefix {
    background: rgba(0, 150, 136, 0.12);
    border: 1px solid rgba(0, 150, 136, 0.35);
}

.wp-root-box {
    background: rgba(255, 160, 0, 0.15);
    border: 1px solid rgba(255, 160, 0, 0.45);
}

.wp-suffix {
    background: rgba(103, 58, 183, 0.12);
    border: 1px solid rgba(103, 58, 183, 0.35);
}

.wp-morphemes {
    margin-bottom: 0.5rem;
}

.wp-meta {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin: 0.3rem 0;
}

.wp-cognates-row {
    font-size: 0.75rem;
    color: var(--muted);
    margin-bottom: 0.3rem;
    direction: rtl;
    font-family: var(--syriac-font);
}

.wp-loading {
    font-size: 0.78rem;
    color: var(--muted);
    font-style: italic;
    padding: 0.3rem 0;
}
```

- [ ] **Step 2: Add `data-word` attribute to word tokens in `templates/read.html`**

Find the word-token `<span>` around line 41–43:

```html
<span class="word-token{% if w == hl_form %} hl{% endif %}{% if wr %} has-root{% endif %}"
      {% if wr %}data-root="{{ wr.r }}" data-translit="{{ wr.t }}" data-gloss="{{ wr.g }}" data-conf="{{ wr.c }}" data-stem="{{ wr.s }}"{% endif %}
```

Replace `{% if wr %}data-root=...{% endif %}` with:

```html
<span class="word-token{% if w == hl_form %} hl{% endif %}{% if wr %} has-root{% endif %}"
      data-word="{{ w }}"
      {% if wr %}data-root="{{ wr.r }}" data-translit="{{ wr.t }}" data-gloss="{{ wr.g }}" data-conf="{{ wr.c }}" data-stem="{{ wr.s }}"{% endif %}
```

- [ ] **Step 3: Replace the word popover JS block in `templates/read.html`**

Find the block starting at `// --- Word popover for root info ---` (around line 210) through the closing `})();` of that IIFE (around line 270). Replace the entire block with:

```javascript
// --- Word popover for root info (AJAX morpheme breakdown) ---
(function() {
    var popover = document.createElement('div');
    popover.className = 'word-popover';
    popover.style.display = 'none';
    document.body.appendChild(popover);

    var LANG = {{ lang|tojson }};
    var _cache = {};

    function escHtml(s) {
        return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    function confTier(c) {
        if (c >= 0.8) return {cls: 'conf-high', label: 'High'};
        if (c >= 0.5) return {cls: 'conf-med', label: 'Medium'};
        return {cls: 'conf-low', label: 'Low'};
    }

    function positionPopover(token) {
        var rect = token.getBoundingClientRect();
        popover.style.display = 'block';
        var popRect = popover.getBoundingClientRect();
        var top = rect.bottom + window.scrollY + 6;
        var left = rect.left + window.scrollX + (rect.width / 2) - (popRect.width / 2);
        if (left < 8) left = 8;
        if (left + popRect.width > window.innerWidth - 8) left = window.innerWidth - popRect.width - 8;
        popover.style.top = top + 'px';
        popover.style.left = left + 'px';
    }

    function buildQuickHtml(token) {
        var root = token.getAttribute('data-root') || '';
        var translit = token.getAttribute('data-translit') || '';
        var gloss = token.getAttribute('data-gloss') || '';
        var conf = parseFloat(token.getAttribute('data-conf') || '0');
        var stem = token.getAttribute('data-stem') || '';
        var tier = confTier(conf);
        var html = '<div class="wp-header">';
        html += '<span class="wp-root" dir="rtl">' + escHtml(root) + '</span>';
        html += '<span class="wp-translit">' + escHtml(translit) + '</span>';
        html += '<span class="wp-conf ' + tier.cls + '" title="' + tier.label + '"></span>';
        html += '</div>';
        if (gloss) html += '<div class="wp-gloss">' + escHtml(gloss) + '</div>';
        if (stem) html += '<div class="wp-meta"><span class="stem-badge stem-' + stem.toLowerCase() + '">' + escHtml(stem) + '</span></div>';
        html += '<div class="wp-loading">Loading morphemes\u2026</div>';
        var vizUrl = '/visualize/' + encodeURIComponent(translit) + '?lang=' + LANG;
        html += '<div class="wp-actions"><a href="' + vizUrl + '" class="wp-link">{{ t("visualize", lang) if t else "Visualize" }}</a></div>';
        return html;
    }

    function buildFullHtml(data) {
        var html = '';
        // Morpheme boxes
        var hasPre = data.prefixes && data.prefixes.length > 0;
        var hasSuf = data.suffixes && data.suffixes.length > 0;
        if (hasPre || data.root || hasSuf) {
            html += '<div class="wp-morphemes">';
            (data.prefixes || []).forEach(function(p) {
                html += '<div class="wp-morph wp-prefix" title="' + escHtml(p.label) + '">';
                html += '<span class="wp-morph-char" dir="rtl">' + escHtml(p.char) + '</span>';
                html += '<span class="wp-morph-label">' + escHtml(p.label) + '</span></div>';
            });
            if (data.root) {
                html += '<div class="wp-morph wp-root-box">';
                html += '<span class="wp-morph-char" dir="rtl">' + escHtml(data.root) + '</span>';
                html += '<span class="wp-morph-label">' + escHtml(data.root_key) + '</span></div>';
            }
            (data.suffixes || []).forEach(function(s) {
                html += '<div class="wp-morph wp-suffix" title="' + escHtml(s.label) + '">';
                html += '<span class="wp-morph-char" dir="rtl">' + escHtml(s.char) + '</span>';
                html += '<span class="wp-morph-label">' + escHtml(s.label) + '</span></div>';
            });
            html += '</div>';
        }
        // Gloss
        var gloss = data['gloss_' + LANG] || data.gloss_en || '';
        if (gloss) html += '<div class="wp-gloss">' + escHtml(gloss) + '</div>';
        // Stem + confidence
        var tier = confTier(data.confidence);
        html += '<div class="wp-meta">';
        if (data.stem) html += '<span class="stem-badge stem-' + data.stem.toLowerCase() + '">' + escHtml(data.stem) + '</span>';
        html += '<span class="wp-conf ' + tier.cls + '" title="' + tier.label + '"></span>';
        html += '</div>';
        // Cognates
        var cogParts = [];
        if (data.cognates && data.cognates.hebrew) cogParts.push(data.cognates.hebrew);
        if (data.cognates && data.cognates.arabic) cogParts.push(data.cognates.arabic);
        if (cogParts.length) html += '<div class="wp-cognates-row">' + escHtml(cogParts.join(' · ')) + '</div>';
        // Actions
        var vizUrl = '/visualize/' + encodeURIComponent(data.root_key || '') + '?lang=' + LANG;
        var parseUrl = '/parse?word=' + encodeURIComponent(data.word) + '&lang=' + LANG;
        html += '<div class="wp-actions">';
        if (data.root_key) html += '<a href="' + vizUrl + '" class="wp-link">{{ t("visualize", lang) if t else "Visualize" }}</a>';
        html += '<a href="' + parseUrl + '" class="wp-link">{{ t("parse_title", lang) if t else "Parse" }}</a>';
        html += '</div>';
        return html;
    }

    document.addEventListener('click', function(e) {
        var token = e.target.closest('.word-token.has-root');
        if (!token) { popover.style.display = 'none'; return; }
        e.stopPropagation();

        // Show quick version immediately from data-attributes
        popover.innerHTML = buildQuickHtml(token);
        positionPopover(token);

        // Then fetch full morpheme breakdown
        var word = token.getAttribute('data-word') || token.textContent.trim();
        var cacheKey = word + '_' + LANG;
        if (_cache[cacheKey]) {
            popover.innerHTML = buildFullHtml(_cache[cacheKey]);
            positionPopover(token);
            return;
        }
        fetch('/api/word-parse?word=' + encodeURIComponent(word) + '&lang=' + LANG)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                _cache[cacheKey] = data;
                if (popover.style.display === 'block') {
                    popover.innerHTML = buildFullHtml(data);
                    positionPopover(token);
                }
            });
        // On fetch error, the quick version stays visible
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') popover.style.display = 'none';
    });
})();
```

- [ ] **Step 4: Verify template renders**

```bash
python3 -c "
import app
app.app.config['TESTING'] = True
c = app.app.test_client()
r = c.get('/read/Matthew/5?lang=en')
assert r.status_code == 200
assert b'data-word' in r.data
assert b'api/word-parse' in r.data
print('OK')
"
```

- [ ] **Step 5: Commit**

```bash
git add static/style.css templates/read.html
git commit -m "feat: add morpheme box CSS + AJAX-enhanced word popover in reader"
```

---

## Task 6 — Failing tests for `/api/passage-profile`

**Files:**
- Create: `tests/test_passage_profile.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_passage_profile.py

def test_passage_profile_missing_book_returns_400(client):
    r = client.get('/api/passage-profile?ch_start=1&ch_end=1')
    assert r.status_code == 400
    assert 'error' in r.get_json()


def test_passage_profile_invalid_chapter_returns_400(client):
    r = client.get('/api/passage-profile?book=Matthew&ch_start=notanumber')
    assert r.status_code == 400


def test_passage_profile_nonexistent_book_returns_404(client):
    r = client.get('/api/passage-profile?book=FakeBook&ch_start=1&ch_end=1')
    assert r.status_code == 404


def test_passage_profile_single_chapter_shape(client):
    r = client.get('/api/passage-profile?book=Matthew&ch_start=1&ch_end=1')
    assert r.status_code == 200
    data = r.get_json()
    assert data['verse_count'] > 0
    assert data['word_count'] > 0
    assert data['unique_roots'] > 0
    assert 0.0 < data['lexical_density'] < 1.0
    assert 'hapax_in_passage' in data
    assert 'corpus_hapaxes' in data
    assert set(data['rarity_buckets'].keys()) == {'hapax', 'rare', 'common', 'very_common'}
    assert isinstance(data['stem_distribution'], dict)
    assert isinstance(data['top_roots'], list)
    assert len(data['top_roots']) <= 15
    assert isinstance(data['verse_density'], list)
    assert len(data['verse_density']) == data['verse_count']
    assert set(data['confidence_dist'].keys()) == {'high', 'medium', 'low'}


def test_passage_profile_top_roots_structure(client):
    r = client.get('/api/passage-profile?book=Matthew&ch_start=1&ch_end=1')
    data = r.get_json()
    for entry in data['top_roots']:
        assert 'root' in entry
        assert 'root_key' in entry
        assert 'gloss' in entry
        assert 'passage_count' in entry
        assert 'corpus_total' in entry
        assert entry['passage_count'] >= 1


def test_passage_profile_verse_density_structure(client):
    r = client.get('/api/passage-profile?book=Matthew&ch_start=1&ch_end=1')
    data = r.get_json()
    for entry in data['verse_density']:
        assert 'ref' in entry
        assert 'root_count' in entry
        assert 'unique' in entry


def test_passage_profile_multi_chapter(client):
    r = client.get('/api/passage-profile?book=Matthew&ch_start=5&ch_end=7')
    data = r.get_json()
    assert r.status_code == 200
    assert data['verse_count'] > 50  # Sermon on the Mount is ~109 verses
    assert data['unique_roots'] > 100


def test_passage_profile_hapax_count_consistent(client):
    r = client.get('/api/passage-profile?book=Matthew&ch_start=1&ch_end=1')
    data = r.get_json()
    # hapax_in_passage must be <= unique_roots
    assert data['hapax_in_passage'] <= data['unique_roots']
    # corpus_hapaxes must be <= unique_roots
    assert data['corpus_hapaxes'] <= data['unique_roots']
    # rarity buckets must sum to unique_roots
    bucket_sum = sum(data['rarity_buckets'].values())
    assert bucket_sum == data['unique_roots']
```

- [ ] **Step 2: Run to confirm all fail with 404**

```bash
python -m pytest tests/test_passage_profile.py -v 2>&1 | head -40
```

Expected: All fail — route does not exist.

---

## Task 7 — Add `/api/passage-profile` endpoint to `app.py`

**Files:**
- Modify: `app.py` (add after the `parse_page` route)

- [ ] **Step 1: Add the endpoint**

After the `parse_page` function, insert:

```python
@app.route('/api/passage-profile')
def api_passage_profile():
    """Lexical statistics for a passage (book + chapter range).

    Query params:
        book      — book name matching corpus (e.g. "Matthew")  [required]
        ch_start  — first chapter number (int)                  [required]
        ch_end    — last chapter number (int, default=ch_start)
        v_start   — first verse in ch_start (int, optional)
        v_end     — last verse in ch_end (int, optional)
        corpus    — corpus filter: peshitta_nt|peshitta_ot|etc (optional)
        lang      — gloss language: en|es|he|ar (default: en)
    """
    _init()
    book = request.args.get('book', '').strip()
    if not book:
        return jsonify({'error': 'Missing book parameter'}), 400
    try:
        ch_start = int(request.args.get('ch_start', 1))
        ch_end = int(request.args.get('ch_end', ch_start))
    except ValueError:
        return jsonify({'error': 'ch_start and ch_end must be integers'}), 400

    v_start = None
    v_end = None
    try:
        if request.args.get('v_start'):
            v_start = int(request.args.get('v_start'))
        if request.args.get('v_end'):
            v_end = int(request.args.get('v_end'))
    except ValueError:
        pass  # ignore malformed optional verse range

    corpus_filter = request.args.get('corpus', '').strip() or None
    lang_code = request.args.get('lang', 'en')

    # --- Collect all verses in the requested range ---
    verse_texts: list[tuple[str, str]] = []  # [(ref, syriac_text)]
    for ch in range(ch_start, ch_end + 1):
        ch_verses = _corpus.get_chapter_verses(book, ch, corpus_filter)
        for v_num, ref, text in ch_verses:
            if ch == ch_start and v_start is not None and v_num < v_start:
                continue
            if ch == ch_end and v_end is not None and v_num > v_end:
                continue
            verse_texts.append((ref, text))

    if not verse_texts:
        return jsonify({'error': f'No verses found for {book} {ch_start}–{ch_end}'}), 404

    # --- Build corpus-wide root frequency dict for rarity classification ---
    root_total_occ: dict[str, int] = {
        entry.root: entry.total_occurrences
        for entry in _extractor.get_all_roots()
    }

    # --- Aggregate per root within this passage ---
    passage_root_counts: dict[str, int] = {}
    verse_density: list[dict] = []
    total_words = 0
    stem_dist: dict[str, int] = {}
    conf_dist = {'high': 0, 'medium': 0, 'low': 0}

    for ref, text in verse_texts:
        words = text.split()
        verse_root_set: set[str] = set()
        verse_root_count = 0
        for w in words:
            root_syr = _extractor.lookup_word_root(w)
            if root_syr is None:
                continue  # stopwords and unanalyzed forms return None
            total_words += 1
            passage_root_counts[root_syr] = passage_root_counts.get(root_syr, 0) + 1
            verse_root_set.add(root_syr)
            verse_root_count += 1
            stem_lbl = (_extractor.lookup_word_stem(w) or 'unknown').lower()
            stem_dist[stem_lbl] = stem_dist.get(stem_lbl, 0) + 1
            conf = _extractor.lookup_word_confidence(w) or 0.5
            if conf >= 0.8:
                conf_dist['high'] += 1
            elif conf >= 0.5:
                conf_dist['medium'] += 1
            else:
                conf_dist['low'] += 1
        verse_density.append({
            'ref': ref,
            'root_count': verse_root_count,
            'unique': len(verse_root_set),
        })

    unique_roots = len(passage_root_counts)
    lexical_density = round(unique_roots / total_words, 4) if total_words else 0.0

    # --- Computed metrics ---
    hapax_in_passage = sum(1 for c in passage_root_counts.values() if c == 1)
    corpus_hapaxes = sum(
        1 for r in passage_root_counts
        if root_total_occ.get(r, 0) <= 1
    )

    rarity_buckets = {'hapax': 0, 'rare': 0, 'common': 0, 'very_common': 0}
    for root_syr in passage_root_counts:
        total = root_total_occ.get(root_syr, 0)
        if total <= 1:
            rarity_buckets['hapax'] += 1
        elif total <= 5:
            rarity_buckets['rare'] += 1
        elif total <= 20:
            rarity_buckets['common'] += 1
        else:
            rarity_buckets['very_common'] += 1

    # --- Top 15 roots by passage frequency ---
    top_roots_raw = sorted(passage_root_counts.items(), key=lambda x: x[1], reverse=True)[:15]
    top_roots = []
    for root_syr, count in top_roots_raw:
        root_translit = _translit_to_dash(root_syr)
        cognate = _cognate_lookup.lookup(root_syr)
        gloss = _pick_gloss(cognate, lang_code) if cognate else _extractor.get_root_gloss(root_syr) or ''
        top_roots.append({
            'root': root_syr,
            'root_key': root_translit,
            'gloss': gloss,
            'passage_count': count,
            'corpus_total': root_total_occ.get(root_syr, 0),
        })

    # --- Semantic field distribution (graceful if not loaded) ---
    sf_dist: dict[str, int] = {}
    if _semantic_fields:
        for root_syr, count in passage_root_counts.items():
            key = _translit_to_dash(root_syr).lower()
            for domain in _semantic_fields.get(key, []):
                sf_dist[domain] = sf_dist.get(domain, 0) + count

    # --- Passage label ---
    if ch_start == ch_end:
        passage_label = f'{book} {ch_start}'
    else:
        passage_label = f'{book} {ch_start}\u2013{ch_end}'

    return jsonify({
        'passage': passage_label,
        'verse_count': len(verse_texts),
        'word_count': total_words,
        'unique_roots': unique_roots,
        'lexical_density': lexical_density,
        'hapax_in_passage': hapax_in_passage,
        'corpus_hapaxes': corpus_hapaxes,
        'rarity_buckets': rarity_buckets,
        'stem_distribution': stem_dist,
        'top_roots': top_roots,
        'semantic_fields': sf_dist,
        'verse_density': verse_density,
        'confidence_dist': conf_dist,
    })
```

- [ ] **Step 2: Run the passage-profile tests**

```bash
python -m pytest tests/test_passage_profile.py -v
```

Expected: All 8 tests pass.

- [ ] **Step 3: Run the full test suite to confirm no regressions**

```bash
python -m pytest tests/ -v
```

Expected: All 15 tests pass (7 word-parse + 8 passage-profile).

- [ ] **Step 4: Commit**

```bash
git add app.py tests/test_passage_profile.py
git commit -m "feat: add /api/passage-profile endpoint for passage lexical statistics"
```

---

## Task 8 — Add `/passage-profile` page route + `templates/passage_profile.html`

**Files:**
- Modify: `app.py` (add page route)
- Create: `templates/passage_profile.html`

- [ ] **Step 1: Add the page route to `app.py`**

After the `api_passage_profile` function, insert:

```python
@app.route('/passage-profile')
def passage_profile_page():
    """Passage lexical profile analysis page."""
    _init()
    lang = _get_lang()
    books = _corpus.get_books()
    initial_book = request.args.get('book', '')
    initial_ch_start = request.args.get('ch_start', '')
    initial_ch_end = request.args.get('ch_end', '')
    return render_template('passage_profile.html', lang=lang, script=_get_script(),
                           trans=_get_trans(), t=_t_proxy, bn=_bn,
                           books=books,
                           initial_book=initial_book,
                           initial_ch_start=initial_ch_start,
                           initial_ch_end=initial_ch_end)
```

- [ ] **Step 2: Create `templates/passage_profile.html`**

```html
{% extends "base.html" %}
{% block title %}{{ t('pp_title', lang) }} — Aramaic Root Atlas{% endblock %}

{% block content %}
<div class="container" style="max-width:1000px;margin:0 auto;padding:1.5rem 1rem;">
    <div style="margin-bottom:1.2rem;">
        <h1 style="font-size:1.6rem;margin:0 0 .4rem;">{{ t('pp_title', lang) }}</h1>
        <p style="color:var(--muted);margin:0;">{{ t('pp_subtitle', lang) }}</p>
    </div>

    <!-- Controls -->
    <div style="display:flex;gap:.5rem;flex-wrap:wrap;align-items:flex-end;margin-bottom:1.5rem;padding:1rem;background:var(--card-bg);border:1px solid var(--border);border-radius:var(--radius);">
        <div>
            <label style="font-size:.75rem;color:var(--muted);display:block;margin-bottom:.2rem;">{{ t('pp_book_label', lang) }}</label>
            <select id="pp-book" style="padding:.4rem .7rem;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--fg);min-width:140px;">
                {% for b_name, b_ch in books %}
                <option value="{{ b_name }}" {% if b_name == initial_book %}selected{% endif %}>{{ bn(b_name, lang) }}</option>
                {% endfor %}
            </select>
        </div>
        <div>
            <label style="font-size:.75rem;color:var(--muted);display:block;margin-bottom:.2rem;">{{ t('pp_chapter_from', lang) }}</label>
            <input type="number" id="pp-ch-start" min="1" value="{{ initial_ch_start or 1 }}"
                   style="width:70px;padding:.4rem .6rem;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--fg);">
        </div>
        <div>
            <label style="font-size:.75rem;color:var(--muted);display:block;margin-bottom:.2rem;">{{ t('pp_chapter_to', lang) }}</label>
            <input type="number" id="pp-ch-end" min="1" value="{{ initial_ch_end or 1 }}"
                   style="width:70px;padding:.4rem .6rem;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--fg);">
        </div>
        <button onclick="runProfile()"
                style="padding:.45rem 1.3rem;background:var(--accent);color:#fff;border:none;border-radius:var(--radius);cursor:pointer;font-weight:600;align-self:flex-end;">
            {{ t('pp_analyze', lang) }}
        </button>
    </div>

    <!-- Loading / empty -->
    <div id="pp-loading" style="display:none;text-align:center;padding:2rem;color:var(--muted);">
        <span class="material-symbols-outlined" style="font-size:2rem;animation:spin 1s linear infinite;">autorenew</span>
    </div>
    <div id="pp-empty" style="text-align:center;padding:3rem;color:var(--muted);font-style:italic;">
        {{ t('pp_subtitle', lang) }}
    </div>

    <!-- Results -->
    <div id="pp-results" style="display:none;">

        <!-- Passage label -->
        <div style="margin-bottom:1rem;">
            <span id="pp-passage-label" style="font-size:1.1rem;font-weight:600;"></span>
        </div>

        <!-- Summary stat cards -->
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:.7rem;margin-bottom:1.2rem;">
            <div class="stat-card" style="padding:.9rem;text-align:center;">
                <div id="pp-stat-unique" style="font-size:1.8rem;font-weight:700;color:var(--accent);"></div>
                <div style="font-size:.75rem;color:var(--muted);">{{ t('pp_unique_roots', lang) }}</div>
            </div>
            <div class="stat-card" style="padding:.9rem;text-align:center;">
                <div id="pp-stat-density" style="font-size:1.8rem;font-weight:700;color:var(--accent);"></div>
                <div style="font-size:.75rem;color:var(--muted);">{{ t('pp_lexical_density', lang) }}</div>
            </div>
            <div class="stat-card" style="padding:.9rem;text-align:center;">
                <div id="pp-stat-hapax" style="font-size:1.8rem;font-weight:700;color:var(--accent);"></div>
                <div style="font-size:.75rem;color:var(--muted);">{{ t('pp_passage_hapaxes', lang) }}</div>
            </div>
            <div class="stat-card" style="padding:.9rem;text-align:center;">
                <div id="pp-stat-corpus-hapax" style="font-size:1.8rem;font-weight:700;color:var(--accent);"></div>
                <div style="font-size:.75rem;color:var(--muted);">{{ t('pp_corpus_hapaxes', lang) }}</div>
            </div>
        </div>

        <!-- Charts row -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:.8rem;margin-bottom:1.2rem;">
            <!-- Rarity distribution -->
            <div class="stat-card" style="padding:1rem;">
                <div style="font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.7rem;">{{ t('pp_rarity_dist', lang) }}</div>
                <div id="pp-rarity-chart"></div>
            </div>
            <!-- Stem distribution -->
            <div class="stat-card" style="padding:1rem;">
                <div style="font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.7rem;">{{ t('pp_stem_dist', lang) }}</div>
                <div id="pp-stem-chart"></div>
            </div>
        </div>

        <!-- Verse density chart -->
        <div class="stat-card" style="padding:1rem;margin-bottom:1.2rem;">
            <div style="font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.7rem;">{{ t('pp_verse_density', lang) }}</div>
            <div id="pp-density-chart" style="overflow-x:auto;"></div>
        </div>

        <!-- Bottom two-column: top roots + semantic domains -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:.8rem;margin-bottom:1.2rem;">
            <!-- Top 15 roots table -->
            <div class="stat-card" style="padding:1rem;">
                <div style="font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.7rem;">{{ t('pp_top_roots', lang) }}</div>
                <table style="width:100%;border-collapse:collapse;font-size:.85rem;">
                    <thead>
                        <tr style="border-bottom:1px solid var(--border);">
                            <th style="text-align:left;padding:.3rem .4rem;color:var(--muted);font-size:.72rem;text-transform:uppercase;">{{ t('pp_col_root', lang) }}</th>
                            <th style="text-align:left;padding:.3rem .4rem;color:var(--muted);font-size:.72rem;text-transform:uppercase;">{{ t('pp_col_gloss', lang) }}</th>
                            <th style="text-align:right;padding:.3rem .4rem;color:var(--muted);font-size:.72rem;text-transform:uppercase;">{{ t('pp_col_freq', lang) }}</th>
                            <th style="text-align:right;padding:.3rem .4rem;color:var(--muted);font-size:.72rem;text-transform:uppercase;">{{ t('pp_col_rarity', lang) }}</th>
                        </tr>
                    </thead>
                    <tbody id="pp-roots-tbody"></tbody>
                </table>
            </div>
            <!-- Semantic domains -->
            <div class="stat-card" style="padding:1rem;">
                <div style="font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.7rem;">{{ t('pp_semantic_domains', lang) }}</div>
                <div id="pp-domains-chart"></div>
                <div id="pp-no-domains" style="display:none;font-size:.8rem;color:var(--muted);font-style:italic;">
                    Run <code>python scripts/generate_semantic_fields.py</code> to enable this view.
                </div>
            </div>
        </div>

        <!-- Export buttons -->
        <div style="display:flex;gap:.5rem;flex-wrap:wrap;">
            <button onclick="exportJSON()"
                    style="padding:.4rem .9rem;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--fg);cursor:pointer;font-size:.85rem;">
                Export JSON
            </button>
            <button onclick="exportCSV()"
                    style="padding:.4rem .9rem;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--fg);cursor:pointer;font-size:.85rem;">
                Export CSV
            </button>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
(function() {
    var LANG = {{ lang|tojson }};
    var _profileData = null;

    var RARITY_COLORS = {
        hapax: '#9c27b0',
        rare: '#1976d2',
        common: '#388e3c',
        very_common: '#f57c00'
    };
    var RARITY_LABELS = {
        hapax: 'Hapax (1×)',
        rare: 'Rare (2–5×)',
        common: 'Common (6–20×)',
        very_common: 'Frequent (21+×)'
    };

    function escHtml(s) {
        return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    }

    window.runProfile = function() {
        var book = document.getElementById('pp-book').value;
        var chStart = document.getElementById('pp-ch-start').value;
        var chEnd = document.getElementById('pp-ch-end').value;
        if (!book || !chStart) return;

        document.getElementById('pp-empty').style.display = 'none';
        document.getElementById('pp-results').style.display = 'none';
        document.getElementById('pp-loading').style.display = 'block';

        var url = '/api/passage-profile?book=' + encodeURIComponent(book)
                + '&ch_start=' + chStart
                + '&ch_end=' + (chEnd || chStart)
                + '&lang=' + LANG;

        fetch(url)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.error) {
                    document.getElementById('pp-loading').style.display = 'none';
                    document.getElementById('pp-empty').style.display = 'block';
                    document.getElementById('pp-empty').textContent = data.error;
                    return;
                }
                _profileData = data;
                renderProfile(data);
            })
            .catch(function() {
                document.getElementById('pp-loading').style.display = 'none';
                document.getElementById('pp-empty').style.display = 'block';
            });
    };

    function renderProfile(d) {
        document.getElementById('pp-loading').style.display = 'none';

        // Passage label
        document.getElementById('pp-passage-label').textContent = d.passage;

        // Stat cards
        document.getElementById('pp-stat-unique').textContent = d.unique_roots.toLocaleString();
        document.getElementById('pp-stat-density').textContent = (d.lexical_density * 100).toFixed(1) + '%';
        document.getElementById('pp-stat-hapax').textContent = d.hapax_in_passage.toLocaleString();
        document.getElementById('pp-stat-corpus-hapax').textContent = d.corpus_hapaxes.toLocaleString();

        // Rarity chart (horizontal stacked bars)
        renderRarityChart(d.rarity_buckets, d.unique_roots);

        // Stem chart (horizontal bars sorted by count)
        renderStemChart(d.stem_distribution);

        // Verse density
        renderDensityChart(d.verse_density);

        // Top roots table
        renderTopRoots(d.top_roots);

        // Semantic domains
        if (d.semantic_fields && Object.keys(d.semantic_fields).length > 0) {
            document.getElementById('pp-no-domains').style.display = 'none';
            renderDomainsChart(d.semantic_fields);
        } else {
            document.getElementById('pp-domains-chart').innerHTML = '';
            document.getElementById('pp-no-domains').style.display = 'block';
        }

        document.getElementById('pp-results').style.display = 'block';
    }

    function renderRarityChart(buckets, total) {
        var el = document.getElementById('pp-rarity-chart');
        el.innerHTML = '';
        var order = ['very_common', 'common', 'rare', 'hapax'];
        order.forEach(function(key) {
            var count = buckets[key] || 0;
            var pct = total > 0 ? Math.round(count / total * 100) : 0;
            var row = document.createElement('div');
            row.style.cssText = 'display:flex;align-items:center;gap:.5rem;margin-bottom:.35rem;';
            row.innerHTML =
                '<div style="width:90px;font-size:.75rem;color:var(--muted);flex-shrink:0;">' + escHtml(RARITY_LABELS[key]) + '</div>' +
                '<div style="flex:1;background:var(--border);border-radius:3px;height:12px;overflow:hidden;">' +
                  '<div style="width:' + pct + '%;height:100%;background:' + RARITY_COLORS[key] + ';border-radius:3px;"></div>' +
                '</div>' +
                '<div style="width:36px;text-align:right;font-size:.75rem;color:var(--fg);">' + count + '</div>';
            el.appendChild(row);
        });
    }

    function renderStemChart(stemDist) {
        var el = document.getElementById('pp-stem-chart');
        el.innerHTML = '';
        var entries = Object.entries(stemDist).sort(function(a, b) { return b[1] - a[1]; }).slice(0, 8);
        var maxVal = entries.length ? entries[0][1] : 1;
        entries.forEach(function(entry) {
            var key = entry[0], count = entry[1];
            var pct = Math.round(count / maxVal * 100);
            var row = document.createElement('div');
            row.style.cssText = 'display:flex;align-items:center;gap:.5rem;margin-bottom:.3rem;';
            row.innerHTML =
                '<div style="width:80px;font-size:.75rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex-shrink:0;">' +
                  '<span class="stem-badge stem-' + escHtml(key) + '" style="font-size:.65rem;">' + escHtml(key) + '</span>' +
                '</div>' +
                '<div style="flex:1;background:var(--border);border-radius:3px;height:10px;overflow:hidden;">' +
                  '<div style="width:' + pct + '%;height:100%;background:var(--accent);border-radius:3px;opacity:0.7;"></div>' +
                '</div>' +
                '<div style="width:32px;text-align:right;font-size:.75rem;color:var(--fg);">' + count + '</div>';
            el.appendChild(row);
        });
    }

    function renderDensityChart(verseDensity) {
        var el = document.getElementById('pp-density-chart');
        el.innerHTML = '';
        if (!verseDensity || verseDensity.length === 0) return;
        var maxCount = Math.max.apply(null, verseDensity.map(function(v) { return v.root_count; }));
        var wrap = document.createElement('div');
        wrap.style.cssText = 'display:flex;align-items:flex-end;gap:2px;height:60px;min-width:' + (verseDensity.length * 7) + 'px;';
        verseDensity.forEach(function(v) {
            var pct = maxCount > 0 ? v.root_count / maxCount * 100 : 0;
            var bar = document.createElement('div');
            bar.title = v.ref + ': ' + v.root_count + ' roots';
            bar.style.cssText = 'flex:1;min-width:5px;max-width:12px;background:var(--accent);opacity:0.65;border-radius:2px 2px 0 0;height:' + Math.max(2, pct) + '%;';
            wrap.appendChild(bar);
        });
        el.appendChild(wrap);
        // X-axis label count
        var label = document.createElement('div');
        label.style.cssText = 'font-size:.7rem;color:var(--muted);margin-top:.3rem;';
        label.textContent = verseDensity.length + ' verses';
        el.appendChild(label);
    }

    function renderTopRoots(roots) {
        var tbody = document.getElementById('pp-roots-tbody');
        tbody.innerHTML = '';
        var maxCount = roots.length ? roots[0].passage_count : 1;
        roots.forEach(function(r) {
            var pct = Math.round(r.passage_count / maxCount * 100);
            var tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid var(--border)';
            tr.innerHTML =
                '<td style="padding:.3rem .4rem;font-family:var(--syriac-font);font-size:1rem;" dir="rtl">' + escHtml(r.root) + '</td>' +
                '<td style="padding:.3rem .4rem;color:var(--muted);font-size:.8rem;font-style:italic;">' + escHtml(r.gloss) + '</td>' +
                '<td style="padding:.3rem .4rem;text-align:right;">' +
                  '<div style="display:flex;align-items:center;gap:.3rem;justify-content:flex-end;">' +
                    '<div style="width:40px;background:var(--border);border-radius:2px;height:8px;">' +
                      '<div style="width:' + pct + '%;height:100%;background:var(--accent);border-radius:2px;"></div>' +
                    '</div>' +
                    '<span style="font-size:.8rem;min-width:20px;text-align:right;">' + r.passage_count + '</span>' +
                  '</div>' +
                '</td>' +
                '<td style="padding:.3rem .4rem;text-align:right;font-size:.75rem;color:var(--muted);">' + r.corpus_total + '</td>';
            tbody.appendChild(tr);
        });
    }

    function renderDomainsChart(sfDist) {
        var el = document.getElementById('pp-domains-chart');
        el.innerHTML = '';
        var entries = Object.entries(sfDist).sort(function(a,b) { return b[1]-a[1]; }).slice(0, 10);
        var maxVal = entries.length ? entries[0][1] : 1;
        entries.forEach(function(entry) {
            var domain = entry[0], count = entry[1];
            var pct = Math.round(count / maxVal * 100);
            var row = document.createElement('div');
            row.style.cssText = 'display:flex;align-items:center;gap:.5rem;margin-bottom:.3rem;';
            row.innerHTML =
                '<div style="width:100px;font-size:.72rem;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex-shrink:0;">' + escHtml(domain) + '</div>' +
                '<div style="flex:1;background:var(--border);border-radius:3px;height:10px;overflow:hidden;">' +
                  '<div style="width:' + pct + '%;height:100%;background:#059669;border-radius:3px;"></div>' +
                '</div>' +
                '<div style="width:28px;text-align:right;font-size:.72rem;">' + count + '</div>';
            el.appendChild(row);
        });
    }

    window.exportJSON = function() {
        if (!_profileData) return;
        var blob = new Blob([JSON.stringify(_profileData, null, 2)], {type: 'application/json'});
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'passage-profile.json';
        a.click();
    };

    window.exportCSV = function() {
        if (!_profileData) return;
        var rows = [['root', 'root_key', 'gloss', 'passage_count', 'corpus_total']];
        _profileData.top_roots.forEach(function(r) {
            rows.push([r.root, r.root_key, r.gloss, r.passage_count, r.corpus_total]);
        });
        var csv = rows.map(function(r) {
            return r.map(function(c) { return '"' + String(c).replace(/"/g, '""') + '"'; }).join(',');
        }).join('\n');
        var blob = new Blob([csv], {type: 'text/csv'});
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'passage-profile.csv';
        a.click();
    };

    {% if initial_book and initial_ch_start %}
    document.addEventListener('DOMContentLoaded', function() { runProfile(); });
    {% endif %}
})();
</script>
{% endblock %}
```

- [ ] **Step 3: Verify page route loads**

```bash
python3 -c "
import app
app.app.config['TESTING'] = True
c = app.app.test_client()
r = c.get('/passage-profile?lang=en')
print(r.status_code)   # expect 200
assert b'pp-results' in r.data
print('OK')
"
```

- [ ] **Step 4: Commit**

```bash
git add app.py templates/passage_profile.html
git commit -m "feat: add /passage-profile page with lexical stats charts"
```

---

## Task 9 — Add i18n keys to `data/i18n.json`

**Files:**
- Modify: `data/i18n.json`

- [ ] **Step 1: Add Feature 1 keys (12 keys × 4 languages)**

Open `data/i18n.json`. In the `"en"` object, add:

```json
"parse_title": "Word Parser",
"parse_subtitle": "Full morphological breakdown: prefixes, root, suffixes, stem, and cognates for any Syriac word.",
"parse_input_placeholder": "Paste or type a Syriac word",
"parse_analyze": "Parse",
"parse_prefixes": "Prefixes",
"parse_root": "Root",
"parse_suffixes": "Suffixes",
"parse_stem": "Stem",
"parse_confidence": "Confidence",
"parse_cognates": "Cognates",
"parse_pos": "Part of Speech",
"parse_copy_gloss": "Copy Gloss (Leipzig)"
```

In the `"es"` object, add:

```json
"parse_title": "Analizador de Palabras",
"parse_subtitle": "Análisis morfológico completo: prefijos, raíz, sufijos, binián y cognados de cualquier palabra aramea.",
"parse_input_placeholder": "Pega o escribe una palabra en siríaco",
"parse_analyze": "Analizar",
"parse_prefixes": "Prefijos",
"parse_root": "Raíz",
"parse_suffixes": "Sufijos",
"parse_stem": "Binián",
"parse_confidence": "Confianza",
"parse_cognates": "Cognados",
"parse_pos": "Categoría Gramatical",
"parse_copy_gloss": "Copiar Glosa (Leipzig)"
```

In the `"he"` object, add:

```json
"parse_title": "מנתח מילים",
"parse_subtitle": "פירוק מורפולוגי מלא: קידומות, שורש, סיומות, בניין וקוגנטים לכל מילה ארמית.",
"parse_input_placeholder": "הדבק או הקלד מילה בסורית",
"parse_analyze": "נתח",
"parse_prefixes": "קידומות",
"parse_root": "שורש",
"parse_suffixes": "סיומות",
"parse_stem": "בניין",
"parse_confidence": "ביטחון",
"parse_cognates": "קוגנטים",
"parse_pos": "חלק הדיבר",
"parse_copy_gloss": "העתק גלוסה"
```

In the `"ar"` object, add:

```json
"parse_title": "محلل الكلمات",
"parse_subtitle": "تحليل صرفي كامل: البادئات والجذر واللواحق والجذع والمعرفات المعرفية لأي كلمة آرامية.",
"parse_input_placeholder": "الصق أو اكتب كلمة سريانية",
"parse_analyze": "حلِّل",
"parse_prefixes": "بادئات",
"parse_root": "جذر",
"parse_suffixes": "لواحق",
"parse_stem": "الجذع",
"parse_confidence": "ثقة",
"parse_cognates": "متشابهات",
"parse_pos": "قسم الكلام",
"parse_copy_gloss": "نسخ المصطلح"
```

- [ ] **Step 2: Add Feature 2 keys (18 keys × 4 languages)**

In the `"en"` object, add:

```json
"pp_title": "Passage Lexical Profile",
"pp_subtitle": "Statistical vocabulary analysis for any book and chapter range: root density, rarity distribution, stem breakdown, and more.",
"pp_book_label": "Book",
"pp_chapter_from": "Chapter from",
"pp_chapter_to": "to",
"pp_analyze": "Analyze",
"pp_unique_roots": "Unique Roots",
"pp_lexical_density": "Lexical Density",
"pp_passage_hapaxes": "Passage Hapaxes",
"pp_corpus_hapaxes": "Corpus Hapaxes",
"pp_rarity_dist": "Root Rarity Distribution",
"pp_stem_dist": "Verb Stem Distribution",
"pp_verse_density": "Verse-by-Verse Root Density",
"pp_top_roots": "Top 15 Roots",
"pp_semantic_domains": "Semantic Domains",
"pp_col_root": "Root",
"pp_col_gloss": "Gloss",
"pp_col_freq": "In Passage",
"pp_col_rarity": "Corpus Total"
```

In the `"es"` object, add:

```json
"pp_title": "Perfil Léxico del Pasaje",
"pp_subtitle": "Análisis estadístico del vocabulario para cualquier libro y rango de capítulos.",
"pp_book_label": "Libro",
"pp_chapter_from": "Capítulo desde",
"pp_chapter_to": "hasta",
"pp_analyze": "Analizar",
"pp_unique_roots": "Raíces Únicas",
"pp_lexical_density": "Densidad Léxica",
"pp_passage_hapaxes": "Hápax en el Pasaje",
"pp_corpus_hapaxes": "Hápax del Corpus",
"pp_rarity_dist": "Distribución de Rareza",
"pp_stem_dist": "Distribución de Binianes",
"pp_verse_density": "Densidad por Versículo",
"pp_top_roots": "15 Raíces Más Frecuentes",
"pp_semantic_domains": "Campos Semánticos",
"pp_col_root": "Raíz",
"pp_col_gloss": "Glosa",
"pp_col_freq": "En el Pasaje",
"pp_col_rarity": "Total en Corpus"
```

In the `"he"` object, add:

```json
"pp_title": "פרופיל לקסיקלי של קטע",
"pp_subtitle": "ניתוח סטטיסטי של אוצר המילים לכל ספר וטווח פרקים.",
"pp_book_label": "ספר",
"pp_chapter_from": "פרק מ-",
"pp_chapter_to": "עד",
"pp_analyze": "נתח",
"pp_unique_roots": "שורשים ייחודיים",
"pp_lexical_density": "צפיפות לקסיקלית",
"pp_passage_hapaxes": "הפקסים בקטע",
"pp_corpus_hapaxes": "הפקסים בקורפוס",
"pp_rarity_dist": "התפלגות נדירות",
"pp_stem_dist": "התפלגות בניינים",
"pp_verse_density": "צפיפות לפי פסוק",
"pp_top_roots": "15 השורשים הנפוצים",
"pp_semantic_domains": "שדות סמנטיים",
"pp_col_root": "שורש",
"pp_col_gloss": "מובן",
"pp_col_freq": "בקטע",
"pp_col_rarity": "סה״כ בקורפוס"
```

In the `"ar"` object, add:

```json
"pp_title": "الملف المعجمي للمقطع",
"pp_subtitle": "تحليل إحصائي للمفردات لأي كتاب ونطاق فصول.",
"pp_book_label": "الكتاب",
"pp_chapter_from": "الفصل من",
"pp_chapter_to": "إلى",
"pp_analyze": "حلِّل",
"pp_unique_roots": "الجذور الفريدة",
"pp_lexical_density": "الكثافة المعجمية",
"pp_passage_hapaxes": "كلمات فريدة في المقطع",
"pp_corpus_hapaxes": "كلمات فريدة في الكوربوس",
"pp_rarity_dist": "توزيع الندرة",
"pp_stem_dist": "توزيع الجذوع",
"pp_verse_density": "كثافة الجذور بالآية",
"pp_top_roots": "أعلى 15 جذرًا",
"pp_semantic_domains": "الحقول الدلالية",
"pp_col_root": "جذر",
"pp_col_gloss": "معنى",
"pp_col_freq": "في المقطع",
"pp_col_rarity": "إجمالي الكوربوس"
```

- [ ] **Step 3: Verify the keys render in a template**

```bash
python3 -c "
import app, json
app._init()
lang = 'en'
print(app._t('parse_title', lang))      # expect: Word Parser
print(app._t('pp_title', lang))         # expect: Passage Lexical Profile
lang = 'es'
print(app._t('parse_title', lang))      # expect: Analizador de Palabras
print(app._t('pp_title', lang))         # expect: Perfil Léxico del Pasaje
"
```

- [ ] **Step 4: Commit**

```bash
git add data/i18n.json
git commit -m "feat: add i18n keys for Word Parser and Passage Lexical Profile (4 languages)"
```

---

## Task 10 — Add nav links + final integration commit

**Files:**
- Modify: `templates/base.html`

- [ ] **Step 1: Add links in the Research dropdown**

In `templates/base.html`, find the Research dropdown (around line 53–54):

```html
<a href="/collocations?lang={{ lang }}">{{ t('coll_title', lang) if t else 'Collocations' }}</a>
<a href="/semantic-fields?lang={{ lang }}">{{ t('sf_title', lang) if t else 'Semantic Fields' }}</a>
```

After those two lines, add:

```html
<a href="/parse?lang={{ lang }}">{{ t('parse_title', lang) if t else 'Word Parser' }}</a>
<a href="/passage-profile?lang={{ lang }}">{{ t('pp_title', lang) if t else 'Passage Profile' }}</a>
```

- [ ] **Step 2: Run the full test suite**

```bash
python -m pytest tests/ -v
```

Expected: All 15 tests pass.

- [ ] **Step 3: Smoke-test both pages render with nav links**

```bash
python3 -c "
import app
app.app.config['TESTING'] = True
c = app.app.test_client()
r = c.get('/parse?lang=en')
assert r.status_code == 200
assert b'parse_title' not in r.data  # keys should be resolved, not raw
assert b'Word Parser' in r.data or b'parse-input' in r.data
r2 = c.get('/passage-profile?lang=en')
assert r2.status_code == 200
assert b'pp-results' in r2.data
r3 = c.get('/?lang=en')
assert b'/parse' in r3.data
assert b'/passage-profile' in r3.data
print('All smoke-tests pass')
"
```

- [ ] **Step 4: Final commit**

```bash
git add templates/base.html
git commit -m "feat: add Word Parser and Passage Profile links to Research dropdown nav"
```

- [ ] **Step 5: Push to remote**

```bash
git push origin main
```

---

## Verification Checklist

After all tasks are complete, manually verify these scenarios:

### Feature 1 — Word Parser
- [ ] Visit `/parse?lang=en`, type `ܘܫܠܡ`, click Parse → morpheme boxes appear with teal prefix `ܘ` (conjunction), gold root `ܫܠܡ` (SH-L-M), gloss in English
- [ ] Switch to `/parse?lang=es` → same word, gloss in Spanish
- [ ] Copy Gloss button → clipboard contains three-line Leipzig format: word / morpheme labels / gloss
- [ ] Open `/read/Matthew/5`, click any word with a root → popover appears immediately with quick info, then updates with morpheme boxes after ~100ms
- [ ] Popover "Parse" link → navigates to `/parse?word=<word>`
- [ ] `/parse?word=ܫܠܡ` (prefill via URL) → auto-parses on load

### Feature 2 — Passage Profile
- [ ] Visit `/passage-profile?lang=en`, select Matthew ch 5–7, click Analyze → all four stat cards populate
- [ ] Rarity distribution chart shows 4 colored bars
- [ ] Stem distribution chart shows top stems by count
- [ ] Verse density chart shows one bar per verse
- [ ] Top 15 roots table shows root, gloss, in-passage count, corpus total
- [ ] Export JSON → downloads valid JSON file
- [ ] Export CSV → downloads file with root/gloss/count columns
- [ ] All labels render correctly in es/he/ar

---

## Notes for Implementers

- `generate_candidate_stems()` returns candidates ordered: bare word first, then with increasing affixes stripped. The loop in `api_word_parse` picks the **first candidate whose remaining stem contains all root consonants** — this is intentionally conservative and avoids over-stripping.
- `_extractor.lookup_word_root()` returns `None` for stopwords and unknown words. The passage-profile endpoint treats `None` as "skip this word" — this is the correct behavior (stopwords are excluded from root counts).
- `semantic_fields.json` is keyed by transliterated root (lowercase dash-separated e.g. `"sh-l-m"`), matching `_translit_to_dash(root_syr).lower()`. If the file is not present, `_semantic_fields` is `{}` and both the semantic fields section in passage-profile and the existing semantic-fields pages gracefully show empty/no-data states.
- The word popover in `read.html` shows a **quick version** from cached `data-*` attributes first (zero latency), then replaces it with the full morpheme breakdown from the AJAX fetch. If the fetch fails, the quick version stays visible. Results are cached in `_cache` for the session duration.
