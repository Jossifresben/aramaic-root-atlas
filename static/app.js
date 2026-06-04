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
  var S = window.SIDE_I18N || {};
  var NAV = {
    discover: [
      { id:'discover-home', href:'/',          label: S.nav_discover_home || 'Discover',
        ic:'<path d="M12 2l2.5 7H22l-6 4.5L18.5 22 12 17.5 5.5 22 8 13.5 2 9h7.5z"/>' },
      { id:'discover',      href:'/discover',   label: S.nav_journeys || 'Journeys',
        ic:'<path d="M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3z"/><path d="M9 3v15M15 6v15"/>' },
    ],
    explore: [
      { id:'search',      href:'/search',          label: S.nav_trace_root   || 'Trace Root',        kbd:'/',
        ic:'<circle cx="11" cy="11" r="7"/><path d="M21 21l-5-5"/>' },
      { id:'browse',      href:'/browse',          label: S.nav_browse       || 'Browse corpora',
        ic:'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>' },
      { id:'interlinear', href:'/interlinear',     label: S.nav_interlinear  || 'Interlinear Reader',
        ic:'<path d="M3 6h18M3 11h18M3 16h12"/>' },
      { id:'parallel',    href:'/parallel',        label: S.nav_parallel     || 'Parallel viewer',
        ic:'<path d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2v-4M9 21H5a2 2 0 01-2-2v-4m0 0h18"/>' },
    ],
    analyze: [
      { id:'concordance',     href:'/concordance',      label: S.nav_concordance  || 'Concordance',
        ic:'<path d="M4 6h16M4 12h16M4 18h10"/>' },
      { id:'diachronic',      href:'/diachronic',       label: S.nav_diachronic   || 'Diachronic Analysis',
        ic:'<path d="M3 20V4M3 20h18M7 16l3-4 4 2 5-7"/>' },
      { id:'hapax',           href:'/hapax',            label: S.nav_hapax        || 'Hapax Legomena',
        ic:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>' },
      { id:'heatmap',         href:'/heatmap',          label: S.nav_heatmap      || 'Frequency Map',
        ic:'<rect x="3" y="3" width="4" height="4"/><rect x="10" y="3" width="4" height="4"/><rect x="17" y="3" width="4" height="4"/><rect x="3" y="10" width="4" height="4"/><rect x="10" y="10" width="4" height="4"/><rect x="17" y="10" width="4" height="4"/><rect x="3" y="17" width="4" height="4"/><rect x="10" y="17" width="4" height="4"/><rect x="17" y="17" width="4" height="4"/>' },
      { id:'parse',           href:'/parse',            label: S.nav_parse        || 'Word Parser',
        ic:'<path d="M4 7h3m10 0h3M4 12h3m10 0h3M4 17h3m10 0h3M10 7v10"/>' },
      { id:'collocations',    href:'/collocations',     label: S.nav_collocations || 'Collocations',
        ic:'<circle cx="9" cy="12" r="4"/><circle cx="15" cy="12" r="4"/>' },
      { id:'semantic-fields', href:'/semantic-fields',  label: S.nav_semantic     || 'Semantic Fields',
        ic:'<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12M2 12h3M19 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12"/>' },
      { id:'passage-profile', href:'/passage-profile',  label: S.nav_passage      || 'Passage Profile',
        ic:'<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>' },
    ],
    workspace: [
      { id:'bookmarks',   href:'/bookmarks',    label: S.nav_bookmarks    || 'Bookmarks',
        ic:'<path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/>' },
      { id:'annotations', href:'/annotations',  label: S.nav_annotations  || 'Research Notes',
        ic:'<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>' },
    ],
    info: [
      { id:'about', href:'/about', label: S.nav_about || 'About & Guide',
        ic:'<circle cx="12" cy="12" r="9"/><path d="M12 8v4M12 16v.01"/>' },
    ],
  };

  function renderSidebar(){
    var side = document.querySelector('.side');
    if(!side) return;
    var active = side.dataset.page || 'search';
    // Preserve current UI language across all nav links
    var lang = document.documentElement.lang || 'en';
    var langSuffix = lang !== 'en' ? '?lang=' + lang : '';
    function withLang(href){
      if(!langSuffix) return href;
      return href + (href.indexOf('?') >= 0 ? '&lang=' + lang : '?lang=' + lang);
    }
    function link(it){
      return '<a href="'+withLang(it.href)+'" class="side-link'+(it.id===active?' active':'')+'">'
        +'<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">'+it.ic+'</svg>'
        +it.label
        +(it.kbd?'<span class="kbd">'+it.kbd+'</span>':'')
        +'</a>';
    }
    var SI = window.SIDE_I18N || {};

    // Collapsible-group state (persisted). Analyze + Workspace start collapsed;
    // a group containing the active page is always shown.
    function collapseState(){ try{ return JSON.parse(localStorage.getItem('side_collapsed') || '{}'); }catch(e){ return {}; } }
    function isCollapsed(id, items){
      if(items.some(function(it){ return it.id === active; })) return false;
      var s = collapseState();
      return id in s ? !!s[id] : (id === 'analyze' || id === 'workspace');
    }
    function group(id, label, items, collapsible){
      var collapsed = collapsible && isCollapsed(id, items);
      return '<div class="side-group'+(collapsible?' collapsible':'')+(collapsed?' collapsed':'')+'" id="side-'+id+'" data-group="'+id+'">'
        +'<div class="side-label"'+(collapsible?' role="button" tabindex="0" aria-expanded="'+(!collapsed)+'"':'')+'>'
          +'<span>'+label+'</span>'
          +(collapsible?'<svg class="side-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M6 9l6 6 6-6"/></svg>':'')
        +'</div>'
        +items.map(link).join('')
      +'</div>';
    }

    side.innerHTML = ''
      +'<a href="'+withLang('/')+'" class="brand">'
        +'<div class="brand-mark">ܐ</div>'
        +'<div class="brand-text"><div class="brand-name">Root Atlas</div>'
        +'<div class="brand-sub">Aramaic Corpora</div></div>'
      +'</a>'
      +group('discover',  (SI.discover||'Discover'),   NAV.discover,  false)
      +group('explore',   (SI.explore||'Explore'),     NAV.explore,   true)
      +group('analyze',   (SI.analyze||'Analyze'),     NAV.analyze,   true)
      +group('workspace', (SI.workspace||'Workspace'), NAV.workspace, true)
      +'<div class="side-group">'
        +NAV.info.map(link).join('')
      +'</div>'
      +'<div class="side-foot">'
        +'<div>By <a href="https://jossifresco.com">Jossi Fresco</a> · '
          +'<a href="https://github.com/Jossifresben/aramaic-root-atlas">GitHub</a></div>'
        +'<div class="v">v 3.1.1 · DOI 10.5281/zenodo.19358625</div>'
        +'<div class="theme-tog" role="group" aria-label="Theme">'
          +'<button data-theme="light" onclick="setTheme(\'light\')">Light</button>'
          +'<button data-theme="dark"  onclick="setTheme(\'dark\')">Dark</button>'
          +'<button data-theme="system" onclick="setTheme(\'system\')">Auto</button>'
        +'</div>'
      +'</div>';

    // Wire collapse toggles
    side.querySelectorAll('.side-group.collapsible > .side-label').forEach(function(lbl){
      function toggle(){
        var g = lbl.closest('.side-group');
        var nowCollapsed = !g.classList.contains('collapsed');
        g.classList.toggle('collapsed', nowCollapsed);
        lbl.setAttribute('aria-expanded', String(!nowCollapsed));
        var st = collapseState(); st[g.dataset.group] = nowCollapsed;
        try{ localStorage.setItem('side_collapsed', JSON.stringify(st)); }catch(e){}
      }
      lbl.addEventListener('click', toggle);
      lbl.addEventListener('keydown', function(e){ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); toggle(); } });
    });

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
    wireQuickSearch();
  });

  function wireQuickSearch(){
    var qInp  = document.getElementById('quick-search-input');
    var qList = document.getElementById('quick-search-list');
    var qTimer = null;

    function escHtml(s){
      return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }
    function closeList(){
      if(qList){ qList.innerHTML=''; qList.hidden=true; }
    }
    function navigate(q){
      // Root: contains a dash (SH-L-M style) or is Syriac/Hebrew Unicode
      // Plain words like "shalom" or "peace" go to text search
      var isRoot = /[-]/.test(q) || /[܀-ݏ֐-׿]/.test(q);
      var lang = document.documentElement.lang || 'en';
      if(isRoot){
        window.location.href = '/?q='+encodeURIComponent(q.toUpperCase())+'&lang='+lang+'&tab=root';
      } else {
        window.location.href = '/?q='+encodeURIComponent(q)+'&lang='+lang+'&tab=text';
      }
    }

    // ⌘K / Ctrl+K — focus the quick-search from anywhere
    document.addEventListener('keydown', function(e){
      if((e.metaKey || e.ctrlKey) && e.key === 'k'){
        e.preventDefault();
        if(qInp){ qInp.focus(); qInp.select(); }
      }
    });

    // / key — navigate to Trace Root (or focus root input if already there)
    document.addEventListener('keydown', function(e){
      if(e.key !== '/') return;
      // Don't intercept if focus is inside any input/textarea/select/contenteditable
      var tag = document.activeElement && document.activeElement.tagName;
      if(tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
      if(document.activeElement && document.activeElement.isContentEditable) return;
      e.preventDefault();
      // If already on the home page, focus the root input directly
      var rootInp = document.getElementById('rootInput');
      if(rootInp){
        rootInp.focus(); rootInp.select();
      } else {
        var lang = document.documentElement.lang || 'en';
        window.location.href = '/?lang=' + lang;
      }
    });

    if(!qInp || !qList) return;

    // Live suggestions from /api/suggest
    qInp.addEventListener('input', function(){
      var v = this.value.trim();
      clearTimeout(qTimer);
      if(!v){ closeList(); return; }
      qTimer = setTimeout(function(){
        fetch('/api/suggest?prefix='+encodeURIComponent(v.toUpperCase()))
          .then(function(r){ return r.json(); })
          .then(function(data){
            if(!data.length){ closeList(); return; }
            qList.innerHTML = data.map(function(d){
              return '<div class="qs-item" data-root="'+escHtml(d.translit)+'">'
                +'<span class="qs-syr">'+escHtml(d.root)+'</span>'
                +'<span class="qs-tr">'+escHtml(d.translit)+'</span>'
                +'<span class="qs-ct">'+escHtml(String(d.count))+'</span>'
                +'</div>';
            }).join('');
            qList.hidden = false;
            qList.querySelectorAll('.qs-item').forEach(function(it){
              it.addEventListener('click', function(){
                var r = this.dataset.root;
                closeList(); qInp.value = '';
                window.location.href = '/visualize/'+encodeURIComponent(r)+'?tab=ficha';
              });
            });
          })
          .catch(function(){ closeList(); });
      }, 150);
    });

    // Keyboard: Escape closes, Enter navigates
    qInp.addEventListener('keydown', function(e){
      if(e.key === 'Escape'){ closeList(); qInp.blur(); return; }
      if(e.key !== 'Enter') return;
      var q = qInp.value.trim();
      if(!q) return;
      closeList();
      navigate(q);
    });

    // Click outside closes
    document.addEventListener('click', function(e){
      if(!qInp.contains(e.target) && !qList.contains(e.target)) closeList();
    });
  }
})();
