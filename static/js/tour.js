/* Aramaic Root Atlas — Guided Tour (Driver.js v1) */
(function () {
    'use strict';

    var I18N      = window.TOUR_I18N  || {};
    var IS_RTL    = window.TOUR_IS_RTL || false;
    var STORAGE   = 'atlas_tour_seen';
    var isHome    = window.location.pathname === '/';

    function t(key) { return I18N[key] || ''; }

    /* Helper: only add a step if the element exists in the DOM */
    function addStep(steps, selector, popover) {
        if (!document.querySelector(selector)) return;
        steps.push({ element: selector, popover: popover });
    }

    /* ---- Build step list ----------------------------------------- */
    function buildSteps() {
        var steps = [];

        // Step 1: Welcome — sidebar brand mark (always present after renderSidebar)
        addStep(steps, '.brand', {
            title: t('welcome_title'),
            description: t('welcome_body'),
            side: 'right', align: 'start'
        });

        // Step 2: Explore group — Trace Root, Browse, Interlinear, Parallel
        addStep(steps, '#side-explore', {
            title: t('nav_explore_title'),
            description: t('nav_explore_body'),
            side: 'right', align: 'start'
        });

        // Step 3: Analyze group — research tools
        addStep(steps, '#side-analyze', {
            title: t('nav_research_title'),
            description: t('nav_research_body'),
            side: 'right', align: 'start'
        });

        // Step 4: Quick search bar (always present)
        addStep(steps, '.quick-search', {
            title: t('search_title') || 'Quick Search',
            description: t('search_body') || 'Type any root or text here. Press ⌘K from anywhere to focus.',
            side: 'bottom', align: 'start'
        });

        // Steps 5-8 only on homepage (elements use .s-tab / .s-panel structure)
        if (isHome) {
            addStep(steps, '.s-tab[data-tab="root"]', {
                title: t('search_title'),
                description: t('search_body'),
                side: 'bottom', align: 'start'
            });
            addStep(steps, '.s-tab[data-tab="cognate"]', {
                title: t('cognate_title'),
                description: t('cognate_body'),
                side: 'bottom', align: 'start'
            });
            addStep(steps, '.s-tab[data-tab="meaning"]', {
                title: t('meaning_title'),
                description: t('meaning_body'),
                side: 'bottom', align: 'start'
            });
            addStep(steps, '.s-tab[data-tab="text"]', {
                title: t('text_title'),
                description: t('text_body'),
                side: 'bottom', align: 'start'
            });
            // Corpus stats row (if present)
            addStep(steps, '.corpus-cells', {
                title: t('nav_browse_title'),
                description: t('nav_browse_body'),
                side: 'top', align: 'center'
            });
        }

        // Workspace group — Bookmarks, Research Notes
        addStep(steps, '#side-workspace', {
            title: t('bookmarks_title'),
            description: t('bookmarks_body'),
            side: 'right', align: 'start'
        });

        // Settings toggle (always present in topbar)
        addStep(steps, '#settings-toggle', {
            title: t('settings_title'),
            description: t('settings_body'),
            side: 'left', align: 'start'
        });

        // Language selector (always present)
        addStep(steps, '#lang-toggle', {
            title: t('lang_title'),
            description: t('lang_body'),
            side: 'left', align: 'start'
        });

        // Share / QR (always present)
        addStep(steps, '#share-toggle', {
            title: t('share_title'),
            description: t('share_body'),
            side: 'left', align: 'start'
        });

        // Tour button itself — wrap-up
        addStep(steps, '#tour-nav-btn', {
            title: t('end_title'),
            description: t('end_body'),
            side: 'left', align: 'end'
        });

        return steps;
    }

    /* ---- Launch tour --------------------------------------------- */
    function startTour() {
        var driverFn = (window.driver && window.driver.js && typeof window.driver.js.driver === 'function')
            ? window.driver.js.driver
            : typeof window.driver === 'function'
                ? window.driver
                : null;

        if (!driverFn) {
            console.warn('Aramaic Root Atlas: Driver.js not loaded — tour unavailable.');
            return;
        }

        var driverObj = driverFn({
            showProgress:  true,
            animate:       true,
            allowClose:    true,
            overlayColor:  'rgba(0,0,0,0.6)',
            nextBtnText:   t('next')   || 'Next',
            prevBtnText:   IS_RTL ? '→' : '←',
            doneBtnText:   t('finish') || 'Done',
            popoverClass:  'atlas-tour-popover' + (IS_RTL ? ' atlas-tour-rtl' : ''),
            steps: buildSteps(),
            onDestroyStarted: function () {
                localStorage.setItem(STORAGE, '1');
                hideTourBtn();
                driverObj.destroy();
            }
        });

        driverObj.drive();
    }

    /* ---- Hide/show the homepage "Guided Tour" button -------------- */
    function hideTourBtn() {
        var btn = document.querySelector('#tour-start-container .tour-start-btn');
        if (btn) btn.style.display = 'none';

        var hint = document.getElementById('tour-restart-hint');
        if (hint) {
            hint.style.display = 'block';
            hint.style.opacity = '1';
            setTimeout(function () {
                hint.style.opacity = '0';
                setTimeout(function () { hint.style.display = 'none'; }, 650);
            }, 4000);
        }
    }

    function syncTourBtn() {
        if (!localStorage.getItem(STORAGE)) return;
        var btn = document.querySelector('#tour-start-container .tour-start-btn');
        if (btn) btn.style.display = 'none';
    }

    window.startTourFromBtn = function () { startTour(); };
    window.startTour = startTour;

    document.addEventListener('DOMContentLoaded', function () {
        syncTourBtn();

        var btn = document.getElementById('tour-nav-btn');
        if (btn) {
            btn.addEventListener('click', function () {
                localStorage.removeItem(STORAGE);
                startTour();
            });
        }
    });

    if (new URLSearchParams(window.location.search).get('tour') === '1') {
        window.addEventListener('load', function () {
            setTimeout(startTour, 400);
        });
    }

})();
