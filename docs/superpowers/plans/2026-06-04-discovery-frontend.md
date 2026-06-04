# Discovery Front-End Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the "Discover" front door to the Aramaic Root Atlas — a curated home page, a narrative "Root Journey" view, and a guided-journeys page — reusing the existing engine and JSON APIs, with no extraction-logic changes.

**Architecture:** Repositioning of the existing Flask app (one app, two doors). New server routes render new Jinja templates that extend `base.html`. The Root Journey page is server-rendered for its headline (root in both scripts + gloss) and enriched client-side from the existing `/api/diachronic/root` and `/api/root-family` endpoints. Curated content lives in JSON data files so it changes without code edits. The existing scholarly tools are untouched in this plan (their caveat/triage pass is deferred).

**Tech Stack:** Python 3 / Flask, Jinja2 templates, vanilla JS (matching `static/app.js`), pytest with the `client` fixture in `tests/conftest.py`.

**Scope note:** This plan implements spec sections §5–§8 (Discover side). Spec §9 (Explore-tool caveat banners, citation/TEI demotion, how-it-works page) is intentionally deferred to a later "positioning" plan per the user's instruction.

---

## File Structure

**Create:**
- `data/discovery/featured_roots.json` — curated hero grid + root-of-the-day pool
- `data/journeys/covenant.json`, `data/journeys/kings.json`, `data/journeys/everyday.json` — launch journeys (3 to start)
- `templates/home.html` — Discover landing page (served at `/`)
- `templates/journey.html` — Root Journey hero view (`/journey/<root_key>`)
- `templates/discovery.html` — guided-journeys shelf (`/discover`)
- `tests/test_discovery.py` — route + data-contract tests

**Modify:**
- `app.py` — add `import datetime`; load featured-roots + journeys in `_init()`; add helpers `_root_card`, `_root_of_the_day`, `_load_journeys`; add routes `home` (`/`), `journey` (`/journey/<path:root_key>`), `discover` (`/discover`); move the existing search page from `/` to `/search`
- `static/app.js` — add a "Discover" nav group (Home, Journeys); repoint the existing "Trace Root" item to `/search`
- `tests/test_smoke.py` — add `/search`, `/discover`, `/journey/SH-L-M` to `PAGES`

**Reused unchanged:** `/api/diachronic/root`, `/api/root-family`, `parse_root_input`, `_extractor`, `_cognate_lookup`, `_corpus`, `_translit_to_dash`, `CORPUS_CHRONOLOGY`, `_get_lang/_get_script/_get_trans`, `_t_proxy`, `_bn`.

---

## Task 1: Curated content data file + loader

**Files:**
- Create: `data/discovery/featured_roots.json`
- Modify: `app.py` (imports near line 7; `_init()` around lines 60–75; new helpers after `_get_lang` ~line 145)
- Test: `tests/test_discovery.py`

- [ ] **Step 1: Create the data file**

Create `data/discovery/featured_roots.json`:

```json
{
  "hero": ["SH-L-M", "K-TH-B", "M-L-K", "B-R-K", "Q-D-SH", "A-M-R"],
  "root_of_day": ["SH-L-M", "K-TH-B", "M-L-K", "B-R-K", "Q-D-SH", "A-M-R"]
}
```

- [ ] **Step 2: Write the failing test**

Create `tests/test_discovery.py`:

```python
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import app as flask_app


def test_featured_roots_all_resolve():
    """Every curated hero/root-of-day entry must parse AND exist in the index."""
    flask_app._init()
    feat = flask_app._featured
    assert feat['hero'], 'hero list is empty'
    for key in set(feat['hero']) | set(feat['root_of_day']):
        syriac = flask_app.parse_root_input(key)
        assert syriac is not None, f'{key} does not parse'
        assert flask_app._extractor.lookup_root(syriac) is not None, f'{key} not attested'


def test_root_of_the_day_is_deterministic():
    flask_app._init()
    a = flask_app._root_of_the_day()
    b = flask_app._root_of_the_day()
    assert a == b and a in flask_app._featured['root_of_day']
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python3 -m pytest tests/test_discovery.py -v`
Expected: FAIL with `AttributeError: module 'app' has no attribute '_featured'`.

- [ ] **Step 4: Add the import**

In `app.py`, find the import block near the top (the `import json`/`import os` lines) and add:

```python
import datetime
```

- [ ] **Step 5: Load featured roots in `_init()`**

In `app.py`, find the `_init()` body where i18n is loaded (the `i18n_path = os.path.join(DATA_DIR, 'i18n.json')` block) and add immediately after it:

