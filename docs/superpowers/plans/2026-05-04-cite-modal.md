# Multi-Format Citation Modal (B1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a "Cite" button to five analysis pages (Interlinear, Concordance, Hapax, Diachronic, Passage Profile) that opens a modal with BibTeX, Chicago, MLA, APA, and SBL citation formats for the current query, plus a Copy button and DOI/ORCID footer.

**Architecture:** A shared `static/cite-modal.js` module holds all citation logic. A `<div id="cite-modal">` fragment is added to `base.html` (like the existing share-modal). Each analysis page defines a `window.getCiteContext()` function that returns a context object describing the current query; the Cite button calls `openCiteModal(window.getCiteContext())`. Existing export buttons are left unchanged.

**Tech Stack:** Vanilla JS, Jinja2, CSS (existing modal system in `static/style.css`). No backend changes. No new dependencies.

---

## Constants (used throughout)

```
AUTHOR_FULL  = "Fresco Benaim, Jose"
AUTHOR_APA   = "Fresco Benaim, J."
YEAR         = "2026"
VERSION      = "2.3"
DOI          = "10.5281/zenodo.19358625"
DOI_URL      = "https://doi.org/10.5281/zenodo.19358625"
ORCID        = "0009-0000-2026-0836"
PROD_BASE    = "https://aramaic-root-atlas.onrender.com"
```

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `templates/base.html` | Modify | Add `<div id="cite-modal">` HTML fragment after `share-modal` block |
| `static/style.css` | Modify | Add `.cite-modal-*` tab styles (~35 lines) |
| `static/cite-modal.js` | Create | `openCiteModal(ctx)`, `closeCiteModal()`, all format builders |
| `templates/interlinear.html` | Modify | Add Cite button to `#il-action-bar`; add `getCiteContext()` |
| `templates/concordance.html` | Modify | Add Cite button to export bar; add `getCiteContext()` |
| `templates/hapax.html` | Modify | Add Cite button to export bar; add `getCiteContext()` |
| `templates/diachronic.html` | Modify | Add Cite button in `#diac-root-results`; add `getCiteContext()` |
| `templates/passage_profile.html` | Modify | Add Cite button in `#pp-results` export block; add `getCiteContext()` |

---

## Task 1: Modal HTML + CSS

**Files:**
- Modify: `templates/base.html` (after line ~167, the `</div>` closing share-modal)
- Modify: `static/style.css` (after `.share-modal-content` block, around line 1531)

### Step 1: Add modal HTML to base.html

Find the closing `</div>` of the share-modal block (looks like `    </div>\n\n    <!-- Verse Modal -->`). Insert the cite-modal HTML between share-modal and verse-modal:

```html
    <!-- Cite Modal -->
    <div id="cite-modal" class="modal-overlay" onclick="if(event.target===this)closeCiteModal()" role="dialog" aria-modal="true" aria-label="Cite this">
        <div class="modal-content cite-modal-content" onclick="event.stopPropagation()">
            <button class="modal-close" onclick="closeCiteModal()" aria-label="Close">&times;</button>
            <h3 class="cite-modal-title">Cite this</h3>
            <div class="cite-tabs" role="tablist">
                <button class="cite-tab active" data-tab="bibtex" onclick="switchCiteTab('bibtex')" role="tab">BibTeX</button>
                <button class="cite-tab" data-tab="chicago" onclick="switchCiteTab('chicago')" role="tab">Chicago</button>
                <button class="cite-tab" data-tab="mla" onclick="switchCiteTab('mla')" role="tab">MLA</button>
                <button class="cite-tab" data-tab="apa" onclick="switchCiteTab('apa')" role="tab">APA</button>
                <button class="cite-tab" data-tab="sbl" onclick="switchCiteTab('sbl')" role="tab">SBL</button>
            </div>
            <div id="cite-panel-bibtex" class="cite-panel active" role="tabpanel">
                <pre id="cite-text-bibtex" class="cite-code"></pre>
            </div>
            <div id="cite-panel-chicago" class="cite-panel" role="tabpanel">
                <pre id="cite-text-chicago" class="cite-code"></pre>
            </div>
            <div id="cite-panel-mla" class="cite-panel" role="tabpanel">
                <pre id="cite-text-mla" class="cite-code"></pre>
            </div>
            <div id="cite-panel-apa" class="cite-panel" role="tabpanel">
                <pre id="cite-text-apa" class="cite-code"></pre>
            </div>
            <div id="cite-panel-sbl" class="cite-panel" role="tabpanel">
                <pre id="cite-text-sbl" class="cite-code"></pre>
            </div>
            <div class="cite-footer">
                <button class="cite-copy-btn" id="cite-copy-btn" onclick="copyCiteText()">
                    <span class="material-symbols-outlined" style="font-size:16px;vertical-align:middle;">content_copy</span> Copy
                </button>
                <a class="cite-doi-link" href="https://doi.org/10.5281/zenodo.19358625" target="_blank" rel="noopener">
                    <span class="material-symbols-outlined" style="font-size:14px;vertical-align:middle;">link</span>
                    DOI: 10.5281/zenodo.19358625
                </a>
            </div>
            <div class="cite-orcid">ORCID: 0009-0000-2026-0836</div>
        </div>
    </div>
```

### Step 2: Add CSS to style.css

Append after the `.share-modal-content` rule block (search for `.share-modal-content {`):

```css
/* ── Cite Modal ─────────────────────────────────────────── */
.cite-modal-content {
    width: min(600px, 92vw);
    padding: 1.5rem 1.75rem 1.25rem;
}
.cite-modal-title {
    margin: 0 0 1rem;
    font-size: 1.1rem;
}
.cite-tabs {
    display: flex;
    gap: 0;
    border-bottom: 2px solid var(--border);
    margin-bottom: 1rem;
}
.cite-tab {
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    padding: .45rem .9rem;
    font-size: .85rem;
    font-weight: 500;
    color: var(--muted);
    cursor: pointer;
}
.cite-tab.active {
    color: var(--fg);
    border-bottom-color: var(--accent);
    font-weight: 700;
}
.cite-tab:hover:not(.active) { color: var(--fg); }
.cite-panel { display: none; }
.cite-panel.active { display: block; }
.cite-code {
    background: var(--bg-alt, var(--bg));
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: .85rem 1rem;
    font-size: .78rem;
    white-space: pre-wrap;
    word-break: break-word;
    margin: 0 0 .85rem;
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
    line-height: 1.55;
    color: var(--fg);
}
.cite-footer {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}
.cite-copy-btn {
    display: inline-flex;
    align-items: center;
    gap: .3rem;
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: .4rem .9rem;
    font-size: .85rem;
    font-weight: 600;
    cursor: pointer;
}
.cite-copy-btn:hover { opacity: .88; }
.cite-doi-link {
    font-size: .82rem;
    color: var(--accent);
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: .25rem;
}
.cite-doi-link:hover { text-decoration: underline; }
.cite-orcid {
    margin-top: .6rem;
    font-size: .75rem;
    color: var(--muted);
}
```

### Step 3: Verify modal HTML is well-formed

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
python3 -c "
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
t = env.get_template('base.html')
# base.html uses Jinja blocks so we just check it parses
print('base.html parses OK')
"
```

Expected: `base.html parses OK` (no Jinja syntax error).

### Step 4: Add `<script>` tag for cite-modal.js to base.html

Find the line in `base.html` that loads `autocomplete.js` or another static JS file (look for `<script src="/static/`). Add cite-modal.js after it:

```html
    <script src="/static/cite-modal.js"></script>
```

(The file doesn't exist yet — that's fine, it's loaded lazily and won't 404 crash the page until Task 2.)

