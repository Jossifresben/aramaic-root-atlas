# UI Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the new Claude Designer mockup to all pages of the Aramaic Root Atlas, replacing the top-navbar layout with a fixed sidebar and warm-parchment design system.

**Architecture:** The new design delivers a complete CSS design system (752 lines) plus a vanilla-JS sidebar renderer (`app.js`). Each Jinja2 template extends `base.html`, which provides the `<div class="app">` grid shell with a dynamically-rendered `<aside class="side">`. Page-specific content goes inside `<main class="content">`. Components not designed by Claude Designer (heatmap, parallel, visualize, constellation, bookmarks, about, annotations, collocations, semantic fields, parse, passage profile) receive the new shell + adapted typography but keep their existing JS and data layers intact.

**Tech Stack:** Flask/Jinja2, vanilla CSS (no framework), vanilla JS, D3.js (unchanged for visualizer/constellation), driver.js (tour, unchanged)

**Source of truth for new design:** `/Users/jfresco16/Downloads/Aramaic-design/` — read these files for every pixel decision:
- `static/style.css` — new design system (752 lines)
- `static/app.js` — sidebar renderer + theme toggle
- `index.html`, `reader.html`, `browse.html`, `concordance.html`, `diachronic.html`, `interlinear.html`

**Worktree:** `/Users/jfresco16/Google Drive/Claude/aramaic-root-atlas/.worktrees/ui-redesign/`
**Branch:** `feature/ui-redesign`

---

## CSS Migration Reference

Variables that change between old and new design:

| Old var | New var |
|---------|---------|
| `--fg` | `--ink` |
| `--muted` | `--ink-3` |
| `--border` | `--rule` |
| `--card-bg` | `--surface` |
| `--bg-alt` | `--bg-2` |
| `--radius` | removed (hardcoded values) |
| `--syriac-font` | `--syr` |

Dark mode:
- Old: `.dark` class on `<body>`
- New: `[data-theme="dark"]` attribute on `<html>` element
- localStorage key: old uses `'theme'`, new design uses `'ara.theme'`
- **Decision:** standardise on `'ara.theme'` in both global.js and app.js

Corpus badge classes:
- Old: `.corpus-badge.corpus-peshitta_nt`, `.corpus-badge.corpus-peshitta_ot`, etc.
- New: `.cbadge.pnt`, `.cbadge.pot`, `.cbadge.bib`, `.cbadge.tar`, `.cbadge.eph`
- JS-generated badges (global.js lines 296-300, 797, 930): update to new class names

---

## File Map

**Replace entirely:**
- `static/style.css` — new design CSS + appended legacy component CSS

**Create new:**
- `static/app.js` — sidebar renderer (adapted Flask URLs), theme toggle

**Heavily modify:**
- `templates/base.html` — strip old nav, add app shell, keep modals + scripts
- `static/js/global.js` — update dark mode localStorage key, update corpus badge class names

**Port to new design (markup overhaul):**
- `templates/index.html`
- `templates/browse.html`
- `templates/read.html`
- `templates/concordance.html`
- `templates/diachronic.html`
- `templates/interlinear.html`

**Extend new shell (new page-head + topbar, keep existing JS data layer):**
- `templates/hapax.html`
- `templates/heatmap.html`
- `templates/passage_profile.html`
- `templates/collocations.html`
- `templates/parallel.html`
- `templates/visualize.html`
- `templates/constellation.html`
- `templates/bookmarks.html`
- `templates/about.html`
- `templates/annotations.html`
- `templates/semantic_fields.html`
- `templates/parse.html`

---

## Task 1: Replace static/style.css

**Files:**
- Replace: `static/style.css`

The new `style.css` = new design CSS (all 752 lines from the Designer file) **followed by** a "legacy bridge" section preserving CSS for features the Designer didn't mock up. The legacy bridge updates old variable names to new ones.

- [ ] **Step 1: Copy the new design CSS as the new style.css**

Read `/Users/jfresco16/Downloads/Aramaic-design/static/style.css` (752 lines) and write it verbatim to `static/style.css` in the worktree.

Run: `wc -l static/style.css` → expect 752

- [ ] **Step 2: Append the legacy bridge CSS block**

Append the following at the end of `static/style.css`. This preserves components for features not yet re-designed, migrating all variable names to the new system:

