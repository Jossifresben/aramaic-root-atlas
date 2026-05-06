/* cite-modal.js — Multi-format citation modal for Aramaic Root Atlas
 *
 * Public API:
 *   openCiteModal(ctx)   — opens modal and renders all formats
 *   closeCiteModal()     — closes modal
 *   switchCiteTab(tab)   — switches active tab
 *   copyCiteText()       — copies current tab text to clipboard
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
        return AUTHOR_FULL + '. ' + YEAR + '. "' + title + '."' +
               ' Version ' + VERSION + '. ' + url + '. ' +
               'https://doi.org/' + DOI + '.';
    }

    function buildMLA(ctx) {
        var title = buildTitle(ctx);
        var url   = ctx.url || window.location.href;
        return AUTHOR_FULL + '. "' + title + '."' +
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
        if (tool === 'concordance')          subtitle = ' Concordance,' + rootPart;
        else if (tool === 'interlinear')     subtitle = ' Interlinear Reader.';
        else if (tool === 'hapax')           subtitle = ' Hapax Legomena.';
        else if (tool === 'diachronic')      subtitle = ' Diachronic Analysis,' + rootPart;
        else if (tool === 'passage_profile') subtitle = ' Passage Profile.';
        return AUTHOR_FULL + '.' + subtitle +
               ' "Aramaic Root Atlas"' + corpus +
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
            btn.innerHTML = '✓ Copied!';
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