Actually, to avoid a 404 in the browser during testing between tasks, create an empty placeholder first:

```bash
touch "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas/static/cite-modal.js"
```

### Step 5: Commit

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
git add templates/base.html static/style.css static/cite-modal.js
git commit -m "feat(cite): add cite-modal HTML skeleton and CSS"
```

---

## Task 2: cite-modal.js — JS logic

**Files:**
- Create: `static/cite-modal.js`

This file is standalone (no imports). It exposes three globals: `openCiteModal(ctx)`, `closeCiteModal()`, `switchCiteTab(tab)`, `copyCiteText()`.

### Step 1: Write static/cite-modal.js

```javascript
/* cite-modal.js — Multi-format citation modal for Aramaic Root Atlas
 *
 * Public API:
 *   openCiteModal(ctx)   — opens modal and renders all formats
 *   closeCiteModal()     — closes modal
 *
 * ctx object shape:
 *   tool:       string  — 'concordance'|'interlinear'|'hapax'|'diachronic'|'passage_profile'
 *   root:       string? — Latin transliteration, e.g. 'M-R-Y'
 *   rootSyriac: string? — Syriac script, e.g. 'ܡܪܝ'
 *   corpus:     string? — human-readable corpus name, e.g. 'Peshitta NT'
 *   book:       string? — book name for interlinear
 *   from:       string? — start chapter:verse for interlinear
 *   to:         string? — end chapter:verse for interlinear
 *   maxFreq:    number? — max frequency for hapax
 *   passage:    string? — passage description for passage_profile
 *   url:        string  — current page URL (window.location.href)
 */