```css
/* ═══════════════════════════════════════════════════════════════
   LEGACY BRIDGE — components for unported pages
   Variables updated to new design system tokens.
   Remove sections as pages get properly ported.
   ═══════════════════════════════════════════════════════════════ */

/* — Modal shell (shared by share, cite, verse modals) — */
.modal-overlay{
  display:none;position:fixed;inset:0;z-index:1000;
  background:rgba(0,0,0,.55);
  align-items:center;justify-content:center;
}
.modal-overlay.active{display:flex}
.modal-content{
  background:var(--surface);border:1px solid var(--rule);border-radius:8px;
  position:relative;max-height:90vh;overflow-y:auto;
  box-shadow:var(--shadow-2);
}
.modal-close{
  position:absolute;top:14px;right:16px;
  font-size:22px;color:var(--ink-3);background:none;border:0;cursor:pointer;line-height:1;
}
.modal-close:hover{color:var(--ink)}

/* — Share modal — */
.share-modal-content{width:min(440px,92vw);padding:32px}
.share-modal-title{font-family:var(--serif);font-size:22px;font-weight:500;margin:0 0 20px}
.share-qr-wrap{display:flex;flex-direction:column;align-items:center;gap:10px;margin-bottom:18px}
.share-qr-hint{font-family:var(--sans);font-size:12px;color:var(--ink-3)}
.share-url-wrap{display:flex;gap:8px;align-items:center}
.share-url-input{flex:1;padding:8px 10px;border:1px solid var(--rule);border-radius:4px;background:var(--bg-2);font-family:var(--mono);font-size:12px;color:var(--ink-2)}
.share-copy-btn{padding:8px 10px;border:1px solid var(--rule);border-radius:4px;background:var(--surface);color:var(--ink-2);cursor:pointer}
.share-copy-btn:hover{background:var(--bg-2);color:var(--ink)}

/* — Cite modal — */
.cite-modal-content{width:min(600px,92vw);padding:32px}
.cite-modal-title{font-family:var(--serif);font-size:22px;font-weight:500;margin:0 0 18px;color:var(--ink)}
.cite-tabs{display:flex;gap:0;border-bottom:1px solid var(--rule);margin-bottom:0}
.cite-tab{
  font-family:var(--sans);font-size:13px;font-weight:500;
  color:var(--ink-3);padding:10px 16px;
  position:relative;border:0;background:none;cursor:pointer;
}
.cite-tab.active{color:var(--ink)}
.cite-tab.active::after{
  content:"";position:absolute;left:0;right:0;bottom:-1px;
  height:2px;background:var(--accent);
}
.cite-panel{display:none;padding:18px 0 0}
.cite-panel.active{display:block}
.cite-code{
  background:var(--bg-2);border:1px solid var(--rule);border-radius:4px;
  padding:14px 16px;font-family:var(--mono);font-size:12.5px;color:var(--ink-2);
  white-space:pre-wrap;word-break:break-all;line-height:1.6;margin:0;
  max-height:220px;overflow-y:auto;
}
.cite-footer{
  display:flex;justify-content:space-between;align-items:center;
  margin-top:16px;padding-top:16px;border-top:1px solid var(--rule-soft);
}
.cite-copy-btn{
  display:inline-flex;align-items:center;gap:6px;
  padding:8px 14px;border:1px solid var(--rule);border-radius:4px;
  font-family:var(--sans);font-size:13px;color:var(--ink-2);
  background:var(--surface);cursor:pointer;
}
.cite-copy-btn:hover{background:var(--bg-2);border-color:var(--ink-3);color:var(--ink)}
.cite-doi-link{font-family:var(--sans);font-size:12px;color:var(--link);display:inline-flex;align-items:center;gap:4px}
.cite-orcid{font-family:var(--mono);font-size:11px;color:var(--ink-4);margin-top:10px}

/* — Verse modal — */
.verse-modal-content{width:min(680px,92vw);padding:0;max-height:88vh}
.modal-sticky-header{
  position:sticky;top:0;background:var(--surface);
  border-bottom:1px solid var(--rule);padding:14px 20px;
  display:flex;align-items:center;gap:12px;z-index:1;
}
.modal-ref{font-family:var(--mono);font-size:12px;color:var(--ink-3);letter-spacing:.04em;margin-right:auto}
.modal-copy{font-size:16px;color:var(--ink-3);padding:4px 8px;border:1px solid var(--rule);border-radius:4px}
.modal-copy:hover{background:var(--bg-2);color:var(--ink)}
.modal-nav-arrow{
  display:block;width:100%;padding:10px;border:0;border-top:1px solid var(--rule);
  color:var(--ink-3);font-size:14px;background:var(--surface);cursor:pointer;
}
.modal-nav-arrow:disabled{opacity:.3;cursor:default}
.modal-nav-arrow:not(:disabled):hover{background:var(--bg-2);color:var(--ink)}
#modal-verses-container{padding:20px}
.modal-loading{padding:20px;font-family:var(--sans);font-size:13px;color:var(--ink-3);text-align:center}
.modal-verse{margin-bottom:20px;padding-bottom:20px;border-bottom:1px solid var(--rule-soft)}
.modal-verse:last-child{border-bottom:0;margin-bottom:0}
.modal-verse-syr{font-family:var(--syr);font-size:24px;direction:rtl;text-align:right;color:var(--ink);line-height:1.55;margin-bottom:6px}
.modal-verse-trans{font-family:var(--serif);font-size:15px;color:var(--ink-2);font-style:italic;font-weight:300}

/* — Word popover (reader) — */
.word-pop{
  position:absolute;z-index:200;
  background:var(--surface);border:1px solid var(--rule);border-radius:6px;
  padding:14px 16px;min-width:220px;max-width:320px;
  box-shadow:var(--shadow-2);font-family:var(--sans);font-size:13px;
}
.word-pop-root{font-family:var(--mono);font-size:14px;font-weight:600;color:var(--accent);letter-spacing:.04em;margin-bottom:6px}
.word-pop-gloss{font-family:var(--serif);font-style:italic;color:var(--ink-2);margin-bottom:6px}
.word-pop-conf{font-size:11px;color:var(--ink-3);display:flex;align-items:center;gap:6px}
.word-pop-stem{display:inline-block;padding:2px 7px;border-radius:8px;font-size:10.5px;background:var(--bg-2);color:var(--ink-2);margin-top:4px}
.word-pop-link{display:block;margin-top:8px;font-size:12px;color:var(--link)}
.word-pop-close{position:absolute;top:6px;right:8px;color:var(--ink-4);font-size:16px;cursor:pointer}

/* — Stem badges — */
.stem-badge{display:inline-block;padding:2px 7px;border-radius:8px;font-family:var(--sans);font-size:10.5px;font-weight:500;white-space:nowrap}
.stem-badge.peal{background:#e8f0e8;color:#2d5a2d}
.stem-badge.ethpeel{background:#dce8f0;color:#1a4a6e}
.stem-badge.pael{background:#f0e8d8;color:#6b3a1f}
.stem-badge.ethpaal{background:#ece8f0;color:#4a3070}
.stem-badge.aphel{background:#f0ece0;color:#5a4a1a}
.stem-badge.shafel{background:#f0e0e0;color:#6b1f1f}
.stem-badge.ettaphal{background:#e0e8e0;color:#1f5a3a}
[data-theme="dark"] .stem-badge.peal{background:#1e3520;color:#8ac98a}
[data-theme="dark"] .stem-badge.ethpeel{background:#162030;color:#6a9bbf}
[data-theme="dark"] .stem-badge.pael{background:#2a1a0f;color:#d49968}
[data-theme="dark"] .stem-badge.ethpaal{background:#1e1530;color:#9a80c4}
[data-theme="dark"] .stem-badge.aphel{background:#251e08;color:#b4a055}
[data-theme="dark"] .stem-badge.shafel{background:#250f0f;color:#c47070}
[data-theme="dark"] .stem-badge.ettaphal{background:#0f2018;color:#60c490}

/* — Autocomplete dropdown — */
.autocomplete-wrap{position:relative;flex:1}
.autocomplete-list{
  position:absolute;top:100%;left:0;right:0;z-index:100;
  background:var(--surface);border:1px solid var(--rule);border-top:0;border-radius:0 0 4px 4px;
  max-height:240px;overflow-y:auto;box-shadow:var(--shadow-2);
}
.autocomplete-item{
  padding:9px 12px;font-family:var(--mono);font-size:13px;cursor:pointer;
  display:flex;align-items:center;gap:10px;
}
.autocomplete-item:hover{background:var(--bg-2)}
.autocomplete-item .ac-syr{font-family:var(--syr);font-size:18px;color:var(--ink)}
.autocomplete-item .ac-gloss{font-size:12px;color:var(--ink-3);font-style:italic;font-family:var(--serif)}

/* — Chapter root summary panel (reader) — */
.chapter-root-panel{
  background:var(--surface);border:1px solid var(--rule);border-radius:6px;
  padding:18px;margin-top:24px;
}
.chapter-root-panel h3{font-family:var(--sans);font-size:11px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3);margin:0 0 14px}
.root-freq-table{width:100%;border-collapse:collapse;font-family:var(--sans);font-size:13px}
.root-freq-table th{text-align:left;color:var(--ink-3);padding:6px 10px 6px 0;border-bottom:1px solid var(--rule);font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase}
.root-freq-table td{padding:8px 10px 8px 0;border-bottom:1px solid var(--rule-soft);vertical-align:middle;color:var(--ink-2)}
.root-freq-table td:first-child{font-family:var(--mono);color:var(--accent);font-size:13px}
.root-freq-table .root-syr{font-family:var(--syr);font-size:18px;color:var(--ink)}

/* — Settings dropdown (sidebar replacement for toolbar) — */
.settings-wrapper,.lang-wrapper{position:relative}
.settings-dropdown,.lang-dropdown{
  position:absolute;top:calc(100% + 6px);right:0;
  background:var(--surface);border:1px solid var(--rule);border-radius:6px;
  min-width:200px;box-shadow:var(--shadow-2);z-index:200;
  display:none;padding:6px 0;
}
.settings-dropdown.open,.lang-dropdown.open{display:block}
.settings-option,.lang-option{
  display:block;padding:9px 16px;font-family:var(--sans);font-size:13px;
  color:var(--ink-2);cursor:pointer;background:none;border:0;width:100%;text-align:left;
}
.settings-option:hover,.lang-option:hover{background:var(--bg-2);color:var(--ink)}
.settings-option.active,.lang-option.active{color:var(--accent);font-weight:500}
.settings-label{
  padding:8px 16px 4px;font-family:var(--sans);font-size:10.5px;
  font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-4);
}
.settings-divider{height:1px;background:var(--rule-soft);margin:6px 0}
.nav-drop-sep{height:1px;background:var(--rule-soft);margin:4px 0;border:0}

/* — Nav button (topbar icon button, settings trigger) — */
.nav-btn{
  width:32px;height:32px;border-radius:4px;display:inline-grid;place-items:center;
  color:var(--ink-3);cursor:pointer;background:none;border:0;
  font-size:20px;
}
.nav-btn:hover{background:var(--bg-2);color:var(--ink);text-decoration:none}

/* — Bookmark notification toast — */
.bookmark-toast{
  position:fixed;bottom:24px;right:24px;z-index:500;
  background:var(--ink);color:var(--bg);
  padding:10px 18px;border-radius:4px;
  font-family:var(--sans);font-size:13px;
  box-shadow:var(--shadow-2);
  opacity:0;transform:translateY(8px);
  transition:opacity .2s,transform .2s;
  pointer-events:none;
}
.bookmark-toast.show{opacity:1;transform:translateY(0)}

/* — Root highlight (from search result nav) — */
.word-highlight{background:var(--gold-soft);outline:2px solid var(--gold-mark);border-radius:2px}

/* — Parallel viewer columns — */
.parallel-cols{display:grid;gap:24px;margin-top:24px}
.parallel-cols.cols-2{grid-template-columns:1fr 1fr}
.parallel-cols.cols-3{grid-template-columns:repeat(3,1fr)}
.parallel-col{background:var(--surface);border:1px solid var(--rule);border-radius:6px;overflow:hidden}
.parallel-col-head{padding:12px 16px;border-bottom:1px solid var(--rule);background:var(--bg-2);display:flex;align-items:center;gap:8px}
.parallel-col-head h3{font-family:var(--sans);font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);margin:0}
.parallel-verse{padding:14px 16px;border-bottom:1px solid var(--rule-soft)}
.parallel-verse:last-child{border-bottom:0}
.parallel-ref{font-family:var(--mono);font-size:11px;color:var(--ink-4);margin-bottom:4px}
.parallel-syr{font-family:var(--syr);font-size:22px;direction:rtl;text-align:right;color:var(--ink);line-height:1.5}
.parallel-trans{font-family:var(--serif);font-size:13px;color:var(--ink-2);font-style:italic;margin-top:4px}

/* — Heat map — */
.heatmap-grid{display:grid;gap:3px;margin-top:16px}
.heatmap-row{display:contents}
.hm-cell{
  padding:8px 10px;font-family:var(--mono);font-size:11.5px;font-variant-numeric:tabular-nums;
  border-radius:2px;cursor:pointer;text-align:center;color:var(--ink);
  background:color-mix(in oklab, var(--accent) 8%, var(--surface));
}
.hm-cell:hover{opacity:.85}
.hm-cell.hm-1{background:color-mix(in oklab, var(--accent) 14%, var(--surface))}
.hm-cell.hm-2{background:color-mix(in oklab, var(--accent) 28%, var(--surface))}
.hm-cell.hm-3{background:color-mix(in oklab, var(--accent) 50%, var(--surface));color:#fff}
.hm-cell.hm-4{background:color-mix(in oklab, var(--accent) 75%, var(--surface));color:#fff}
.hm-root{font-size:10px;color:var(--ink-4);margin-top:2px;letter-spacing:.04em}

/* — Visualizer (D3 page) — */
#viz-container{width:100%;height:540px;background:var(--surface);border:1px solid var(--rule);border-radius:6px;overflow:hidden}
.viz-root-card{background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:20px;margin-top:20px}
.viz-root-card h2{font-family:var(--serif);font-size:26px;font-weight:500;margin:0 0 6px}
.viz-gloss{font-family:var(--serif);font-size:18px;font-style:italic;color:var(--ink-2);margin-bottom:12px}
.viz-badges{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}
.viz-sister-roots{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.viz-sister-root{padding:4px 10px;border:1px solid var(--rule);border-radius:14px;font-family:var(--mono);font-size:12px;color:var(--ink-2);cursor:pointer}
.viz-sister-root:hover{border-color:var(--ink-3);color:var(--ink);background:var(--surface-2)}

/* — Constellation page — */
#constellation-container{width:100%;height:580px;background:var(--surface);border:1px solid var(--rule);border-radius:6px;overflow:hidden}

/* — Bookmarks page — */
.bm-tabs{display:flex;gap:0;border-bottom:1px solid var(--rule);margin-bottom:24px}
.bm-tab{
  font-family:var(--sans);font-size:13px;font-weight:500;color:var(--ink-3);
  padding:10px 20px;position:relative;cursor:pointer;border:0;background:none;
}
.bm-tab.active{color:var(--ink)}
.bm-tab.active::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:2px;background:var(--accent)}
.bm-empty{font-family:var(--serif);font-size:18px;color:var(--ink-3);font-style:italic;text-align:center;padding:48px 0}
.bm-tag{display:inline-block;padding:2px 8px;border-radius:10px;background:var(--bg-2);border:1px solid var(--rule);font-family:var(--sans);font-size:11px;color:var(--ink-3)}

/* — Passage profile stat cards — */
.pp-stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:14px;margin:24px 0}
.pp-stat{background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:16px 18px}
.pp-stat-num{font-family:var(--serif);font-size:26px;font-weight:500;color:var(--ink);letter-spacing:-.01em;line-height:1.1}
.pp-stat-label{font-family:var(--sans);font-size:11px;color:var(--ink-3);font-weight:500;letter-spacing:.06em;text-transform:uppercase;margin-top:4px}

/* — About page — */
.about-section{max-width:720px;margin-bottom:48px}
.about-section h2{font-family:var(--serif);font-size:28px;font-weight:500;letter-spacing:-.01em;margin:0 0 16px}
.about-section p{font-family:var(--serif);font-size:18px;line-height:1.65;color:var(--ink-2);font-weight:300;margin:0 0 14px}
.about-section ul{font-family:var(--serif);font-size:17px;line-height:1.65;color:var(--ink-2);font-weight:300;margin:0 0 14px;padding-left:1.4em}
.about-caveat{border-left:3px solid var(--accent-soft);padding-left:16px;font-style:italic;color:var(--ink-3);margin:20px 0}

/* — Tour styles (driver.js overrides) — */
.driver-popover{font-family:var(--sans) !important;border-radius:6px !important}
.driver-popover-title{font-family:var(--serif) !important;font-size:18px !important}

/* — Collocations page — */
.coll-matrix td,.coll-matrix th{padding:6px 10px;font-family:var(--mono);font-size:12px;border:1px solid var(--rule-soft);text-align:right;font-variant-numeric:tabular-nums}
.coll-matrix th{background:var(--bg-2);color:var(--ink-3);font-size:10px;letter-spacing:.06em;text-transform:uppercase;font-family:var(--sans)}

/* — Semantic fields page — */
.sf-cluster{background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:18px;margin-bottom:20px}
.sf-cluster h3{font-family:var(--serif);font-size:20px;font-weight:500;margin:0 0 10px}
.sf-roots{display:flex;gap:8px;flex-wrap:wrap}
.sf-root-pill{padding:4px 12px;border-radius:14px;background:var(--bg-2);border:1px solid var(--rule);font-family:var(--mono);font-size:12.5px;color:var(--ink-2);cursor:pointer}
.sf-root-pill:hover{border-color:var(--ink-3);color:var(--ink)}

/* — Parse page — */
.parse-result{background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:20px;margin-top:20px}
.parse-word{font-family:var(--syr);font-size:40px;direction:rtl;text-align:right;margin-bottom:12px}
.parse-row{display:grid;grid-template-columns:140px 1fr;gap:10px;padding:6px 0;border-bottom:1px solid var(--rule-soft);font-family:var(--sans);font-size:13px}
.parse-row dt{color:var(--ink-3);font-weight:500;letter-spacing:.04em}
.parse-row dd{color:var(--ink);margin:0}

/* — Spacer utility — */
.spacer{flex:1 1 auto}
```