```python
        # Load curated discovery content
        global _featured
        _featured = {'hero': [], 'root_of_day': []}
        feat_path = os.path.join(DATA_DIR, 'discovery', 'featured_roots.json')
        if os.path.exists(feat_path):
            with open(feat_path, 'r', encoding='utf-8') as f:
                _featured = json.load(f)
```

Also add `_featured: dict = {}` to the module-level globals near `_i18n: dict = {}` (~line 46), and add `_featured` to the `global` declaration line inside `_init()` (the `global _i18n, _cognates_raw, ...` line ~line 60).

- [ ] **Step 6: Add the root-of-the-day helper**

In `app.py`, after the `_get_lang()` function (~line 145), add:

```python
def _root_of_the_day():
    """Deterministic daily pick from the curated pool (reproducible, no RNG)."""
    pool = _featured.get('root_of_day') or []
    if not pool:
        return None
    idx = datetime.date.today().toordinal() % len(pool)
    return pool[idx]
```

- [ ] **Step 7: Run test to verify it passes**

Run: `python3 -m pytest tests/test_discovery.py -v`
Expected: PASS (2 tests). If `test_featured_roots_all_resolve` fails on a specific key, that key is not attested — remove it from the JSON and re-run.

- [ ] **Step 8: Commit**

```bash
git add data/discovery/featured_roots.json app.py tests/test_discovery.py
git commit -m "feat(discovery): curated featured-roots data + deterministic root-of-the-day"
```

---

## Task 2: Root card helper

**Files:**
- Modify: `app.py` (after `_root_of_the_day`)
- Test: `tests/test_discovery.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_discovery.py`:

```python
def test_root_card_known_root():
    flask_app._init()
    card = flask_app._root_card('SH-L-M')
    assert card is not None
    assert card['syriac'] == 'ܫܠܡ'
    assert card['gloss']           # non-empty gloss
    assert card['total'] > 0
    assert card['key']             # round-trippable key for URLs


def test_root_card_unknown_returns_none():
    flask_app._init()
    assert flask_app._root_card('ZZZZ') is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_discovery.py::test_root_card_known_root -v`
Expected: FAIL with `AttributeError: ... '_root_card'`.

- [ ] **Step 3: Implement the helper**

In `app.py`, immediately after `_root_of_the_day()`, add:

```python
def _root_card(root_input):
    """Build a compact display card for a root, or None if not attested.

    Uses only existing engine calls; no extraction logic added.
    """
    root_syriac = parse_root_input(root_input)
    if not root_syriac:
        return None
    entry = _extractor.lookup_root(root_syriac)
    if not entry:
        return None
    display = _extractor.get_root_display(root_syriac)
    gloss = _extractor.get_root_gloss(root_syriac)
    cog = _cognate_lookup.lookup(root_syriac)
    if cog and not gloss:
        gloss = cog.gloss_en
    return {
        'key': _translit_to_dash(root_syriac),
        'syriac': display.get('syriac', root_syriac),
        'hebrew': display.get('hebrew', ''),
        'gloss': gloss or '',
        'total': entry.total_occurrences,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_discovery.py -v`
Expected: PASS (all 4 tests).

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_discovery.py
git commit -m "feat(discovery): _root_card helper for home + journey SSR"
```

---

## Task 3: Root Journey route + template (the hero)

**Files:**
- Create: `templates/journey.html`
- Modify: `app.py` (new route near the other page routes, e.g. after the `index`/`browse` routes ~line 510)
- Test: `tests/test_discovery.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_discovery.py`:

```python
def test_journey_known_root_renders(client):
    r = client.get('/journey/SH-L-M')
    assert r.status_code == 200
    body = r.data.decode('utf-8')
    assert 'ܫܠܡ' in body                     # Syriac form, SSR
    assert 'one skeleton' in body.lower()    # homograph teaching panel present
    assert '/api/diachronic/root?root=' in body  # JS enrichment wired


def test_journey_unknown_root_404(client):
    r = client.get('/journey/ZZZZ')
    assert r.status_code == 404
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_discovery.py::test_journey_known_root_renders -v`
Expected: FAIL with 404 (route not yet defined).

- [ ] **Step 3: Add the route**

In `app.py`, after the `browse` route (~line 510), add:

```python
@app.route('/journey/<path:root_key>')
def journey(root_key):
    _init()
    lang = _get_lang()
    card = _root_card(root_key)
    if card is None:
        from flask import abort
        abort(404)
    return render_template('journey.html',
                           lang=lang, script=_get_script(), trans=_get_trans(),
                           t=_t_proxy, bn=_bn, card=card, page_id='discover')