(function () {
    'use strict';

    /* ── Constants ──────────────────────────────────────── */
    var AUTHOR_FULL = 'Fresco Benaim, Jose';
    var AUTHOR_APA  = 'Fresco Benaim, J.';
    var YEAR        = '2026';
    var VERSION     = '2.3';
    var DOI         = '10.5281/zenodo.19358625';
    var ORCID       = '0009-0000-2026-0836';

    var _currentTab = 'bibtex';

    /* ── Title builder ──────────────────────────────────── */
    function buildTitle(ctx) {
        var tool = ctx.tool || '';
        var rootPart = '';
        if (ctx.rootSyriac && ctx.root) rootPart = ctx.rootSyriac + ' (' + ctx.root + ')';
        else if (ctx.root) rootPart = ctx.root;
        else if (ctx.rootSyriac) rootPart = ctx.rootSyriac;

        var label = '';
        if (tool === 'concordance') {
            label = 'Concordance' + (rootPart ? ': ' + rootPart : '');
        } else if (tool === 'interlinear') {
            label = 'Interlinear';
            if (ctx.book) label += ': ' + ctx.book;
            if (ctx.from) label += ' ' + ctx.from;
            if (ctx.to && ctx.to !== ctx.from) label += '–' + ctx.to;
        } else if (tool === 'hapax') {
            label = 'Hapax Legomena';
            if (ctx.maxFreq != null) label += ' (≤' + ctx.maxFreq + ')';
        } else if (tool === 'diachronic') {
            label = 'Diachronic Analysis' + (rootPart ? ': ' + rootPart : '');
        } else if (tool === 'passage_profile') {
            label = 'Passage Lexical Profile' + (ctx.passage ? ': ' + ctx.passage : '');
        } else {
            label = 'Analysis';
        }

        var parts = ['Aramaic Root Atlas', label];
        if (ctx.corpus) parts.push(ctx.corpus);
        return parts.join(' — ');
    }

    /* ── BibTeX key builder ─────────────────────────────── */
    function buildKey(ctx) {
        var slug = (ctx.root || ctx.book || ctx.passage || 'ara')
            .toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
        return 'fresco2026' + (ctx.tool || 'ara').replace(/_/g, '') + '_' + slug;
    }

    /* ── Format builders ────────────────────────────────── */
    function buildBibTeX(ctx) {
        var title = buildTitle(ctx);
        var key   = buildKey(ctx);
        var url   = ctx.url || window.location.href;
        return [
            '@misc{' + key + ',',
            '  author       = {' + AUTHOR_FULL + '},',
            '  title        = {' + title.replace(/—/g, '---') + '},',
            '  year         = {' + YEAR + '},',
            '  version      = {' + VERSION + '},',
            '  doi          = {' + DOI + '},',
            '  url          = {' + url + '},',
            '  note         = {ORCID: ' + ORCID + '}',
            '}'
        ].join('\n');
    }

    function buildChicago(ctx) {
        var title = buildTitle(ctx);
        var url   = ctx.url || window.location.href;
        return AUTHOR_FULL + '. ' + YEAR + '. “' + title + '.”' +
               ' Version ' + VERSION + '. ' + url + '. ' +
               'https://doi.org/' + DOI + '.';
    }

    function buildMLA(ctx) {
        var title = buildTitle(ctx);
        var url   = ctx.url || window.location.href;
        return AUTHOR_FULL + '. “' + title + '.”' +
               ' Version ' + VERSION + ', ' + YEAR + ', ' + url + '.';
    }

    function buildAPA(ctx) {
        var title = buildTitle(ctx);
        return AUTHOR_APA + ' (' + YEAR + '). ' + title +
               ' (Version ' + VERSION + ') [Web application].' +
               ' https://doi.org/' + DOI;
    }

    function buildSBL(ctx) {
        /* SBL 2nd ed. §6.4.6 — electronic source */
        var tool = ctx.tool || '';
        var accessed = new Date().toLocaleDateString('en-US', {year:'numeric', month:'long', day:'numeric'});
        var url = ctx.url || window.location.href;
        var corpus = ctx.corpus ? ' ' + ctx.corpus + '.' : '.';
        var rootPart = ctx.root ? ' Root ' + ctx.root + '.' : '.';
        var subtitle = '';
        if (tool === 'concordance')      subtitle = ' Concordance,' + rootPart;
        else if (tool === 'interlinear') subtitle = ' Interlinear Reader.';
        else if (tool === 'hapax')       subtitle = ' Hapax Legomena.';
        else if (tool === 'diachronic')  subtitle = ' Diachronic Analysis,' + rootPart;
        else if (tool === 'passage_profile') subtitle = ' Passage Profile.';
        return AUTHOR_FULL + '.' + subtitle +
               ' “Aramaic Root Atlas”' + corpus +
               ' Accessed ' + accessed + '. ' + url + '.';
    }

    /* ── Modal controls ─────────────────────────────────── */
    window.switchCiteTab = function (tab) {
        _currentTab = tab;
        document.querySelectorAll('.cite-tab').forEach(function (btn) {
            btn.classList.toggle('active', btn.dataset.tab === tab);
        });
        document.querySelectorAll('.cite-panel').forEach(function (p) {
            p.classList.toggle('active', p.id === 'cite-panel-' + tab);
        });
    };

    window.copyCiteText = function () {
        var el = document.getElementById('cite-text-' + _currentTab);
        if (!el) return;
        navigator.clipboard.writeText(el.textContent).then(function () {
            var btn = document.getElementById('cite-copy-btn');
            if (!btn) return;
            var orig = btn.innerHTML;
            btn.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px;vertical-align:middle;">check</span> Copied!';
            setTimeout(function () { btn.innerHTML = orig; }, 1800);
        });
    };

    window.openCiteModal = function (ctx) {
        if (!ctx) return;
        var formats = {
            bibtex:  buildBibTeX(ctx),
            chicago: buildChicago(ctx),
            mla:     buildMLA(ctx),
            apa:     buildAPA(ctx),
            sbl:     buildSBL(ctx)
        };
        ['bibtex', 'chicago', 'mla', 'apa', 'sbl'].forEach(function (fmt) {
            var el = document.getElementById('cite-text-' + fmt);
            if (el) el.textContent = formats[fmt];
        });
        switchCiteTab('bibtex');
        document.getElementById('cite-modal').classList.add('active');
    };

    window.closeCiteModal = function () {
        var m = document.getElementById('cite-modal');
        if (m) m.classList.remove('active');
    };

    /* Keyboard: Escape closes the modal */
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            var m = document.getElementById('cite-modal');
            if (m && m.classList.contains('active')) closeCiteModal();
        }
    });
}());
```

### Step 2: Smoke-test the JS module

Start the dev server and open the browser console:

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
python3 app.py &
sleep 2
```