- [ ] **Step 3: Verify the file looks right**

Run: `wc -l static/style.css` → expect ≥ 950 lines

- [ ] **Step 4: Commit**

```bash
git add static/style.css
git commit -m "style: replace CSS with new design system + legacy bridge"
```

---

## Task 2: Create static/app.js

**Files:**
- Create: `static/app.js`

The new `app.js` renders the sidebar dynamically from a NAV data object. URLs are Flask routes, not `.html` files. Theme toggle (`setTheme`) uses localStorage key `'ara.theme'` and `data-theme` on `<html>`.

- [ ] **Step 1: Create static/app.js**

```js
// Aramaic Root Atlas — app shell
// Sidebar renderer + theme persistence

(function(){
  // ── Theme persistence ──────────────────────────────────
  var root = document.documentElement;
  var saved = localStorage.getItem('ara.theme');
  if(saved){ root.setAttribute('data-theme', saved); }

  function setTheme(t){
    if(t === 'system'){
      root.removeAttribute('data-theme');
      localStorage.removeItem('ara.theme');
    } else {
      root.setAttribute('data-theme', t);
      localStorage.setItem('ara.theme', t);
    }
    syncThemeToggle();
  }
  function syncThemeToggle(){
    var cur = localStorage.getItem('ara.theme') || 'system';
    document.querySelectorAll('.theme-tog button').forEach(function(b){
      b.classList.toggle('on', b.dataset.theme === cur);
    });
  }
  window.setTheme = setTheme;

  // ── Sidebar nav data — Flask URL routing ────────────────
  var NAV = {
    tools: [
      { id:'search',      href:'/',             label:'Search',      kbd:'/',
        ic:'<circle cx="11" cy="11" r="7"/><path d="M21 21l-5-5"/>' },
      { id:'reader',      href:'/read/Matthew/1', label:'Reader',
        ic:'<path d="M3 5h7a3 3 0 013 3v12M21 5h-7a3 3 0 00-3 3v12"/>' },
      { id:'concordance', href:'/concordance',  label:'Concordance',
        ic:'<path d="M4 6h16M4 12h16M4 18h10"/>' },
      { id:'diachronic',  href:'/diachronic',   label:'Diachronic',
        ic:'<path d="M3 20V4M3 20h18M7 16l3-4 4 2 5-7"/>' },
      { id:'interlinear', href:'/interlinear',  label:'Interlinear',
        ic:'<path d="M3 6h18M3 11h18M3 16h12M3 21h18"/>' },
    ],
    ref: [
      { id:'browse',    href:'/browse',       label:'Browse corpora',
        ic:'<rect x="4" y="4" width="7" height="7"/><rect x="13" y="4" width="7" height="7"/><rect x="4" y="13" width="7" height="7"/><rect x="13" y="13" width="7" height="7"/>' },
      { id:'hapax',     href:'/hapax',        label:'Hapax legomena',
        ic:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>' },
      { id:'heatmap',   href:'/heatmap',      label:'Frequency map',
        ic:'<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>' },
      { id:'about',     href:'/about',        label:'About & method',
        ic:'<circle cx="12" cy="12" r="9"/><path d="M12 8v4M12 16v.01"/>' },
    ],
  };

  function renderSidebar(){
    var side = document.querySelector('.side');
    if(!side) return;
    var active = side.dataset.page || 'search';
    function link(it){
      return '<a href="'+it.href+'" class="side-link'+(it.id===active?' active':'')+'">'
        +'<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor">'+it.ic+'</svg>'
        +it.label
        +(it.kbd?'<span class="kbd">'+it.kbd+'</span>':'')
        +'</a>';
    }
    side.innerHTML = ''
      +'<a href="/" class="brand">'
        +'<div class="brand-mark">ܐ</div>'
        +'<div class="brand-text"><div class="brand-name">Root Atlas</div>'
        +'<div class="brand-sub">Aramaic Corpora</div></div>'
      +'</a>'
      +'<div class="side-group">'
        +'<div class="side-label">Tools</div>'
        +NAV.tools.map(link).join('')
      +'</div>'
      +'<div class="side-group">'
        +'<div class="side-label">Reference</div>'
        +NAV.ref.map(link).join('')
      +'</div>'
      +'<div class="side-group">'
        +'<div class="side-label">Workspace</div>'
        +'<a href="/bookmarks" class="side-link'+(active==='bookmarks'?' active':'')+'">'
          +'<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor">'
          +'<path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg>Bookmarks</a>'
        +'<a href="/parallel" class="side-link'+(active==='parallel'?' active':'')+'">'
          +'<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor">'
          +'<path d="M3 6h18M3 12h18M3 18h18"/></svg>Parallel viewer</a>'
      +'</div>'
      +'<div class="side-foot">'
        +'<div>By <a href="https://jossifresco.com">Jossi Fresco</a> · '
          +'<a href="https://github.com/Jossifresben/aramaic-root-atlas">GitHub</a></div>'
        +'<div class="v">v 2.4 · DOI 10.5281/zenodo.19358625</div>'
        +'<div class="theme-tog" role="group" aria-label="Theme">'
          +'<button data-theme="light" onclick="setTheme(\'light\')">Light</button>'
          +'<button data-theme="dark"  onclick="setTheme(\'dark\')">Dark</button>'
          +'<button data-theme="system" onclick="setTheme(\'system\')">Auto</button>'
        +'</div>'
      +'</div>';
    syncThemeToggle();
  }

  // ── UI helpers ─────────────────────────────────────────
  window.switchSearchTab = function(name){
    document.querySelectorAll('.s-tab').forEach(function(t){t.classList.toggle('active',t.dataset.tab===name)});
    document.querySelectorAll('.s-panel').forEach(function(p){p.classList.toggle('hidden',p.dataset.panel!==name)});
  };
  window.toggleTranslit = function(){
    var el = document.getElementById('translit-help');
    if(el) el.classList.toggle('hidden');
  };
  window.fillExample = function(val){
    var inp = document.querySelector('.s-panel:not(.hidden) .s-input') || document.querySelector('.s-input');
    if(inp){ inp.value = val; inp.focus(); }
  };
  window.switchTab = function(group, name){
    document.querySelectorAll('[data-tabs="'+group+'"] .tab').forEach(function(t){
      t.classList.toggle('active',t.dataset.tab===name);
    });
    document.querySelectorAll('[data-panes="'+group+'"] .pane[data-pane]').forEach(function(p){
      p.classList.toggle('hidden',p.dataset.pane!==name);
    });
  };
  window.toggleChip = function(btn){ btn.classList.toggle('on'); };

  document.addEventListener('DOMContentLoaded', function(){
    renderSidebar();
    syncThemeToggle();
  });
})();
```

- [ ] **Step 2: Commit**

```bash
git add static/app.js
git commit -m "feat: add sidebar renderer app.js with Flask URL routing"
```

---

## Task 3: Update static/js/global.js — dark mode + corpus badge classes

**Files:**
- Modify: `static/js/global.js`

Two changes: (1) consolidate dark mode localStorage key from `'theme'` to `'ara.theme'`; (2) update JS-generated corpus badge class names from `.corpus-badge.corpus-<id>` to `.cbadge.<abbr>`.

- [ ] **Step 1: Update localStorage key for theme**

In `static/js/global.js`, find and replace the two occurrences:

Old (line ~19): `var savedTheme = localStorage.getItem('theme');`
New: `var savedTheme = localStorage.getItem('ara.theme');`

Old (line ~25): `localStorage.setItem('theme', next);`
New: `localStorage.setItem('ara.theme', next);`

- [ ] **Step 2: Update corpus badge class generation in JS**

Define a corpus abbreviation map at the top of the DOMContentLoaded block (or near the badge-generating code):

Old pattern (lines ~296-300):
```js
html += `<span class="corpus-badge corpus-${cid}">${corpusLabels[cid] || cid}: ${att[cid]}×</span>`;
```

New pattern:
```js
var CORPUS_ABBR = {peshitta_nt:'pnt',peshitta_ot:'pot',biblical_aramaic:'bib',targum_onkelos:'tar',ephrem_nisibis:'eph'};
// …
var abbr = CORPUS_ABBR[cid] || cid;
html += `<span class="cbadge ${abbr}">${corpusLabels[cid]||cid}: ${att[cid]}×</span>`;
```

Apply the same pattern at all three badge-generation sites (~lines 297, 797, 930). Also remove any remaining `.corpus-badge` CSS from style.css if found (the old CSS is replaced, so nothing to remove).

- [ ] **Step 3: Commit**

```bash
git add static/js/global.js
git commit -m "fix: align dark-mode key and corpus badge classes with new design"
```

---

## Task 4: Rewrite templates/base.html

**Files:**
- Replace: `templates/base.html`

The new base.html provides the `<div class="app">` grid shell. The old horizontal `<nav>` is removed entirely. Settings, language, bookmarks, share, and tour move into sidebar-accessible controls — during this transition they live in topbar icon buttons. Modals (share, cite, verse) are kept verbatim. `global.js` and all other scripts are kept.

The new base.html structure:
```
<html lang="{{ lang }}" dir="…">
<head>  fonts + style.css + driver.css + GA </head>
<body>
  <div class="app">
    <aside class="side" data-page="{{ page_id|default('search') }}"></aside>
    <div class="main">
      <header class="topbar">
        {% block topbar %}
        <div class="crumb">…default breadcrumb…</div>
        <div class="quick-search">…</div>
        <div class="topbar-tools">
          {# settings, lang, bookmarks, tour, share buttons #}
        </div>
        {% endblock %}
      </header>
      <main class="content">
        {% block content %}{% endblock %}
      </main>
      <footer class="foot">…</footer>
    </div>
  </div>
  {# share modal #}
  {# cite modal #}
  {# verse modal #}
  <script>…TOUR_I18N…</script>
  <script src="qrcodejs"></script>
  <script src="/static/js/global.js"></script>
  <script src="/static/app.js"></script>
  {% block scripts %}{% endblock %}
</body>
```

- [ ] **Step 1: Write the new base.html**

Write `templates/base.html` with the following complete content (replace the entire file):