```

- [ ] **Step 4: Create the template**

Create `templates/journey.html`:

```html
{% extends "base.html" %}
{% block title %}{{ card.key }} — Root Journey{% endblock %}
{% block content %}
<div class="journey-wrap" data-root="{{ card.key }}">

  <!-- 1. The root, big -->
  <header class="journey-head">
    <div class="journey-scripts">
      <span class="jr-syriac">{{ card.syriac }}</span>
      {% if card.hebrew %}<span class="jr-sep">·</span><span class="jr-hebrew">{{ card.hebrew }}</span>{% endif %}
      <span class="jr-sep">·</span><span class="jr-key">{{ card.key }}</span>
    </div>
    <p class="journey-gloss">{{ card.gloss }}</p>
    {% if card.hebrew %}<p class="journey-note">Two scripts, one root — Syriac and Hebrew square resolve to the same three-letter skeleton.</p>{% endif %}
  </header>

  <!-- 2. Timeline strip (filled by JS from /api/diachronic/root) -->
  <section class="journey-timeline">
    <h2>Across 1,500 years</h2>
    <div id="jr-timeline" class="jr-timeline">Loading the journey…</div>
  </section>

  <!-- 3. One skeleton, several meanings (homograph lesson) -->
  <section class="journey-panel">
    <h2>One skeleton, several meanings</h2>
    <p>A three-letter root is a <em>skeleton</em>, not a single word. The same consonants can carry
    related — sometimes quite different — senses. This atlas groups words by their skeleton; a
    dictionary separates the individual senses. Treat what you see here as a starting point for
    exploration, not a final definition.</p>
  </section>

  <!-- 4. Cousins across languages (filled by JS from /api/root-family) -->
  <section class="journey-cousins">
    <h2>Cousins in sister languages</h2>
    <div id="jr-cousins" class="jr-cousins"></div>
    <p class="journey-disclaimer">Fascinating connections — explorers' leads, not dictionary-grade etymology.</p>
  </section>

  <!-- 5. One real verse, decoded (filled by JS) -->
  <section class="journey-verse">
    <h2>Seen in the wild</h2>
    <div id="jr-verse" class="jr-verse"></div>
  </section>

  <!-- 6. Keep exploring -->
  <nav class="journey-more">
    <a class="btn" href="/visualize/{{ card.key }}?lang={{ lang }}">Full visualizer</a>
    <a class="btn" href="/discover?lang={{ lang }}">More journeys</a>
  </nav>
</div>

<script>
(function(){
  var wrap = document.querySelector('.journey-wrap');
  var root = wrap && wrap.dataset.root;
  if(!root) return;
  var q = encodeURIComponent(root);

  // Timeline from existing diachronic endpoint
  fetch('/api/diachronic/root?root=' + q).then(function(r){return r.json();}).then(function(d){
    var el = document.getElementById('jr-timeline');
    if(!d.corpora){ el.textContent = 'No timeline data.'; return; }
    var max = Math.max.apply(null, d.corpora.map(function(c){return c.raw_count;}).concat([1]));
    el.innerHTML = d.corpora.map(function(c){
      var pct = Math.round((c.raw_count / max) * 100);
      return '<div class="jr-bar-row"><span class="jr-bar-label">' + c.label + '</span>'
        + '<span class="jr-bar"><span class="jr-bar-fill" style="width:' + pct + '%"></span></span>'
        + '<span class="jr-bar-count">' + c.raw_count + '</span></div>';
    }).join('');
  }).catch(function(){ document.getElementById('jr-timeline').textContent = 'Timeline unavailable.'; });

  // Cousins + key verse from existing root-family endpoint
  fetch('/api/root-family?root=' + q).then(function(r){return r.json();}).then(function(d){
    var cousins = document.getElementById('jr-cousins');
    var heb = (d.cognates && d.cognates.hebrew) || [];
    var ar  = (d.cognates && d.cognates.arabic) || [];
    function pills(list, langLabel){
      if(!list.length) return '';
      return '<div class="jr-cousin-group"><span class="jr-cousin-lang">' + langLabel + '</span>'
        + list.slice(0,5).map(function(c){
            return '<span class="jr-pill">' + (c.word||'') + ' <em>' + (c.meaning_en||'') + '</em></span>';
          }).join('') + '</div>';
    }
    cousins.innerHTML = pills(heb, 'Hebrew') + pills(ar, 'Arabic') || '<p>No cousins recorded yet.</p>';

    var verse = document.getElementById('jr-verse');
    var kv = d.key_verse || d.paradigm_verse || null;
    if(kv && (kv.ref || kv.reference)){
      verse.innerHTML = '<blockquote>' + (kv.text || '') + '</blockquote>'
        + (kv.translation ? '<p class="jr-verse-tr">' + kv.translation + '</p>' : '')
        + '<cite>' + (kv.ref || kv.reference) + '</cite>';
    } else { verse.parentNode.style.display = 'none'; }
  }).catch(function(){});
})();
</script>
{% endblock %}
```

> Note: the JS reads `d.cognates.hebrew/arabic` and `d.key_verse` defensively (falling back to `paradigm_verse`/`reference`). When implementing, open `/api/root-family?root=SH-L-M` once in the browser and confirm the exact key names; adjust the two `||` fallbacks to match. The test only requires the SSR markers, so it stays green regardless.

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m pytest tests/test_discovery.py::test_journey_known_root_renders tests/test_discovery.py::test_journey_unknown_root_404 -v`
Expected: PASS (2 tests).