Then in the browser console on any page (e.g. http://localhost:5001):

```javascript
openCiteModal({
  tool: 'concordance',
  root: 'M-R-Y',
  rootSyriac: 'ܡܪܝ',
  corpus: 'Peshitta NT',
  url: 'https://aramaic-root-atlas.onrender.com/concordance?root=M-R-Y'
});
```

Expected: cite modal opens with BibTeX tab selected, pre-filled with correct citation text. Click Chicago/MLA/APA/SBL tabs — each shows the correct format. Click Copy — toast appears. Press Escape — modal closes.

### Step 3: Commit

```bash
kill %1 2>/dev/null; true
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
git add static/cite-modal.js
git commit -m "feat(cite): implement cite-modal.js with BibTeX, Chicago, MLA, APA, SBL formats"
```

---

## Task 3: Wire up analysis pages

**Files:**
- Modify: `templates/interlinear.html`
- Modify: `templates/concordance.html`
- Modify: `templates/hapax.html`
- Modify: `templates/diachronic.html`
- Modify: `templates/passage_profile.html`

For each page, two changes:
1. Add a `<button class="cite-btn" onclick="openCiteModal(getCiteContext())">` in the relevant results bar
2. Add a `getCiteContext()` function in the page's `<script>` block

### Cite button HTML snippet (same for all pages)

```html
<button class="cite-btn" onclick="openCiteModal(getCiteContext())" title="Cite this analysis">
    <span class="material-symbols-outlined" style="font-size:15px;vertical-align:middle;">format_quote</span>
    Cite
</button>
```

Add this CSS for `.cite-btn` in `static/style.css` (after the `.cite-orcid` rule added in Task 1):

```css
.cite-btn {
    display: inline-flex;
    align-items: center;
    gap: .3rem;
    background: none;
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: .3rem .7rem;
    font-size: .82rem;
    color: var(--fg);
    cursor: pointer;
}
.cite-btn:hover { background: var(--bg-alt, var(--border)); }
```

---

### interlinear.html

**Where to add the button:** Inside `<div class="il-export-bar">` (line ~65), after the existing export buttons.

**Updated il-export-bar:**

```html
    <div class="il-export-bar">
      <button class="il-export-btn" onclick="exportTEI()">{{ t('il_export_tei', lang) }}</button>
      <button class="il-export-btn" onclick="exportTXT()">{{ t('il_export_txt', lang) }}</button>
      <button class="il-export-btn" onclick="exportCSV()">{{ t('il_export_csv', lang) }}</button>
      <button class="cite-btn" onclick="openCiteModal(getCiteContext())" title="Cite this analysis">
          <span class="material-symbols-outlined" style="font-size:15px;vertical-align:middle;">format_quote</span> Cite
      </button>
      <label class="il-translation-toggle">
        <input type="checkbox" id="il-show-trans" checked onchange="toggleTranslation()">
        {{ t('il_translation_toggle', lang) }}
      </label>
    </div>
```

**getCiteContext() for interlinear** — add inside `<script>` block, before `document.addEventListener('keydown',`:

```javascript
function getCiteContext() {
    var corpusSel = document.getElementById('il-corpus');
    var corpusLabel = corpusSel && corpusSel.options[corpusSel.selectedIndex]
        ? corpusSel.options[corpusSel.selectedIndex].text : '';
    if (corpusLabel === '— All Corpora —' || corpusLabel === 'All Corpora' || !corpusSel.value) corpusLabel = '';
    return {
        tool: 'interlinear',
        book: document.getElementById('il-book').value || '',
        from: document.getElementById('il-ch-start').value || '',
        to:   document.getElementById('il-ch-end').value || '',
        corpus: corpusLabel,
        url: window.location.href
    };
}
```

---

### concordance.html

**Where to add the button:** Inside the export bar `<div>` at line ~60–67, alongside the existing export buttons.

Find:
```html
            <button class="btn-secondary" onclick="exportConc('csv')">
```

Add before that button:
```html
            <button class="cite-btn" onclick="openCiteModal(getCiteContext())" title="Cite this analysis">
                <span class="material-symbols-outlined" style="font-size:15px;vertical-align:middle;">format_quote</span> Cite
            </button>
```

**getCiteContext() for concordance** — add inside the `<script>` block, before the closing `</script>`:

```javascript
function getCiteContext() {
    var corpusSel = document.getElementById('conc-corpus');
    var corpusLabel = corpusSel && corpusSel.value
        ? corpusSel.options[corpusSel.selectedIndex].text : '';
    var root = (currentData && currentData.root_translit) || '';
    var rootSyr = (currentData && currentData.root) || '';
    return {
        tool: 'concordance',
        root: root,
        rootSyriac: rootSyr,
        corpus: corpusLabel,
        url: window.location.href
    };
}
```

Note: `currentData` is the variable already set by the concordance script after a successful search.

---

### hapax.html

**Where to add the button:** In the export bar `<div>` at line ~45–50, alongside CSV/JSON buttons.

Find:
```html
            <button class="btn-secondary" onclick="exportHapax('csv')">
```

Add before that button:
```html
            <button class="cite-btn" onclick="openCiteModal(getCiteContext())" title="Cite this analysis">
                <span class="material-symbols-outlined" style="font-size:15px;vertical-align:middle;">format_quote</span> Cite
            </button>
```

**getCiteContext() for hapax** — add inside `<script>` block, before closing `</script>`:

```javascript
function getCiteContext() {
    var freqEl = document.getElementById('freq-slider') || document.getElementById('freq-input');
    var maxFreq = freqEl ? parseInt(freqEl.value) || 1 : 1;
    var corpusSel = document.getElementById('corpus-filter');
    var corpusLabel = corpusSel && corpusSel.value
        ? corpusSel.options[corpusSel.selectedIndex].text : '';
    return {
        tool: 'hapax',
        maxFreq: maxFreq,
        corpus: corpusLabel,
        url: window.location.href
    };
}
```

**Verify the exact IDs of the hapax frequency slider before writing this.** Read `templates/hapax.html` lines 18–45 to find the actual element ID for the frequency slider. Use whatever ID you find.

---

### diachronic.html

**Where to add the button:** Inside `<div id="diac-root-results">`, near the existing export button. Find the `exportShifts` button area or the root title div. Add a Cite button next to the root title.

Find the `<h3>` or title element inside `#diac-root-results` (around line 45–55):
```html
<h3 id="diac-root-title" ...>
```

Add after that `<h3>` line:
```html
                <button class="cite-btn" style="margin-left:.5rem;" onclick="openCiteModal(getCiteContext())" title="Cite this analysis">
                    <span class="material-symbols-outlined" style="font-size:15px;vertical-align:middle;">format_quote</span> Cite
                </button>
```

**Verify the exact structure of `#diac-root-results` before editing.** Read `templates/diachronic.html` lines 43–60 to find the right injection point.

**getCiteContext() for diachronic** — add inside `<script>` block, before closing `</script>`:

```javascript
function getCiteContext() {
    var rootInput = document.getElementById('diac-root-input');
    var root = rootInput ? rootInput.value.trim().toUpperCase() : '';
    var titleEl = document.getElementById('diac-root-title');
    var rootSyr = titleEl ? titleEl.textContent.trim() : '';
    return {
        tool: 'diachronic',
        root: root,
        rootSyriac: rootSyr,
        url: window.location.href
    };
}
```

---

### passage_profile.html

**Where to add the button:** Inside the export block `<!-- Export buttons -->` at line ~119–128.

Find:
```html
            <button onclick="exportJSON()"
```

Add before that button:
```html
            <button class="cite-btn" onclick="openCiteModal(getCiteContext())" title="Cite this analysis">
                <span class="material-symbols-outlined" style="font-size:15px;vertical-align:middle;">format_quote</span> Cite
            </button>
```

**getCiteContext() for passage_profile** — add inside `<script>` block, before closing `</script>`:

```javascript
function getCiteContext() {
    var passageInput = document.getElementById('pp-passage') || document.getElementById('passage-input');
    var passage = passageInput ? passageInput.value.trim() : '';
    return {
        tool: 'passage_profile',
        passage: passage,
        url: window.location.href
    };
}
```

**Verify the exact ID of the passage input field before writing.** Read `templates/passage_profile.html` lines 1–40 to find the right ID.

---

### Verification for all 5 pages

Start the server, then check each page:

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
python3 app.py &
sleep 2
# Check all 5 pages load without JS errors:
for page in interlinear concordance hapax diachronic passage_profile; do
    code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/$page)
    echo "$page: $code"
