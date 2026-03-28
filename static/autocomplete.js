/**
 * initRootAutocomplete(inputId, listId, onSelect)
 *
 * Attaches root autocomplete behaviour to an <input> element.
 *   inputId  — id of the text input
 *   listId   — id of the .autocomplete-list container
 *   onSelect — callback fired when the user picks a suggestion (receives the translit string)
 *
 * Handles:
 *  - Dash auto-insertion after consonant letters
 *  - Digraph detection (SH, KH, TH, TS)
 *  - Debounced fetch from /api/suggest
 *  - Keyboard: Enter triggers onSelect with current value, Escape closes list
 *  - Click-outside closes list
 */
function initRootAutocomplete(inputId, listId, onSelect) {
    var inp = document.getElementById(inputId);
    var acList = document.getElementById(listId);
    if (!inp || !acList) return;

    var acTimeout = null;
    var DIGRAPHS = ['SH', 'KH', 'TH', 'TS'];
    var DIGRAPH_STARTS = ['S', 'K', 'T'];

    function escHtml(s) {
        var d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    inp.addEventListener('keydown', function(e) {
        if (e.key === '-') e.preventDefault();
        if (e.key === 'Enter') { acList.innerHTML = ''; onSelect(inp.value.trim()); }
        if (e.key === 'Escape') { acList.innerHTML = ''; }
    });

    inp.addEventListener('input', function(e) {
        var v = this.value.toUpperCase();
        if (e.inputType && e.inputType.indexOf('delete') !== -1) {
            this.value = v; fetchSuggestions(v); return;
        }
        var clean = v.replace(/-+$/, '');
        var parts = clean.split('-').filter(function(p) { return p.length > 0; });
        var last = parts[parts.length - 1] || '';
        var completedParts = parts.length - (last.length > 0 ? 1 : 0);
        var isComplete = (last.length === 2 && DIGRAPHS.indexOf(last) !== -1) ||
                         (last.length === 1 && DIGRAPH_STARTS.indexOf(last) === -1);
        var isInvalidDigraph = (last.length === 2 && DIGRAPHS.indexOf(last) === -1);
        if (isComplete && completedParts < 2) {
            this.value = v + '-';
        } else if (isInvalidDigraph && completedParts < 2) {
            var np = parts.slice(0, -1).concat([last[0], last[1]]);
            var fx = np.join('-');
            if (np.length < 3) fx += '-';
            this.value = fx;
        } else {
            this.value = v;
        }
        fetchSuggestions(this.value.replace(/-+$/, ''));
    });

    function fetchSuggestions(prefix) {
        clearTimeout(acTimeout);
        if (!prefix) { acList.innerHTML = ''; return; }
        acTimeout = setTimeout(function() {
            fetch('/api/suggest?prefix=' + encodeURIComponent(prefix))
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    acList.innerHTML = '';
                    data.forEach(function(d) {
                        var item = document.createElement('div');
                        item.className = 'autocomplete-item';
                        item.innerHTML =
                            '<span class="ac-syriac">' + escHtml(d.root) + '</span> ' +
                            '<span class="ac-translit">' + escHtml(d.translit) + '</span> ' +
                            '<span class="ac-count">(' + d.count + ')</span>';
                        item.setAttribute('data-value', d.translit);
                        item.addEventListener('click', function() {
                            inp.value = this.getAttribute('data-value');
                            acList.innerHTML = '';
                            onSelect(inp.value.trim());
                        });
                        acList.appendChild(item);
                    });
                });
        }, 150);
    }

    document.addEventListener('click', function(e) {
        if (!inp.contains(e.target) && !acList.contains(e.target)) acList.innerHTML = '';
    });
}