- [ ] **Step 6: Manually verify enrichment**

Run: `python3 app.py` (port 5001), open `http://localhost:5001/journey/SH-L-M`. Confirm: the timeline bars fill across the six corpora, cousins pills show Hebrew/Arabic words, and a verse renders. If cousins/verse are empty, fix the JS key names per the note in Step 4.

- [ ] **Step 7: Commit**

```bash
git add app.py templates/journey.html tests/test_discovery.py
git commit -m "feat(discovery): Root Journey hero view (SSR headline + API-enriched timeline/cousins/verse)"
```

---

## Task 4: Move the existing search page to `/search`

**Files:**
- Modify: `app.py` (the `index` route ~lines 203–227)
- Test: `tests/test_smoke.py`

- [ ] **Step 1: Write the failing test**

In `tests/test_smoke.py`, add `'/search'` to the `PAGES` list (after `'/'`).

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest "tests/test_smoke.py::test_page_renders_in_english[/search]" -v`
Expected: FAIL with 404.

- [ ] **Step 3: Repoint the route**

In `app.py`, change the decorator on the existing `index()` function from:

```python
@app.route('/')
def index():
```

to:

```python
@app.route('/search')
def index():
```

Leave the function body unchanged (it still renders `index.html` with `page_id='search'`).

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest "tests/test_smoke.py::test_page_renders_in_english[/search]" -v`
Expected: PASS. (`/` will 404 until Task 5 — that is expected mid-task.)

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_smoke.py
git commit -m "refactor(discovery): move search page from / to /search"
```

---

## Task 5: Discover home at `/`

**Files:**
- Create: `templates/home.html`
- Modify: `app.py` (add `home` route where `index` used to be)
- Test: `tests/test_discovery.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_discovery.py`:

```python
def test_home_renders_with_featured(client):
    r = client.get('/')
    assert r.status_code == 200
    body = r.data.decode('utf-8')
    assert '/journey/' in body          # at least one journey link (hero grid)
    assert 'root of the day' in body.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_discovery.py::test_home_renders_with_featured -v`
Expected: FAIL with 404.

- [ ] **Step 3: Add the route**

In `app.py`, add (near the top of the page routes, e.g. just above the `@app.route('/search')` line):

```python
@app.route('/')
def home():
    _init()
    lang = _get_lang()
    rotd = _root_card(_root_of_the_day()) if _root_of_the_day() else None
    hero = [c for c in (_root_card(k) for k in _featured.get('hero', [])) if c]
    return render_template('home.html',
                           lang=lang, script=_get_script(), trans=_get_trans(),
                           t=_t_proxy, bn=_bn, rotd=rotd, hero=hero, page_id='discover-home')
```

- [ ] **Step 4: Create the template**

Create `templates/home.html`:

```html
{% extends "base.html" %}
{% block title %}Triliteral Aramaic Atlas — Discover{% endblock %}
{% block content %}
<div class="home-wrap">

  <!-- Hook + meaning search -->
  <section class="home-hero">
    <h1 class="home-title">Every Aramaic word grows from a three-letter root.</h1>
    <p class="home-sub">Pick one and watch it travel across 1,500 years and two scripts.</p>
    <form class="home-search" action="/api/reverse-search" method="get" id="home-search-form" onsubmit="return homeSearch(event)">
      <input type="text" id="home-search-input" name="q" placeholder="Type a word you know — peace, king, write, bless" aria-label="Search by meaning">
      <button type="submit">Explore</button>
    </form>
    <p class="home-search-hint">We'll guess the closest root — a starting point, not the final word.</p>
  </section>

  <!-- Root of the day -->
  {% if rotd %}
  <section class="home-rotd">
    <div class="home-rotd-label">Root of the day</div>
    <a class="home-rotd-card" href="/journey/{{ rotd.key }}?lang={{ lang }}">
      <span class="rotd-syriac">{{ rotd.syriac }}</span>
      <span class="rotd-gloss">{{ rotd.gloss }}</span>
      <span class="rotd-go">See its journey →</span>
    </a>
  </section>
  {% endif %}

  <!-- Curated hero grid -->
  <section class="home-grid-wrap">
    <h2>Start with a famous root</h2>
    <div class="home-grid">
      {% for c in hero %}
      <a class="home-card" href="/journey/{{ c.key }}?lang={{ lang }}">
        <span class="card-syriac">{{ c.syriac }}</span>
        <span class="card-key">{{ c.key }}</span>
        <span class="card-gloss">{{ c.gloss }}</span>
      </a>
      {% endfor %}
    </div>
  </section>

  <p class="home-explore-link"><a href="/search?lang={{ lang }}">Looking for the research tools? → Explore</a></p>