done
kill %1 2>/dev/null
```

Expected: all 5 return `200`.

Then manually open each page, perform a search/load to reveal the results area, and verify:
- Cite button appears
- Clicking it opens the modal
- BibTeX contains the correct root/passage/corpus context
- Switching tabs shows different formats
- Copy button works
- Escape closes the modal

### Commit

```bash
cd "/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas"
git add templates/interlinear.html templates/concordance.html templates/hapax.html \
        templates/diachronic.html templates/passage_profile.html static/style.css
git commit -m "feat(cite): wire Cite button to all 5 analysis pages"
```

---

## Self-Review

**Spec coverage:**
- ✅ BibTeX tab — Task 2 `buildBibTeX()`
- ✅ Chicago tab — Task 2 `buildChicago()`
- ✅ MLA tab — Task 2 `buildMLA()`
- ✅ APA tab — Task 2 `buildAPA()`
- ✅ SBL tab — Task 2 `buildSBL()`
- ✅ Copy button — Task 2 `copyCiteText()` with "Copied!" feedback
- ✅ DOI link in footer — Task 1 HTML
- ✅ ORCID in footer — Task 1 HTML
- ✅ Auto-generated title from current query context — Task 2 `buildTitle()`
- ✅ Interlinear page — Task 3
- ✅ Concordance page — Task 3
- ✅ Hapax page — Task 3
- ✅ Diachronic page — Task 3
- ✅ Passage Profile page — Task 3
- ✅ Escape key closes modal — Task 2 `keydown` listener
- ✅ Click backdrop closes modal — Task 1 HTML `onclick` on overlay

**Placeholder scan:** None. All citation format strings are fully specified. Two "Verify the exact ID" notes are inspection instructions, not placeholders — the implementer reads the file first.

**Type consistency:**
- `openCiteModal(ctx)` defined in Task 2, called with `getCiteContext()` in Task 3 — matches.
- `switchCiteTab(tab)` defined in Task 2, called from HTML `onclick` in Task 1 — matches.
- `copyCiteText()` defined in Task 2, called from HTML `onclick` in Task 1 — matches.
- `closeCiteModal()` defined in Task 2, called from HTML `onclick` in Task 1 and Escape handler — matches.
- `getCiteContext()` defined per-page in Task 3 — used in Task 3 button `onclick` — matches.