```html
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ 'rtl' if lang in ('he', 'ar') else 'ltr' }}" {% if page_id is defined %}data-pageid="{{ page_id }}"{% endif %}>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Aramaic Root Atlas{% endblock %}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,300;0,400;0,500;0,600;1,400;1,500&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Noto+Sans+Syriac:wght@400;500&family=Noto+Serif+Hebrew:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/driver.js@1/dist/driver.css">
    <link rel="icon" type="image/svg+xml" href="{{ url_for('static', filename='favicon.svg') }}">
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XWZC618EC4"></script>
    <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-XWZC618EC4');</script>
    {% block head %}{% endblock %}
</head>
<body>

<div class="app">
  <aside class="side" data-page="{{ page_id|default('search') }}"></aside>

  <div class="main">
    <header class="topbar">
      {% block topbar %}
      <div class="crumb">
        <a href="/?lang={{ lang }}">Search</a>
      </div>
      <div class="quick-search">
        <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><path d="M21 21l-5-5"/></svg>
        <input placeholder="Quick lookup — root, gloss, reference"><span class="kbd">⌘K</span>
      </div>
      {% endblock %}
      <div class="topbar-tools">
        <!-- Language -->
        <div class="lang-wrapper">
          <button class="nav-btn lang-toggle" id="lang-toggle" aria-label="Language" aria-haspopup="true" aria-expanded="false">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="M2 12h20M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20"/></svg>
          </button>
          <div class="lang-dropdown" id="lang-dropdown" role="menu">
            <a class="lang-option{% if lang == 'en' %} active{% endif %}" role="menuitem" data-lang="en">English</a>
            <a class="lang-option{% if lang == 'es' %} active{% endif %}" role="menuitem" data-lang="es">Español</a>
            <a class="lang-option{% if lang == 'he' %} active{% endif %}" role="menuitem" data-lang="he">עברית</a>
            <a class="lang-option{% if lang == 'ar' %} active{% endif %}" role="menuitem" data-lang="ar">العربية</a>
          </div>
        </div>
        <!-- Settings -->
        <div class="settings-wrapper">
          <button class="nav-btn settings-toggle" id="settings-toggle" aria-label="Settings" aria-haspopup="true" aria-expanded="false">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 00-.1-1.2l2-1.6-2-3.4-2.4.8a7 7 0 00-2-1.2L14 3h-4l-.5 2.4a7 7 0 00-2 1.2L5 5.8l-2 3.4 2 1.6a7 7 0 000 2.4l-2 1.6 2 3.4 2.4-.8a7 7 0 002 1.2L10 21h4l.5-2.4a7 7 0 002-1.2l2.4.8 2-3.4-2-1.6c.1-.4.1-.8.1-1.2z"/></svg>
          </button>
          <div class="settings-dropdown" id="settings-dropdown" role="menu">
            <div class="settings-label">{{ t('settings_script', lang) if t else 'Transliteration' }}</div>
            <button class="settings-option{% if script == 'latin' %} active{% endif %}" data-script="latin" role="menuitemradio">Latin (ABC)</button>
            <button class="settings-option{% if script == 'syriac' %} active{% endif %}" data-script="syriac" role="menuitemradio">Syriac (ʾbg)</button>
            <button class="settings-option{% if script == 'hebrew' %} active{% endif %}" data-script="hebrew" role="menuitemradio">Hebrew (אבג)</button>
            <div class="settings-divider"></div>
            <div class="settings-label">{{ t('settings_translation', lang) if t else 'Translation' }}</div>
            <button class="settings-option{% if trans == 'en' %} active{% endif %}" data-trans="en" role="menuitemradio">English</button>
            <button class="settings-option{% if trans == 'es' %} active{% endif %}" data-trans="es" role="menuitemradio">Español</button>
            <button class="settings-option{% if trans == 'he' %} active{% endif %}" data-trans="he" role="menuitemradio">עברית</button>
            <button class="settings-option{% if trans == 'ar' %} active{% endif %}" data-trans="ar" role="menuitemradio">العربية</button>
            <button class="settings-option{% if trans == 'el' %} active{% endif %}" data-trans="el" role="menuitemradio">Greek (SBLGNT)</button>
            <div class="settings-divider"></div>
            <div class="settings-label">{{ t('settings_syriac_font', lang) if t else 'Script style' }}</div>
            <button class="settings-option syriac-font-option" data-syriac-font="estrangela" role="menuitemradio">Estrangela</button>
            <button class="settings-option syriac-font-option" data-syriac-font="eastern" role="menuitemradio">Eastern (Madnḥāyā)</button>
            <button class="settings-option syriac-font-option" data-syriac-font="western" role="menuitemradio">Western (Serṭo)</button>
          </div>
        </div>
        <!-- Share -->
        <button class="nav-btn share-toggle" id="share-toggle" aria-label="Share">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98M21 5a3 3 0 11-6 0 3 3 0 016 0zM9 12a3 3 0 11-6 0 3 3 0 016 0zM21 19a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
        </button>
        <!-- Tour -->
        <button class="nav-btn" id="tour-nav-btn" aria-label="Guided Tour">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 015 0c0 2-2.5 2-2.5 4M12 17v.01"/></svg>
        </button>
      </div>
    </header>

    <main class="content">
      {% block content %}{% endblock %}
    </main>

    <footer class="foot">
      <div class="foot-inner">
        <div>Aramaic Root Atlas · By <a href="https://jossifresco.com" target="_blank" rel="noopener">Jossi Fresco</a> · <a href="https://github.com/Jossifresben/aramaic-root-atlas" target="_blank" rel="noopener">GitHub</a> · Apache 2.0</div>
        <div class="foot-meta">
          <span>ORCID 0009-0000-2026-0836</span>
          <span>DOI 10.5281/zenodo.19358625</span>
        </div>
      </div>
    </footer>
  </div>{# /main #}
</div>{# /app #}

<!-- Share Modal -->
<div id="share-modal" class="modal-overlay" role="dialog" aria-modal="true" aria-label="Share">
  <div class="modal-content share-modal-content">
    <button class="modal-close" id="share-close" aria-label="Close">&times;</button>
    <h3 class="share-modal-title">{{ t('share_title', lang) if t else 'Share this page' }}</h3>
    <div class="share-qr-wrap"><div id="share-qr"></div><p class="share-qr-hint">Scan with your device</p></div>
    <div class="share-url-wrap">
      <input type="text" id="share-url" class="share-url-input" readonly aria-label="URL">
      <button id="share-copy-btn" class="share-copy-btn" title="Copy">&#10697;</button>
    </div>
  </div>
</div>

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
    <div id="cite-panel-bibtex" class="cite-panel active" role="tabpanel"><pre id="cite-text-bibtex" class="cite-code"></pre></div>
    <div id="cite-panel-chicago" class="cite-panel" role="tabpanel"><pre id="cite-text-chicago" class="cite-code"></pre></div>
    <div id="cite-panel-mla" class="cite-panel" role="tabpanel"><pre id="cite-text-mla" class="cite-code"></pre></div>
    <div id="cite-panel-apa" class="cite-panel" role="tabpanel"><pre id="cite-text-apa" class="cite-code"></pre></div>
    <div id="cite-panel-sbl" class="cite-panel" role="tabpanel"><pre id="cite-text-sbl" class="cite-code"></pre></div>
    <div class="cite-footer">
      <button class="cite-copy-btn" id="cite-copy-btn" onclick="copyCiteText()">&#10697; Copy</button>
      <a class="cite-doi-link" href="https://doi.org/10.5281/zenodo.19358625" target="_blank" rel="noopener">DOI: 10.5281/zenodo.19358625</a>
    </div>
    <div class="cite-orcid">ORCID: 0009-0000-2026-0836</div>
  </div>
</div>

<!-- Verse Modal -->
<div id="verse-modal" class="modal-overlay" onclick="if(event.target===this)this.classList.remove('active')">
  <div class="modal-content verse-modal-content" onclick="event.stopPropagation()">
    <div class="modal-sticky-header">
      <button class="modal-close" onclick="document.getElementById('verse-modal').classList.remove('active')">&times;</button>
      <button class="modal-copy" id="verse-copy-btn" onclick="copyVerseModal()" title="Copy">&#10697;</button>
      <div class="modal-ref" id="modal-ref"></div>
    </div>
    <button class="modal-nav-arrow" id="nav-prev" onclick="navigateVerse(-1)" disabled>&#9650;</button>
    <div id="modal-verses-container"></div>
    <button class="modal-nav-arrow" id="nav-next" onclick="navigateVerse(1)" disabled>&#9660;</button>
    <div class="modal-loading" id="modal-loading">Loading…</div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
<script>
window.TOUR_I18N = {
    next:                  "{{ t('tour_next',              lang)|e if t else 'Next' }}",
    skip:                  "{{ t('tour_skip',              lang)|e if t else 'Skip' }}",
    finish:                "{{ t('tour_finish',            lang)|e if t else 'Finish' }}",
    welcome_title:         "{{ t('tour_welcome_title',     lang)|e if t else 'Welcome' }}",
    welcome_body:          "{{ t('tour_welcome_body',      lang)|e if t else '' }}",
    nav_browse_title:      "{{ t('tour_nav_browse_title',  lang)|e if t else 'Browse' }}",
    nav_browse_body:       "{{ t('tour_nav_browse_body',   lang)|e if t else '' }}",
    nav_explore_title:     "{{ t('tour_nav_explore_title', lang)|e if t else 'Explore' }}",
    nav_explore_body:      "{{ t('tour_nav_explore_body',  lang)|e if t else '' }}",
    nav_research_title:    "{{ t('tour_nav_research_title',lang)|e if t else 'Research' }}",
    nav_research_body:     "{{ t('tour_nav_research_body', lang)|e if t else '' }}",
    search_title:          "{{ t('tour_search_title',      lang)|e if t else 'Search' }}",
    search_body:           "{{ t('tour_search_body',       lang)|e if t else '' }}",
    end_title:             "{{ t('tour_end_title',         lang)|e if t else 'Done' }}",
    end_body:              "{{ t('tour_end_body',          lang)|e if t else '' }}"
};
window.TOUR_IS_RTL = {{ 'true' if lang in ('he', 'ar') else 'false' }};
</script>
<script src="{{ url_for('static', filename='js/global.js') }}"></script>
<script src="{{ url_for('static', filename='app.js') }}"></script>
<script src="{{ url_for('static', filename='cite-modal.js') }}"></script>
{% block scripts %}{% endblock %}
</body>
</html>
```

- [ ] **Step 2: Spot-check after saving**

Open the Flask dev server: `python3 app.py`
Visit `http://localhost:5001/` — confirm:
- Sidebar renders with brand mark "ܐ" and nav groups
- Dark mode toggle in sidebar footer works (Light/Dark/Auto)
- No console errors about missing CSS classes
- Share and settings buttons in topbar are visible

- [ ] **Step 3: Commit**

```bash
git add templates/base.html
git commit -m "feat: migrate base.html to new sidebar app shell"
```

---

## Task 5: Port templates/index.html

**Files:**
- Rewrite: `templates/index.html`

Port the homepage from the Designer's `index.html`. Preserve all Jinja2 data (corpus stats from `{{ stats }}`), all existing JS functions (autocomplete, switchSearchTab, fillExample). Replace markup with new design classes.

- [ ] **Step 1: Understand the existing template's data bindings**

Read `templates/index.html` in the worktree. Note:
- `{{ stats }}` or `{% for corpus in stats %}` — corpus statistics
- JS search functions on `window`
- Autocomplete on root input

The new homepage has:
1. Eyebrow + `h1.display` hero
2. `.search-card` with 5 `.s-tab`/`.s-panel` (root, cognate, meaning, co-occurrence, full text)
3. `.corpora-grid` — 5 `.corpus-cell.pnt/pot/bib/tar/eph` cells with live stats
4. `.quick-list` — 6 tool links

- [ ] **Step 2: Rewrite templates/index.html**

Extend `base.html`, set `page_id='search'`. In `{% block topbar %}`, show the search breadcrumb. In `{% block content %}`, write:

```html
{% extends "base.html" %}
{% set page_id = 'search' %}
{% block title %}Aramaic Root Atlas — Search{% endblock %}

{% block topbar %}
<div class="crumb"><b>Search</b><span class="sep">›</span><span>Trace a root across all corpora</span></div>
<div class="quick-search">
  <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><path d="M21 21l-5-5"/></svg>
  <input placeholder="Quick lookup — root, gloss, reference"><span class="kbd">⌘K</span>
</div>
{% endblock %}

{% block content %}
<div class="eyebrow">A research tool for Semitic philology</div>
<h1 class="display">Trace triliteral <em>roots</em> across two millennia of Aramaic literature.</h1>
<p class="lede">Search {{ stats.total_verses|default('38,062') }} verses across the Peshitta, Targum Onkelos, Biblical Aramaic, and Ephrem of Nisibis. <a href="/about">About this project →</a></p>

<section class="search-card">
  <div class="search-tabs">
    <button class="s-tab active" data-tab="root" onclick="switchSearchTab('root')"><span class="num">01</span>By root</button>
    <button class="s-tab" data-tab="cognate" onclick="switchSearchTab('cognate')"><span class="num">02</span>By cognate</button>
    <button class="s-tab" data-tab="meaning" onclick="switchSearchTab('meaning')"><span class="num">03</span>By meaning</button>
    <button class="s-tab" data-tab="prox" onclick="switchSearchTab('prox')"><span class="num">04</span>Co-occurrence</button>
    <button class="s-tab" data-tab="text" onclick="switchSearchTab('text')"><span class="num">05</span>Full text</button>
  </div>
  {# panel 01: root #}
  <div class="s-panel" data-panel="root">
    <div class="s-body">
      <div class="s-field"><label class="s-label">Triliteral root</label>
        <div class="autocomplete-wrap">
          <input class="s-input" id="root-search-input" placeholder="K-TH-B,  SH-L-M,  Q-D-SH" autofocus>
        </div>
      </div>
      <div class="s-field"><label class="s-label">Corpus</label>
        <select class="s-select" id="root-corpus-select">
          <option value="">All corpora</option>
          <option value="peshitta_nt">Peshitta NT</option>
          <option value="peshitta_ot">Peshitta OT</option>
          <option value="biblical_aramaic">Biblical Aramaic</option>
          <option value="targum_onkelos">Targum Onkelos</option>
          <option value="ephrem_nisibis">Ephrem — Nisibis</option>
        </select>
      </div>
      <button class="btn" id="root-search-btn">Analyse
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor"><path d="M3 8h10M9 4l4 4-4 4"/></svg>
      </button>
    </div>
    <div class="s-foot">
      <div class="examples"><span class="ex-label">Try:</span>
        <button class="ex" onclick="fillExample('K-TH-B')">K-TH-B</button>
        <button class="ex" onclick="fillExample('SH-L-M')">SH-L-M</button>
        <button class="ex" onclick="fillExample('Q-D-SH')">Q-D-SH</button>
        <button class="ex" onclick="fillExample('B-R-K')">B-R-K</button>
        <button class="ex" onclick="fillExample('R-KH-M')">R-KH-M</button>
      </div>
      <button class="help" onclick="toggleTranslit()">Transliteration table</button>
    </div>
    <div id="translit-help" class="translit-help hidden">
      {# keep existing transliteration table cells verbatim #}
    </div>
  </div>
  {# panels 02-05: keep existing search panel markup, replace class names #}
  {# cognate, meaning, prox, text panels — copy from existing index.html
     replacing .search-input→.s-input, .search-select→.s-select, etc. #}
</section>

<h2 class="section" style="margin-top:64px">Indexed corpora</h2>
<div class="corpora-grid">
  {% for c in [
    {'id':'pnt','name':'Peshitta NT','corpus_key':'peshitta_nt','period':'~ 2nd–5th c. CE · Classical Syriac'},
    {'id':'pot','name':'Peshitta OT','corpus_key':'peshitta_ot','period':'~ 2nd–5th c. CE · Classical Syriac'},
    {'id':'bib','name':'Biblical Aramaic','corpus_key':'biblical_aramaic','period':'~ 6th–2nd c. BCE · Imperial'},
    {'id':'tar','name':'Targum Onkelos','corpus_key':'targum_onkelos','period':'~ 1st–3rd c. CE · Jewish Aramaic'},
    {'id':'eph','name':'Ephrem — Nisibis','corpus_key':'ephrem_nisibis','period':'~ 350–363 CE · Patristic Syriac'},
  ] %}
  {% set s = stats.by_corpus[c.corpus_key] if stats and stats.by_corpus else {} %}
  <div class="corpus-cell {{ c.id }}">
    <div class="nm">{{ c.name }}</div>
    <div class="verses">{{ s.verse_count|default('-') }}<small>verses</small></div>
    <div class="words">{{ s.word_count|default('-') }} words · {{ s.root_count|default('-') }} roots</div>
    <div class="period">{{ c.period }}</div>
  </div>
  {% endfor %}
</div>

<h2 class="section" style="margin-top:64px">Continue your work</h2>
<div class="quick-list">
  <a href="/read/Matthew/1"><div class="ql-num">01</div><div><div class="ql-name">Open the reader</div><div class="ql-desc">Verse-by-verse Syriac with transliteration, gloss, and translation.</div></div><div class="ql-arr">→</div></a>
  <a href="/diachronic"><div class="ql-num">02</div><div><div class="ql-name">Diachronic frequency</div><div class="ql-desc">Plot a root's distribution across periods and corpora.</div></div><div class="ql-arr">→</div></a>
  <a href="/interlinear"><div class="ql-num">03</div><div><div class="ql-name">Interlinear word study</div><div class="ql-desc">Word-by-word alignment with root, stem, and morphological gloss.</div></div><div class="ql-arr">→</div></a>
  <a href="/concordance"><div class="ql-num">04</div><div><div class="ql-name">Concordance with KWIC</div><div class="ql-desc">Keyword-in-context across all 38,062 verses, sortable by context.</div></div><div class="ql-arr">→</div></a>
  <a href="/browse"><div class="ql-num">05</div><div><div class="ql-name">Browse 66 books</div><div class="ql-desc">Direct chapter access across all five corpora.</div></div><div class="ql-arr">→</div></a>
  <a href="/hapax"><div class="ql-num">06</div><div><div class="ql-name">Hapax &amp; rare forms</div><div class="ql-desc">Words attested only once or twice — useful for textual criticism.</div></div><div class="ql-arr">→</div></a>
</div>
{% endblock %}

{% block scripts %}
<script>
  // Wire root search form (preserve existing search logic from old index.html)
  // Paste the existing search JS from the old template's {% block scripts %} here
</script>
{% endblock %}
```

**Important:** The `{% block scripts %}` must contain the existing JS from the old template that wires up autocomplete, the Analyse button click handler, and the KWIC inline results. Read the old `templates/index.html`'s `<script>` block and paste it verbatim into `{% block scripts %}`.

- [ ] **Step 3: Add page_id to Flask render_template**

In `app.py`, find the `/` route's `render_template('index.html', ...)` call and add `page_id='search'`:
```python
return render_template('index.html', ..., page_id='search')
```

- [ ] **Step 4: Smoke test**

Visit `http://localhost:5001/` — confirm sidebar shows "Search" active, corpus ledger shows real numbers, search tabs switch, transliteration table toggles.

- [ ] **Step 5: Commit**

```bash
git add templates/index.html app.py
git commit -m "feat: port homepage to new design system"
```

---

## Task 6: Port templates/browse.html

**Files:**
- Rewrite: `templates/browse.html`

Port the browse page. The new design uses `.browse-grid` of `.book-card.pnt/pot/etc` with `.chapters` grid and `.ch.heat-1/2/3/4` chapter heat cells.

- [ ] **Step 1: Understand current browse.html structure**

Read `templates/browse.html` in the worktree. Note how books and chapters are rendered (Jinja2 for loops over `books` data), how heat values are calculated.

- [ ] **Step 2: Rewrite templates/browse.html**

```html
{% extends "base.html" %}
{% set page_id = 'browse' %}
{% block title %}Browse — Aramaic Root Atlas{% endblock %}

{% block topbar %}
<div class="crumb"><a href="/?lang={{ lang }}">Search</a><span class="sep">›</span><b>Browse corpora</b></div>
<div class="quick-search">
  <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><path d="M21 21l-5-5"/></svg>
  <input placeholder="Find a book or chapter"><span class="kbd">⌘K</span>
</div>
{% endblock %}

{% block content %}
<div class="page-head">
  <div>
    <h1 class="ph-title">Browse <em>corpora</em></h1>
    <p class="ph-sub">Direct chapter access across all five corpora. Each cell is heat-mapped by total indexed root forms.</p>
  </div>
</div>

<div class="filter-row" style="border-top:0">
  <span class="fl">Filter</span>
  <button class="chip on" data-c="pnt" onclick="toggleChip(this)">Peshitta NT</button>
  <button class="chip on" data-c="pot" onclick="toggleChip(this)">Peshitta OT</button>
  <button class="chip on" data-c="bib" onclick="toggleChip(this)">Biblical Aramaic</button>
  <button class="chip on" data-c="tar" onclick="toggleChip(this)">Targum Onkelos</button>
  <button class="chip on" data-c="eph" onclick="toggleChip(this)">Ephrem</button>
</div>

{% for corpus_group in corpus_groups %}
<h2 class="section" style="margin-top:{{ '32px' if loop.first else '48px' }}">{{ corpus_group.label }}</h2>
<div class="browse-grid">
  {% for book in corpus_group.books %}
  {% set abbr = {'peshitta_nt':'pnt','peshitta_ot':'pot','biblical_aramaic':'bib','targum_onkelos':'tar','ephrem_nisibis':'eph'}[book.corpus_id] %}
  <div class="book-card {{ abbr }}">
    <div class="b-name">{{ book.name }}</div>
    <div class="b-meta"><span class="cbadge {{ abbr }}">{{ abbr|upper }}</span>{{ book.chapter_count }} chapters · {{ book.word_count|default('') }} words</div>
    <div class="chapters">
      {% for ch in book.chapters %}
      {% set heat = 'heat-'+ch.heat_level|string if ch.heat_level else '' %}
      <a class="ch {{ heat }}" href="/read/{{ book.name }}/{{ ch.num }}?lang={{ lang }}">{{ ch.num }}</a>
      {% endfor %}
    </div>
  </div>
  {% endfor %}
</div>
{% endfor %}
{% endblock %}
```

**Note:** The existing browse.html passes `books` grouped by corpus from `app.py`. Read the existing template to understand the exact variable structure (`books`, `corpus_id`, `chapter_count`, `chapters[].heat_level`), then adapt the Jinja2 loops above to match. The logic itself doesn't change, only the CSS classes.

- [ ] **Step 3: Update app.py browse route**

Add `page_id='browse'` to `render_template('browse.html', ...)`.

- [ ] **Step 4: Smoke test**

Visit `http://localhost:5001/browse` — book cards show with corpus color strip, chapters are heat-mapped.

- [ ] **Step 5: Commit**

```bash
git add templates/browse.html app.py
git commit -m "feat: port browse page to new design"
```

---

## Task 7: Port templates/read.html

**Files:**
- Rewrite: `templates/read.html`

The new reader uses `.verse { grid-template-columns: 60px 1fr 60px }` with `.v-syr`, `.v-tr`, `.v-en` stacked in the middle cell. The `.reader-bar` holds chip toggles. Root words use `<span class="root">` (same as existing). The existing word-popover JS, chapter-root-panel JS, and bookmark JS are preserved unchanged in `{% block scripts %}`.