</div>

<script>
function homeSearch(e){
  e.preventDefault();
  var q = document.getElementById('home-search-input').value.trim();
  if(!q) return false;
  fetch('/api/reverse-search?q=' + encodeURIComponent(q) + '&lang=' + (document.documentElement.lang||'en'))
    .then(function(r){return r.json();})
    .then(function(d){
      var first = (d.results && d.results[0]) || (Array.isArray(d) && d[0]) || null;
      var key = first && (first.root_key || first.key || first.root);
      if(key){ window.location = '/journey/' + encodeURIComponent(key) + '?lang=' + (document.documentElement.lang||'en'); }
      else { alert('No close root found — try another word.'); }
    });
  return false;
}
</script>
{% endblock %}
```

> Note: confirm the result key name from `/api/reverse-search?q=peace` (the code reads `root_key`/`key`/`root` defensively). Adjust the one line in `homeSearch` if needed. The test only checks SSR markers, so it stays green.

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m pytest tests/test_discovery.py::test_home_renders_with_featured -v`
Expected: PASS.

- [ ] **Step 6: Run the full smoke suite (now `/` is back)**

Run: `python3 -m pytest tests/test_smoke.py -v`
Expected: PASS for `/` and `/search`.

- [ ] **Step 7: Manually verify the meaning search**

Run the app; on `/` type "peace" and submit. Confirm it lands on `/journey/SH-L-M` (or the closest root). Fix the result-key line in `homeSearch` if it doesn't route.

- [ ] **Step 8: Commit**

```bash
git add app.py templates/home.html tests/test_discovery.py
git commit -m "feat(discovery): Discover home at / (meaning search, root-of-the-day, hero grid)"
```

---

## Task 6: Journeys data files + loader

**Files:**
- Create: `data/journeys/covenant.json`, `data/journeys/kings.json`, `data/journeys/everyday.json`
- Modify: `app.py` (loader + `_init()`)
- Test: `tests/test_discovery.py`

- [ ] **Step 1: Create three journey files**

`data/journeys/covenant.json`:

```json
{
  "id": "covenant",
  "title": "Words of the Covenant",
  "blurb": "Roots that carry blessing, holiness, and binding promise across the traditions.",
  "stops": [
    { "root": "B-R-K", "note": "To bless — and, curiously, to kneel. The body of the blessing." },
    { "root": "Q-D-SH", "note": "Holy, set apart. The vocabulary of the sacred." }
  ]
}
```

`data/journeys/kings.json`:

```json
{
  "id": "kings",
  "title": "Kings & Kingdoms",
  "blurb": "The language of rule, reign, and authority from Daniel to the Peshitta.",
  "stops": [
    { "root": "M-L-K", "note": "King, reign, kingdom — one root behind a whole political world." },
    { "root": "A-M-R", "note": "To say, to command — the speech of those in charge." }
  ]
}
```

`data/journeys/everyday.json`:

```json
{
  "id": "everyday",
  "title": "Everyday Aramaic",
  "blurb": "The common roots that show up everywhere, once you learn to see them.",
  "stops": [
    { "root": "K-TH-B", "note": "To write — scribes, scripture, and the written word itself." },
    { "root": "SH-L-M", "note": "Peace, wholeness, completion — the most famous root of all." }
  ]
}
```

- [ ] **Step 2: Write the failing test**

Append to `tests/test_discovery.py`:

```python
def test_journeys_load_and_resolve():
    flask_app._init()
    journeys = flask_app._load_journeys()
    assert len(journeys) >= 3
    for j in journeys:
        assert j['title'] and j['stops']
        for stop in j['stops']:
            syriac = flask_app.parse_root_input(stop['root'])
            assert syriac and flask_app._extractor.lookup_root(syriac), \
                f"journey {j['id']} stop {stop['root']} unresolved"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python3 -m pytest tests/test_discovery.py::test_journeys_load_and_resolve -v`
