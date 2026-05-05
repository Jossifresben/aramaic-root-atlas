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