- [ ] **Step 1: Read existing read.html to extract JS block and data bindings**

Note the Jinja2 variables: `book`, `chapter`, `verses`, `trans`, `script`, etc. Note the JS that renders word popovers.

- [ ] **Step 2: Rewrite templates/read.html**

```html
{% extends "base.html" %}
{% set page_id = 'reader' %}
{% block title %}{{ book }} {{ chapter }} — Aramaic Root Atlas{% endblock %}

{% block topbar %}
<div class="crumb">
  <a href="/?lang={{ lang }}">Search</a><span class="sep">›</span>
  <a href="/browse?lang={{ lang }}">Browse</a><span class="sep">›</span>
  <b>{{ book }} {{ chapter }}</b>
</div>
<div class="quick-search">
  <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><path d="M21 21l-5-5"/></svg>
  <input placeholder="Quick lookup"><span class="kbd">⌘K</span>
</div>
{% endblock %}

{% block content %}
<div class="page-head">
  <div>
    <h1 class="ph-title">{{ book }} · <em>Chapter {{ chapter }}</em></h1>
    <div class="ph-sub" style="display:flex;align-items:center;gap:10px;margin-top:8px">
      <span class="cbadge {{ corpus_abbr }}">{{ corpus_label }}</span>
      <span>{{ verse_count }} verses</span>
    </div>
  </div>
  <div class="ph-actions">
    {% if chapter > 1 %}<a href="/read/{{ book }}/{{ chapter - 1 }}?lang={{ lang }}" class="btn secondary">‹ Ch {{ chapter - 1 }}</a>{% endif %}
    <a href="/browse?lang={{ lang }}" class="btn secondary">All books</a>
    <a href="/read/{{ book }}/{{ chapter + 1 }}?lang={{ lang }}" class="btn secondary">Ch {{ chapter + 1 }} ›</a>
  </div>
</div>

<div class="reader-bar">
  <span style="font-family:var(--sans);font-size:11px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-3)">Show</span>
  <button class="chip on" id="chip-syr" onclick="toggleChip(this);toggleLayer('syr')">Syriac</button>
  <button class="chip on" id="chip-tr" onclick="toggleChip(this);toggleLayer('tr')">Translit.</button>
  <button class="chip on" id="chip-en" onclick="toggleChip(this);toggleLayer('en')">Translation</button>
  <button class="chip" id="chip-roots" onclick="toggleChip(this);toggleRoots()">Roots</button>
  <span class="spacer"></span>
  <button class="btn secondary" onclick="openCiteModal({tool:'reader',book:'{{ book }}',chapter:'{{ chapter }}'})">Cite</button>
</div>

{% for verse in verses %}
<div class="verse" data-ref="{{ book }} {{ chapter }}:{{ verse.num }}">
  <div class="v-num">{{ verse.num }}</div>
  <div>
    <div class="v-syr layer-syr" dir="rtl">{{ verse.syriac_html|safe }}</div>
    <div class="v-tr layer-tr">{{ verse.translit }}</div>
    <div class="v-en layer-en">{{ verse.translation }}</div>
  </div>
  <div class="v-actions">
    <button title="Bookmark" onclick="toggleVerseBookmark('{{ book }} {{ chapter }}:{{ verse.num }}')">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg>
    </button>
    <button title="Roots" onclick="showVerseRoots('{{ book }} {{ chapter }}:{{ verse.num }}')">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 2v20M5 9l7-7 7 7M5 15l7 7 7-7"/></svg>
    </button>
    <button title="Note" onclick="addVerseNote('{{ book }} {{ chapter }}:{{ verse.num }}')">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M11 4H4v16h16v-7M18.5 2.5a2.12 2.12 0 113 3L12 15l-4 1 1-4z"/></svg>
    </button>
  </div>
</div>
{% endfor %}

<!-- Word popover (injected by JS) -->
<div id="word-pop" class="word-pop" style="display:none"></div>

<!-- Chapter root summary -->
<div class="chapter-root-panel" id="chapter-root-panel" style="display:none">
  <h3>Roots in this chapter</h3>
  <div id="chapter-root-content"></div>
</div>
{% endblock %}

{% block scripts %}
{# Paste the existing read.html {% block scripts %} JS verbatim here.
   It handles: word click → popover, toggleLayer(), toggleRoots(),
   chapter-root fetch and render, bookmark toggle. #}
{% endblock %}
```

**Critical:** `verse.syriac_html` must include the root `<span class="root">` markup already present in the existing reader (the existing code wraps root words in `<span class="root" data-root="…">`). This class name stays the same — `.verse .v-syr .root` is defined in the new CSS.

- [ ] **Step 3: Update app.py read route**

Add `page_id='reader'` and compute `corpus_abbr`, `corpus_label`, `verse_count` if not already available.

- [ ] **Step 4: Smoke test**

Visit `http://localhost:5001/read/Matthew/4` — verses render in grid, Syriac text is large and RTL, chip toggles show/hide layers, root words have dotted underlines.

- [ ] **Step 5: Commit**

```bash
git add templates/read.html app.py
git commit -m "feat: port reader to new verse grid design"
```

---

## Task 8: Port templates/concordance.html

**Files:**
- Rewrite: `templates/concordance.html`

The new concordance layout uses `.entry-grid { grid-template-columns: 1fr 280px }` — main content on left, apparatus (cognates, distribution, lexicon) on right. The entry head shows the large glyph + transliteration + Hebrew. The `.kwic-table` replaces the old concordance table.

- [ ] **Step 1: Read existing concordance.html JS block**

The existing template has significant JS for fetching concordance data, rendering rows, handling export. This all goes into `{% block scripts %}` unchanged.

- [ ] **Step 2: Rewrite templates/concordance.html**

```html
{% extends "base.html" %}
{% set page_id = 'concordance' %}
{% block title %}Concordance — Aramaic Root Atlas{% endblock %}

{% block topbar %}
<div class="crumb"><a href="/?lang={{ lang }}">Search</a><span class="sep">›</span><b id="crumb-root">Concordance</b></div>
<div class="quick-search">
  <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><path d="M21 21l-5-5"/></svg>
  <input id="quick-root-input" placeholder="Root — K-TH-B"><span class="kbd">⌘K</span>
</div>
<div class="topbar-tools" style="display:inherit">
  <button class="tb" title="Cite" onclick="openCiteModal(getCiteContext())">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 8c0-2 1-4 4-4M9 8c0-2 1-4 4-4M3 8v3c0 2 1 3 3 3M9 8v3c0 2 1 3 3 3"/></svg>
  </button>
  <button class="tb" title="Export" onclick="exportConcordance()">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 3v12M7 10l5 5 5-5M5 21h14"/></svg>
  </button>
</div>
{% endblock %}

{% block content %}
<div class="entry-grid">
  <div>
    <!-- Entry head (populated by JS after root loads) -->
    <div class="entry-head" id="entry-head" style="display:none">
      <div class="glyphs">
        <div class="glyph-syr" id="glyph-syr"></div>
        <div>
          <div class="glyph-translit" id="glyph-translit"></div>
          <div class="glyph-heb" id="glyph-heb"></div>
        </div>
      </div>
      <div class="entry-meta" id="entry-meta"></div>
    </div>
    <p class="gloss" id="root-gloss" style="display:none"></p>

    <!-- Stat strip -->
    <div class="entry-stats" id="entry-stats" style="display:none">
      <div class="estat"><div class="estat-num" id="stat-total">—</div><div class="estat-label">Attestations</div></div>
      <div class="estat"><div class="estat-num" id="stat-forms">—</div><div class="estat-label">Distinct forms</div></div>
      <div class="estat"><div class="estat-num" id="stat-corpora">—</div><div class="estat-label">Corpora</div></div>
      <div class="estat"><div class="estat-num" id="stat-rate">—</div><div class="estat-label">Per 1k words</div></div>
    </div>

    <!-- Sub-nav tabs -->
    <div class="subnav" id="conc-subnav" style="display:none">
      <button class="tab active" onclick="switchConcordanceTab('concordance')"><span class="ec">A</span>Concordance <span class="ec" id="tab-count-conc"></span></button>
      <button class="tab" onclick="switchConcordanceTab('forms')"><span class="ec">B</span>Forms <span class="ec" id="tab-count-forms"></span></button>
      <button class="tab" onclick="switchConcordanceTab('cognates')"><span class="ec">C</span>Cognates</button>
    </div>

    <!-- Filters -->
    <div class="filter-row" id="conc-filters" style="display:none">
      <span class="fl">Corpora</span>
      <button class="chip on" data-c="pnt" onclick="toggleChip(this);reloadConc()">Peshitta NT</button>
      <button class="chip on" data-c="pot" onclick="toggleChip(this);reloadConc()">Peshitta OT</button>
      <button class="chip on" data-c="bib" onclick="toggleChip(this);reloadConc()">Biblical Aramaic</button>
      <button class="chip on" data-c="tar" onclick="toggleChip(this);reloadConc()">Targum Onkelos</button>
      <button class="chip on" data-c="eph" onclick="toggleChip(this);reloadConc()">Ephrem</button>
      <span style="margin-left:auto;font-family:var(--mono);font-size:11.5px;color:var(--ink-3)">
        Sort: <a href="#" onclick="sortConc('ref')">Reference</a> ·
        <a href="#" onclick="sortConc('left')">Left</a> ·
        <a href="#" onclick="sortConc('right')">Right</a>
      </span>
    </div>

    <!-- KWIC table -->
    <table class="kwic-table" id="kwic-table" style="margin-top:8px">
      <tbody id="kwic-tbody"></tbody>
    </table>
    <div id="conc-pagination" style="display:flex;justify-content:space-between;align-items:center;padding:18px 0;font-family:var(--sans);font-size:12.5px;color:var(--ink-3)"></div>

    <!-- Empty / loading states -->
    <div id="conc-empty" style="font-family:var(--serif);font-style:italic;color:var(--ink-3);padding:48px 0;text-align:center">Enter a root above to begin</div>
  </div>

  <!-- Right rail: apparatus -->
  <aside id="conc-apparatus" style="position:sticky;top:80px;font-size:13px;display:none">
    <div style="padding-bottom:24px;margin-bottom:24px;border-bottom:1px solid var(--rule)">
      <div style="font-size:11px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3);margin-bottom:14px;font-family:var(--sans)">Cognates</div>
      <div id="apparatus-cognates" style="display:grid;grid-template-columns:auto 1fr;gap:12px 14px;align-items:baseline;font-family:var(--sans)"></div>
    </div>
    <div style="padding-bottom:24px;margin-bottom:24px;border-bottom:1px solid var(--rule)">
      <div style="font-size:11px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3);margin-bottom:14px;font-family:var(--sans)">Distribution</div>
      <div id="apparatus-distribution"></div>
    </div>
  </aside>
</div>
{% endblock %}

{% block scripts %}
{# Paste the existing concordance.html JS block verbatim here.
   Update class names used by JS:
   - '.corpus-badge.corpus-peshitta_nt' → '.cbadge.pnt' (etc.)
   - Any old color vars → new design vars #}
{# Add getCiteContext() for the topbar Cite button #}
<script>
function getCiteContext(){
  return {tool:'concordance', root: currentRoot, url: location.href};
}
</script>
{% endblock %}
```