Expected: FAIL with `AttributeError: ... '_load_journeys'`.

- [ ] **Step 4: Implement the loader**

In `app.py`, after `_root_card`, add:

```python
def _load_journeys():
    """Load guided-journey definitions from data/journeys/*.json, sorted by title."""
    out = []
    jdir = os.path.join(DATA_DIR, 'journeys')
    if os.path.isdir(jdir):
        for fn in sorted(os.listdir(jdir)):
            if fn.endswith('.json'):
                with open(os.path.join(jdir, fn), 'r', encoding='utf-8') as f:
                    out.append(json.load(f))
    out.sort(key=lambda j: j.get('title', ''))
    return out
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m pytest tests/test_discovery.py::test_journeys_load_and_resolve -v`
Expected: PASS. If a stop fails, fix that root key in the JSON.

- [ ] **Step 6: Commit**

```bash
git add data/journeys/ app.py tests/test_discovery.py
git commit -m "feat(discovery): guided-journey data files + loader"
```

---

## Task 7: Discovery journeys page at `/discover`

**Files:**
- Create: `templates/discovery.html`
- Modify: `app.py` (add `discover` route)
- Test: `tests/test_discovery.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_discovery.py`:

```python
def test_discover_page_lists_journeys(client):
    r = client.get('/discover')
    assert r.status_code == 200
    body = r.data.decode('utf-8')
    assert 'Words of the Covenant' in body
    assert '/journey/' in body
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_discovery.py::test_discover_page_lists_journeys -v`
Expected: FAIL with 404.

- [ ] **Step 3: Add the route**

In `app.py`, after the `home` route, add:

```python
@app.route('/discover')
def discover():
    _init()
    lang = _get_lang()
    journeys = _load_journeys()
    return render_template('discovery.html',
                           lang=lang, script=_get_script(), trans=_get_trans(),
                           t=_t_proxy, bn=_bn, journeys=journeys, page_id='discover')
```

- [ ] **Step 4: Create the template**

Create `templates/discovery.html`:

```html
{% extends "base.html" %}
{% block title %}Discovery Journeys — Triliteral Aramaic Atlas{% endblock %}
{% block content %}
<div class="discover-wrap">
  <header class="discover-head">
    <h1>Discovery Journeys</h1>
    <p>Short, guided walks through related roots. Pick a path and follow the words.</p>
  </header>
  <div class="discover-shelf">
    {% for j in journeys %}
    <article class="discover-journey">
      <h2>{{ j.title }}</h2>
      <p class="discover-blurb">{{ j.blurb }}</p>
      <ol class="discover-stops">
        {% for stop in j.stops %}
        <li>
          <a href="/journey/{{ stop.root }}?lang={{ lang }}" class="discover-stop-root">{{ stop.root }}</a>
          <span class="discover-stop-note">{{ stop.note }}</span>
        </li>
        {% endfor %}
      </ol>
    </article>
    {% endfor %}
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m pytest tests/test_discovery.py::test_discover_page_lists_journeys -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add app.py templates/discovery.html tests/test_discovery.py
git commit -m "feat(discovery): /discover guided-journeys shelf"
```

---

## Task 8: Sidebar — add "Discover" group, repoint search

**Files:**
- Modify: `static/app.js` (the `NAV` object ~lines 30–69 and `renderSidebar` ~lines 90–110)
- Test: `tests/test_smoke.py` (add `/discover` and a journey page)

- [ ] **Step 1: Write the failing test**

In `tests/test_smoke.py`, add `'/discover'` and `'/journey/SH-L-M'` to the `PAGES` list.

- [ ] **Step 2: Run test to verify it passes for those paths**

Run: `python3 -m pytest "tests/test_smoke.py::test_page_renders_in_english[/discover]" "tests/test_smoke.py::test_page_renders_in_english[/journey/SH-L-M]" -v`
Expected: PASS (routes exist from Tasks 3 and 7). This locks the new pages into the smoke matrix across all four languages.

- [ ] **Step 3: Add the Discover nav group**

In `static/app.js`, inside the `NAV` object, add a new `discover` array as the FIRST group (before `explore`):

```javascript
    discover: [
      { id:'discover-home', href:'/',          label: S.nav_discover_home || 'Discover',
        ic:'<path d="M12 2l2.5 7H22l-6 4.5L18.5 22 12 17.5 5.5 22 8 13.5 2 9h7.5z"/>' },
      { id:'discover',      href:'/discover',   label: S.nav_journeys || 'Journeys',
        ic:'<path d="M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3z"/><path d="M9 3v15M15 6v15"/>' },
    ],
```