- [ ] **Step 3: Update app.py concordance route**

Add `page_id='concordance'`.

- [ ] **Step 4: Smoke test**

Visit `http://localhost:5001/concordance?root=K-TH-B` — entry head appears, KWIC table populates, right rail shows cognates and distribution bars.

- [ ] **Step 5: Commit**

```bash
git add templates/concordance.html app.py
git commit -m "feat: port concordance to new entry-grid design"
```

---

## Task 9: Port templates/diachronic.html

**Files:**
- Rewrite: `templates/diachronic.html`

The new diachronic page uses the `.entry-head` + `.glyphs` header, `.subnav` tabs (Root view / Frequency shifts / Hapax timeline / Compare two roots), `.dia-row` + `.dia-bar` for the frequency chart, `.dtable` for the attestation detail table, and `.timeline` for the period histogram.

- [ ] **Step 1: Rewrite templates/diachronic.html**

```html
{% extends "base.html" %}
{% set page_id = 'diachronic' %}
{% block title %}Diachronic — Aramaic Root Atlas{% endblock %}

{% block topbar %}
<div class="crumb"><a href="/?lang={{ lang }}">Search</a><span class="sep">›</span><b id="diac-crumb">Diachronic</b></div>
<div class="quick-search">
  <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><path d="M21 21l-5-5"/></svg>
  <input id="diac-root-input" placeholder="Root — SH-L-M"><span class="kbd">⌘K</span>
</div>
{% endblock %}

{% block content %}
<div class="page-head">
  <div>
    <h1 class="ph-title"><em>Diachronic</em> analysis</h1>
    <p class="ph-sub">Trace a root's distribution across periods and corpora. Frequencies normalised per 1,000 words.</p>
  </div>
  <div class="ph-actions">
    <button class="btn secondary" onclick="openCiteModal(getCiteContext())">Cite</button>
    <button class="btn secondary" onclick="exportDiachronicCSV()">Export CSV</button>
  </div>
</div>

<!-- Sub-view tabs -->
<div class="subnav" style="margin:0 0 24px" data-tabs="diac">
  <button class="tab active" data-tab="root" onclick="switchTab('diac','root')"><span class="ec">A</span>Root view</button>
  <button class="tab" data-tab="shifts" onclick="switchTab('diac','shifts')"><span class="ec">B</span>Frequency shifts</button>
  <button class="tab" data-tab="hapax" onclick="switchTab('diac','hapax')"><span class="ec">C</span>Hapax timeline</button>
  <button class="tab" data-tab="compare" onclick="switchTab('diac','compare')"><span class="ec">D</span>Compare two roots</button>
</div>

<!-- Root view pane -->
<div data-panes="diac">
<div class="pane" data-pane="root">
  <!-- Root input -->
  <div style="display:flex;gap:14px;align-items:end;padding:8px 0 28px">
    <div class="s-field" style="max-width:280px;flex:1">
      <label class="s-label">Triliteral root</label>
      <div class="autocomplete-wrap">
        <input class="s-input" id="diac-root-field" value="{{ root|default('') }}" placeholder="e.g. SH-L-M">
      </div>
    </div>
    <div class="s-field">
      <label class="s-label">Normalisation</label>
      <select class="s-select" id="diac-norm">
        <option value="per_1k">Per 1,000 words</option>
        <option value="raw">Raw count</option>
      </select>
    </div>
    <button class="btn" onclick="loadDiachronic()">Analyse</button>
  </div>

  <!-- Entry head (shown after load) -->
  <div class="entry-head" id="diac-entry-head" style="display:none;border-bottom-width:1px">
    <div class="glyphs">
      <div class="glyph-syr" id="diac-glyph-syr"></div>
      <div>
        <div class="glyph-translit" id="diac-glyph-translit"></div>
        <div class="glyph-heb" id="diac-glyph-heb" style="margin-top:4px"></div>
      </div>
    </div>
    <div class="entry-meta" id="diac-entry-meta"></div>
  </div>
  <p class="gloss" id="diac-gloss" style="display:none"></p>

  <!-- Distribution chart -->
  <h2 class="section" id="diac-dist-head" style="margin-top:36px;display:none">Distribution by corpus</h2>
  <div id="diac-dist-bars"></div>

  <!-- Detail table -->
  <h2 class="section" id="diac-table-head" style="margin-top:48px;display:none">Attestations &amp; representative forms</h2>
  <table class="dtable" id="diac-detail-table" style="display:none">
    <thead><tr>
      <th>Corpus</th><th>Period</th>
      <th class="num">Occurrences</th><th class="num">Per 1k words</th>
      <th>Representative forms</th>
    </tr></thead>
    <tbody id="diac-detail-tbody"></tbody>
  </table>

  <!-- Timeline histogram -->
  <h2 class="section" id="diac-timeline-head" style="margin-top:48px;display:none">Frequency over time</h2>
  <div class="timeline" id="diac-timeline" style="display:none"></div>
</div>

<!-- Shifts pane -->
<div class="pane hidden" data-pane="shifts">
  <div style="padding:24px 0" id="shifts-content">
    <p style="font-family:var(--serif);font-style:italic;color:var(--ink-3)">Loading frequency shifts…</p>
  </div>
</div>

<!-- Hapax timeline pane -->
<div class="pane hidden" data-pane="hapax">
  <div style="padding:24px 0" id="hapax-timeline-content">
    <p style="font-family:var(--serif);font-style:italic;color:var(--ink-3)">Select a corpus to see hapax distribution.</p>
  </div>
</div>

<!-- Compare pane -->
<div class="pane hidden" data-pane="compare">
  <div style="display:flex;gap:14px;align-items:end;padding:24px 0">
    <div class="s-field"><label class="s-label">Root one</label><input class="s-input" id="compare-root-1" placeholder="SH-L-M"></div>
    <div class="s-field"><label class="s-label">Root two</label><input class="s-input" id="compare-root-2" placeholder="K-TH-B"></div>
    <button class="btn" onclick="loadCompare()">Compare</button>
  </div>
  <div id="compare-content"></div>
</div>
</div>{# /data-panes #}
{% endblock %}

{% block scripts %}
{# Paste the existing diachronic.html JS block verbatim here.
   Key functions to preserve: loadDiachronic(), renderDiaBars(), renderDiaTable(),
   renderTimeline(), loadShifts(), exportDiachronicCSV(), getCiteContext().
   Update corpus badge class generation to use .cbadge.pnt etc. #}
{% endblock %}
```

- [ ] **Step 2: Update app.py diachronic route**

Add `page_id='diachronic'`.

- [ ] **Step 3: Smoke test**

Visit `http://localhost:5001/diachronic?root=SH-L-M` — entry head shows, dia-rows render with coloured bars, detail table shows, timeline renders. Subnav tabs switch panes.

- [ ] **Step 4: Commit**

```bash
git add templates/diachronic.html app.py
git commit -m "feat: port diachronic to new entry-head + dia-row design"
```

---

## Task 10: Port templates/interlinear.html

**Files:**
- Rewrite: `templates/interlinear.html`

The new interlinear uses `.il-verse > .il-ref + .il-grid + .il-trans` layout. `.il-grid` is RTL flex-wrap. Each `.il-tok` has rows: `.syr`, `.tr`, `.gl`, `.root`, `.stem`. The chip filter row toggles visibility of these rows.

- [ ] **Step 1: Rewrite templates/interlinear.html**

```html
{% extends "base.html" %}
{% set page_id = 'interlinear' %}
{% block title %}Interlinear — Aramaic Root Atlas{% endblock %}

{% block topbar %}
<div class="crumb">
  <a href="/?lang={{ lang }}">Search</a><span class="sep">›</span>
  <b>Interlinear</b>
  {% if book %}<span class="sep">›</span><span>{{ book }} {{ chapter }}</span>{% endif %}
</div>
<div class="quick-search">
  <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><path d="M21 21l-5-5"/></svg>
  <input placeholder="Quick lookup"><span class="kbd">⌘K</span>
</div>
{% endblock %}

{% block content %}
<div class="page-head">
  <div>
    <h1 class="ph-title"><em>Interlinear</em> reader</h1>
    <p class="ph-sub">Word-by-word alignment with Syriac, transliteration, gloss, root, and stem. Click any token to open its root entry.</p>
  </div>
  <div class="ph-actions">
    <button class="btn secondary" onclick="exportIL('tei')">Export TEI</button>
    <button class="btn secondary" onclick="exportIL('txt')">Plain text</button>
    <button class="btn secondary" onclick="exportIL('csv')">CSV</button>
    <button class="btn secondary" onclick="openCiteModal(getCiteContext())">Cite</button>
  </div>
</div>

<!-- Controls -->
<div style="display:grid;grid-template-columns:repeat(5,1fr) auto;gap:18px;align-items:end;padding:8px 0 24px">
  <div class="s-field"><label class="s-label">Corpus</label>
    <select class="s-select" id="il-corpus">
      <option value="peshitta_nt">Peshitta NT</option>
      <option value="peshitta_ot">Peshitta OT</option>
      <option value="targum_onkelos">Targum Onkelos</option>
      <option value="ephrem_nisibis">Ephrem</option>
    </select>
  </div>
  <div class="s-field"><label class="s-label">Book</label><select class="s-select" id="il-book"></select></div>
  <div class="s-field"><label class="s-label">Chapter</label><select class="s-select" id="il-chapter"></select></div>
  <div class="s-field"><label class="s-label">Translit.</label>
    <select class="s-select" id="il-translit-script">
      <option value="latin">Latin</option>
      <option value="hebrew">Hebrew</option>
    </select>
  </div>
  <div class="s-field"><label class="s-label">Script</label>
    <select class="s-select" id="il-syr-font">
      <option value="estrangela">Estrangela</option>
      <option value="eastern">Madnḥāyā</option>
      <option value="western">Serṭō</option>
    </select>
  </div>
  <button class="btn" onclick="loadInterlinear()">Analyse</button>
</div>

<!-- Show layer chips -->
<div class="filter-row" style="border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)">
  <span class="fl">Show</span>
  <button class="chip on" onclick="toggleChip(this);toggleILLayer('syr')">Syriac</button>
  <button class="chip on" onclick="toggleChip(this);toggleILLayer('tr')">Translit.</button>
  <button class="chip on" onclick="toggleChip(this);toggleILLayer('gl')">Gloss</button>
  <button class="chip on" onclick="toggleChip(this);toggleILLayer('root')">Root</button>
  <button class="chip on" onclick="toggleChip(this);toggleILLayer('stem')">Stem</button>
  <button class="chip" onclick="toggleChip(this);toggleILLayer('il-trans')">Translation</button>
</div>

<!-- Verses container (populated by JS) -->
<div id="il-verses-container">
  <p style="font-family:var(--serif);font-style:italic;color:var(--ink-3);padding:48px 0;text-align:center">Select a corpus, book, and chapter above</p>
</div>
{% endblock %}

{% block scripts %}
{# Paste the existing interlinear.html JS verbatim.
   Key functions: loadInterlinear(), renderILVerse(verse), toggleILLayer(cls),
   exportIL(fmt), getCiteContext().
   
   renderILVerse() must generate:
   <section class="il-verse">
     <div class="il-ref">Book Ch : V</div>
     <div class="il-grid">
       <div class="il-tok">
         <div class="syr">…</div>
         <div class="tr">…</div>
         <div class="gl">…</div>
         <div class="root">…</div>
         <div class="stem [muted]">…</div>
       </div>…
     </div>
     <div class="il-trans">…</div>
   </section>
   #}
{% endblock %}
```