- [ ] **Step 4: Repoint the existing "Trace Root" item**

In the `explore` array, change the `search` item's `href` from `'/'` to `'/search'`:

```javascript
      { id:'search',      href:'/search',          label: S.nav_trace_root   || 'Trace Root',        kbd:'/',
        ic:'<circle cx="11" cy="11" r="7"/><path d="M21 21l-5-5"/>' },
```

- [ ] **Step 5: Render the Discover group first**

In `renderSidebar`, in the `side.innerHTML = ''` assignment, insert this block immediately after the `brand` anchor and before the `side-explore` group:

```javascript
      +'<div class="side-group" id="side-discover">'
        +'<div class="side-label">'+(SI.discover||'Discover')+'</div>'
        +NAV.discover.map(link).join('')
      +'</div>'
```

- [ ] **Step 6: Run the full smoke suite**

Run: `python3 -m pytest tests/test_smoke.py -v`
Expected: PASS for all paths in all four languages, including `/`, `/search`, `/discover`, `/journey/SH-L-M`.

- [ ] **Step 7: Manually verify the sidebar**

Run the app; confirm the sidebar shows a "Discover" group on top (Discover + Journeys), the active state highlights correctly on `/`, `/discover`, and `/journey/...`, and "Trace Root" under Explore now goes to `/search`.

- [ ] **Step 8: Commit**

```bash
git add static/app.js tests/test_smoke.py
git commit -m "feat(discovery): sidebar Discover group; repoint Trace Root to /search"
```

---

## Task 9: Styles for the Discover surfaces

**Files:**
- Modify: `static/style.css` (append a Discovery section at the end)
- Test: visual (no unit test; covered by smoke for render-without-error)

- [ ] **Step 1: Append styles**

Add to the end of `static/style.css`:

```css
/* ── Discovery front-end ─────────────────────────────────────── */
.home-wrap, .journey-wrap, .discover-wrap { max-width: 880px; margin: 1.5rem auto 4rem; padding: 0 1rem; }
.home-title { font-size: clamp(1.6rem, 4vw, 2.4rem); line-height: 1.15; margin: 0 0 .4rem; }
.home-sub { font-size: 1.15rem; color: var(--muted, #6b7280); margin: 0 0 1.5rem; }
.home-search { display: flex; gap: .5rem; max-width: 560px; }
.home-search input { flex: 1; padding: .7rem .9rem; font-size: 1rem; border: 1px solid var(--border, #d1d5db); border-radius: 8px; }
.home-search button { padding: .7rem 1.2rem; border: none; border-radius: 8px; background: var(--accent, #3a6bc4); color: #fff; cursor: pointer; }
.home-search-hint { font-size: .82rem; color: var(--muted, #6b7280); margin: .4rem 0 0; }
.home-rotd { margin: 2.2rem 0; }
.home-rotd-label { font-size: .72rem; text-transform: uppercase; letter-spacing: .08em; color: var(--muted, #6b7280); margin-bottom: .4rem; }
.home-rotd-card { display: flex; align-items: baseline; gap: 1rem; padding: 1rem 1.2rem; border: 1px solid var(--border, #e5e7eb); border-radius: 10px; text-decoration: none; color: inherit; }
.rotd-syriac { font-size: 2rem; }
.rotd-gloss { flex: 1; color: var(--muted, #6b7280); }
.home-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: .8rem; }
.home-card { display: flex; flex-direction: column; gap: .25rem; padding: 1rem; border: 1px solid var(--border, #e5e7eb); border-radius: 10px; text-decoration: none; color: inherit; transition: box-shadow .15s; }
.home-card:hover { box-shadow: 0 2px 10px rgba(0,0,0,.08); }
.card-syriac { font-size: 1.8rem; }
.card-key { font-size: .78rem; color: var(--muted, #6b7280); letter-spacing: .04em; }
.card-gloss { font-size: .9rem; }
.home-explore-link { margin-top: 2.5rem; font-size: .9rem; }

.journey-scripts { font-size: 1.1rem; display: flex; align-items: baseline; gap: .5rem; flex-wrap: wrap; }
.jr-syriac { font-size: 2.6rem; } .jr-hebrew { font-size: 2.2rem; } .jr-sep { color: var(--muted, #9ca3af); }
.jr-key { font-family: monospace; font-size: 1rem; color: var(--muted, #6b7280); }
.journey-gloss { font-size: 1.25rem; margin: .3rem 0; }
.journey-note { color: var(--muted, #6b7280); font-size: .95rem; }
.journey-timeline, .journey-panel, .journey-cousins, .journey-verse { margin: 2rem 0; }
.jr-bar-row { display: flex; align-items: center; gap: .6rem; margin: .3rem 0; }
.jr-bar-label { width: 140px; font-size: .85rem; }
.jr-bar { flex: 1; background: var(--bg-subtle, #f3f4f6); border-radius: 4px; height: 14px; overflow: hidden; }
.jr-bar-fill { display: block; height: 100%; background: var(--accent, #3a6bc4); }
.jr-bar-count { width: 48px; text-align: right; font-size: .82rem; color: var(--muted, #6b7280); }
.journey-panel { background: var(--bg-subtle, #f7f8fa); border-radius: 10px; padding: 1rem 1.25rem; }
.jr-pill { display: inline-block; margin: .2rem; padding: .25rem .55rem; background: var(--bg-subtle, #f3f4f6); border-radius: 999px; font-size: .85rem; }
.jr-cousin-lang { font-weight: 600; margin-right: .4rem; }
.journey-disclaimer { font-size: .82rem; font-style: italic; color: var(--muted, #6b7280); }
.journey-verse blockquote { font-size: 1.4rem; margin: 0 0 .4rem; }
.journey-more { display: flex; gap: .6rem; margin-top: 2rem; }
.journey-more .btn { padding: .5rem 1rem; border: 1px solid var(--border, #d1d5db); border-radius: 8px; text-decoration: none; color: inherit; }

.discover-shelf { display: grid; gap: 1.2rem; }
.discover-journey { border: 1px solid var(--border, #e5e7eb); border-radius: 10px; padding: 1.1rem 1.3rem; }
.discover-journey h2 { margin: 0 0 .3rem; }
.discover-blurb { color: var(--muted, #6b7280); margin: 0 0 .7rem; }
.discover-stops { margin: 0; padding-left: 1.2rem; }
.discover-stops li { margin: .3rem 0; }
.discover-stop-root { font-family: monospace; font-weight: 600; }
.discover-stop-note { color: var(--muted, #6b7280); margin-left: .4rem; }
```