- [ ] **Step 2: Update app.py interlinear route**

Add `page_id='interlinear'`.

- [ ] **Step 3: Smoke test**

Visit `http://localhost:5001/interlinear` — controls render, selecting Mark ch 1 and clicking Analyse populates il-verse sections with il-tok tokens. Chip toggles hide/show rows. Syriac is RTL and large.

- [ ] **Step 4: Commit**

```bash
git add templates/interlinear.html app.py
git commit -m "feat: port interlinear to new il-tok grid design"
```

---

## Task 11: Extend shell to hapax.html

**Files:**
- Modify: `templates/hapax.html`

The hapax page keeps its existing JS and controls unchanged. Only the outer shell (nav→sidebar), page-head, and filter area receive new classes. The results table adopts `.dtable`.

- [ ] **Step 1: Update templates/hapax.html outer shell**

Change:
1. `{% extends "base.html" %}` — already inherits, just add `{% set page_id = 'hapax' %}`
2. `{% block topbar %}` — add crumb and quick-search
3. The old `<h1>` / intro text → wrap in `<div class="page-head">…</div>`
4. Replace old filter bar markup with `<div class="filter-row">` + `.chip` buttons
5. Replace old `<table class="hapax-table">` → `<table class="dtable">`
   - Old `<thead>` class names on `<th>` → remove, `dtable` styles them automatically
   - Add `.num` class to numeric columns
   - Add `.syr` class to Syriac text column
   - Add `.tr` class to transliteration column
   - Add `.gloss` class to gloss column
6. Export buttons → `<div class="ph-actions">` in page-head + keep `getCiteContext()` onclick

- [ ] **Step 2: Add page_id to app.py hapax route**

```python
return render_template('hapax.html', ..., page_id='hapax')
```

- [ ] **Step 3: Smoke test**

Visit `http://localhost:5001/hapax` — sidebar shows Hapax active. Frequency slider + corpus filter chips work. Table renders with proper typography.

- [ ] **Step 4: Commit**

```bash
git add templates/hapax.html app.py
git commit -m "feat: extend new shell to hapax page"
```

---

## Task 12: Extend shell to remaining pages (bulk)

**Files:**
- Modify: `templates/heatmap.html`, `templates/passage_profile.html`, `templates/collocations.html`, `templates/parallel.html`, `templates/visualize.html`, `templates/constellation.html`, `templates/bookmarks.html`, `templates/about.html`, `templates/annotations.html`, `templates/semantic_fields.html`, `templates/parse.html`

For each page, apply the same pattern as Task 11:

**Per-page recipe:**
1. Add `{% set page_id = '<id>' %}` at top (values below)
2. Add `{% block topbar %}` with crumb + quick-search
3. Wrap page title/description in `<div class="page-head"><div><h1 class="ph-title">…</h1><p class="ph-sub">…</p></div><div class="ph-actions">…export buttons…</div></div>`
4. Replace old filter bars with `.filter-row` + `.chip` pattern
5. Replace old table classes → `.dtable`
6. Replace any `.corpus-badge.corpus-*` in template HTML → `.cbadge.<abbr>`
7. Add `page_id` to `render_template()` call in app.py

**page_id values:**
- `heatmap.html` → `'heatmap'` (sidebar: ref group)
- `passage_profile.html` → `'search'` (no dedicated nav slot, Search stays active)
- `collocations.html` → `'search'`
- `parallel.html` → `'parallel'` (workspace group in sidebar)
- `visualize.html` → `'search'`
- `constellation.html` → `'search'`
- `bookmarks.html` → `'bookmarks'` (workspace group)
- `about.html` → `'about'` (ref group)
- `annotations.html` → `'search'`
- `semantic_fields.html` → `'search'`
- `parse.html` → `'search'`

**Additional per-page notes:**

**heatmap.html:** Wrap heatmap grid in `.pp-stats` for the summary row, use existing heatmap grid cells. No structural changes to the D3-free heatmap JS.

**passage_profile.html:** Use `.pp-stats` + `.pp-stat` for the stat cards. Use `.dtable` for the root frequency table.

**parallel.html:** Use `.parallel-cols.cols-2` or `.cols-3` container. Use `.parallel-col`, `.parallel-col-head`, `.parallel-verse`, `.parallel-syr`, `.parallel-trans` classes (defined in the legacy bridge CSS in Task 1).

**visualize.html / constellation.html:** Only the shell changes (sidebar + topbar). `#viz-container` and `#constellation-container` are sized in legacy bridge CSS. D3 code is unchanged.

**bookmarks.html:** Use `.bm-tabs` + `.bm-tab` for Verses/Roots tab bar. Use `.dtable` for bookmark list. Use `.bm-empty` for empty state.

**about.html:** Use `.about-section` wrapper per section. Use `.about-caveat` for methodology caveats. Standard `p`, `ul` tags — styled by new CSS.

- [ ] **Step 1: Apply the shell recipe to each page**

For each of the 11 pages, read the existing template, identify the title/controls/table, apply the recipe above. The existing JS in each `{% block scripts %}` is untouched.

- [ ] **Step 2: Add page_id to each render_template() call in app.py**

Add the corresponding `page_id` kwarg to each route.

- [ ] **Step 3: Smoke test each page**

Visit each URL:
- `/heatmap` — sidebar active, summary stat cards, heatmap renders
- `/passage-profile?book=Matthew&chapter_start=5&chapter_end=7` — stat cards, root freq table
- `/collocations` — filter chips, matrix table
- `/parallel` — side-by-side columns, Syriac RTL
- `/visualize/sh-l-m` — D3 graph in `#viz-container`, root card below
- `/constellation?book=Matthew&chapter=5&v_start=1&v_end=12` — D3 in `#constellation-container`
- `/bookmarks` — tab bar, bookmark list or empty state
- `/about` — about sections, methodology caveats
- `/annotations` — annotation list
- `/semantic-fields` — cluster cards
- `/parse` — word parser form + result

- [ ] **Step 4: Commit all at once**

```bash
git add templates/heatmap.html templates/passage_profile.html templates/collocations.html \
        templates/parallel.html templates/visualize.html templates/constellation.html \
        templates/bookmarks.html templates/about.html templates/annotations.html \
        templates/semantic_fields.html templates/parse.html app.py
git commit -m "feat: extend new shell to all remaining pages"
```

---

## Task 13: Mobile responsiveness audit

**Files:**
- Modify: `static/style.css` (append if needed)

The new CSS already has two breakpoints. Test on a narrow viewport and fix any overflow.

- [ ] **Step 1: Test at 375px width**

Open DevTools → responsive mode → 375px wide. Check:
- Sidebar collapses to `display:none` → ✅ (`.app { grid-template-columns: 1fr }` at 760px)
- `.content` padding is `32px 22px 60px` at 760px → ✅
- `.il-grid` wraps correctly → check
- `.kwic-table` scrolls horizontally if needed → check
- `.entry-grid` collapses to single column at 1100px → ✅ (in new CSS)

If `.kwic-table` overflows on mobile, add:
```css
@media (max-width:760px){
  .kwic-table{display:block;overflow-x:auto;-webkit-overflow-scrolling:touch}
  .kwic-table .left,.kwic-table .right{width:auto}
}
```

- [ ] **Step 2: Commit if changes made**

```bash
git add static/style.css
git commit -m "fix: mobile overflow for kwic-table and il-grid"
```

---

## Task 14: Final review and branch cleanup

**Files:**
- Read-only review

- [ ] **Step 1: Check all pages load without 500 errors**

Run the Flask server and visit every route. Check the terminal for any Jinja2 `UndefinedError`. Common issues:
- `page_id` not passed from app.py → add to render_template() calls
- Template variable name mismatch (e.g. `stats.by_corpus` vs `by_corpus`) → fix to match app.py

- [ ] **Step 2: Check browser console for JS errors**

On each page, open DevTools → Console. Common issues:
- `setTheme is not defined` → app.js not loaded → check `{% block scripts %}` order in base.html
- `toggleChip is not defined` → app.js loaded before DOM ready → check DOMContentLoaded wrapper

- [ ] **Step 3: Verify dark mode works end-to-end**

1. Click Dark in sidebar footer → page goes dark → `data-theme="dark"` on `<html>` → ✅
2. Reload → dark mode persists (localStorage `'ara.theme'`)
3. Click Auto → `data-theme` removed → system preference applies

- [ ] **Step 4: Verify cite modal works on all wired pages**

Visit concordance, diachronic, hapax, interlinear, reader — cite button opens modal, all 5 citation formats populate, Copy button works.

- [ ] **Step 5: Final commit message and summary**

```bash
git log --oneline feature/ui-redesign ^main | head -20
```

Review commit history, confirm no leftover debug code.

---

## Appendix: CSS Class Mapping

Quick reference for updating old class names to new ones when porting templates:

| Old | New |
|-----|-----|
| `.corpus-badge.corpus-peshitta_nt` | `.cbadge.pnt` |
| `.corpus-badge.corpus-peshitta_ot` | `.cbadge.pot` |
| `.corpus-badge.corpus-biblical_aramaic` | `.cbadge.bib` |
| `.corpus-badge.corpus-targum_onkelos` | `.cbadge.tar` |
| `.corpus-badge.corpus-ephrem_nisibis` | `.cbadge.eph` |
| `nav.nav` | `aside.side` (JS-rendered) |
| `main.main` | `div.main > main.content` |
| `footer.footer` | `footer.foot` |
| `.card` | `.surface` (background token only) |
| `.dark` on body | `[data-theme="dark"]` on html |
| `localStorage 'theme'` | `localStorage 'ara.theme'` |
| `.search-input` | `.s-input` |
| `.search-select` | `.s-select` |
| `.search-label` | `.s-label` |
| `.search-form` | `.s-body` |
| `.filter-chip` | `.chip` |
| `.filter-chip.active` | `.chip.on` |
| `.concordance-table` | `.kwic-table` |
| `.hapax-table` | `.dtable` |
| `.diac-bar` | `.dia-bar.<abbr>` |
| `.il-word` | `.il-tok` |
| `.il-syr` | `.il-tok .syr` |

## Appendix: app.py page_id reference

Add these kwargs to each render_template() call:

```python
# Route → page_id
'/'                     → page_id='search'
'/browse'               → page_id='browse'
'/read/<book>/<ch>'     → page_id='reader'
'/concordance'          → page_id='concordance'
'/diachronic'           → page_id='diachronic'
'/interlinear'          → page_id='interlinear'
'/hapax'                → page_id='hapax'
'/heatmap'              → page_id='heatmap'
'/bookmarks'            → page_id='bookmarks'
'/about'                → page_id='about'
'/parallel'             → page_id='parallel'
'/visualize/<root>'     → page_id='search'
'/constellation'        → page_id='search'
'/passage-profile'      → page_id='search'
'/collocations'         → page_id='search'
'/parse'                → page_id='search'
'/semantic-fields'      → page_id='search'
'/annotations'          → page_id='search'
```