- [ ] **Step 2: Manually verify**

Run the app; visit `/`, `/journey/SH-L-M`, `/discover`. Confirm layouts are clean in light and dark mode and on a narrow viewport.

- [ ] **Step 3: Commit**

```bash
git add static/style.css
git commit -m "style(discovery): home, Root Journey, and journeys-shelf styles"
```

---

## Task 10: Full regression + finish

- [ ] **Step 1: Run the entire test suite**

Run: `python3 -m pytest -q`
Expected: all tests pass (existing suite + new `tests/test_discovery.py` + expanded smoke matrix).

- [ ] **Step 2: Manual walkthrough**

Run the app and walk the newcomer path: land on `/` → click root-of-the-day → see the timeline fill → read the "one skeleton" panel and cousins → click "More journeys" → `/discover` → click a stop → another Root Journey. Confirm no console errors.

- [ ] **Step 3: Final commit (if any tweaks)**

```bash
git add -A && git commit -m "chore(discovery): polish pass after manual walkthrough"
```

---

## Self-Review

**Spec coverage:**
- §5 two doors → Tasks 4, 8 (search moved to `/search`; Discover nav group; Explore retained untouched). ✓
- §6 front door (hook + meaning search, root-of-the-day, hero grid) → Tasks 1, 2, 5. ✓
- §7 Root Journey (both scripts, timeline, "one skeleton" panel, cousins, key verse, keep-exploring) → Task 3. ✓
- §8 Discovery journeys (data files + shelf) → Tasks 6, 7. ✓
- §9 (caveat banners, citation/TEI demotion, how-it-works) → **deferred by design** (stated in Scope note). Not a gap.
- §10 root-of-the-day determinism → Task 1 Step 6 (`toordinal() % len`). ✓

**Placeholder scan:** No TBD/TODO. The two "confirm exact API key name" notes (Task 3 Step 4, Task 5 Step 4) are deliberate verification steps with defensive fallbacks already coded and tests that pass regardless — not placeholders.

**Type/name consistency:** `_featured`, `_root_of_the_day`, `_root_card`, `_load_journeys`, route fns `home`/`journey`/`discover`/`index`, template names, and the `card` context dict keys (`key/syriac/hebrew/gloss/total`) are used identically across tasks. Journey JSON shape (`id/title/blurb/stops[{root,note}]`) matches loader and `discovery.html`. ✓

**Risk note:** The only behavioral change to existing surfaces is moving search `/` → `/search`; smoke tests cover both. Any hard-coded internal link to `/` that meant "search" now lands on Discover — acceptable and intended.
