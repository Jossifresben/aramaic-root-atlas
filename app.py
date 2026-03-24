"""Aramaic Root Atlas — a cross-corpus triliteral root explorer."""

import json
import os
import threading

from flask import Flask, render_template, request, jsonify

from aramaic_core.corpus import AramaicCorpus
from aramaic_core.extractor import RootExtractor
from aramaic_core.cognates import CognateLookup
from aramaic_core.glosser import WordGlosser
from aramaic_core.characters import (
    parse_root_input, transliterate_syriac, semitic_root_variants,
    transliterate_syriac_academic, transliterate_syriac_to_hebrew,
    transliterate_syriac_to_arabic,
)

app = Flask(__name__)

# --- Globals ---
_corpus: AramaicCorpus | None = None
_extractor: RootExtractor | None = None
_cognate_lookup: CognateLookup | None = None
_glosser: WordGlosser | None = None
_i18n: dict = {}
_cognates_raw: dict = {}
_initialized = False
_init_lock = threading.Lock()

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
CORPORA_DIR = os.path.join(DATA_DIR, 'corpora')
ROOTS_DIR = os.path.join(DATA_DIR, 'roots')
TRANSLATIONS_DIR = os.path.join(DATA_DIR, 'translations')


def _init():
    global _corpus, _extractor, _cognate_lookup, _glosser
    global _i18n, _cognates_raw, _initialized

    if _initialized:
        return

    with _init_lock:
        if _initialized:
            return

        # Load i18n
        i18n_path = os.path.join(DATA_DIR, 'i18n.json')
        if os.path.exists(i18n_path):
            with open(i18n_path, 'r', encoding='utf-8') as f:
                _i18n = json.load(f)

        # Load raw cognates JSON
        cog_path = os.path.join(ROOTS_DIR, 'cognates.json')
        if os.path.exists(cog_path):
            with open(cog_path, 'r', encoding='utf-8') as f:
                _cognates_raw = json.load(f)

        # Load corpus — multiple CSVs
        _corpus = AramaicCorpus()
        _corpus.set_translations_dir(TRANSLATIONS_DIR)

        nt_path = os.path.join(CORPORA_DIR, 'peshitta_nt.csv')
        if os.path.exists(nt_path):
            _corpus.add_corpus('peshitta_nt', 'Peshitta NT', nt_path)

        ot_path = os.path.join(CORPORA_DIR, 'peshitta_ot.csv')
        if os.path.exists(ot_path):
            _corpus.add_corpus('peshitta_ot', 'Peshitta OT', ot_path)

        ba_path = os.path.join(CORPORA_DIR, 'biblical_aramaic.csv')
        if os.path.exists(ba_path):
            _corpus.add_corpus('biblical_aramaic', 'Biblical Aramaic', ba_path)

        to_path = os.path.join(CORPORA_DIR, 'targum_onkelos.csv')
        if os.path.exists(to_path):
            _corpus.add_corpus('targum_onkelos', 'Targum Onkelos', to_path)

        _corpus.load()

        # Build root index
        _extractor = RootExtractor(_corpus, ROOTS_DIR)
        _extractor.build_index()

        # Load cognates
        _cognate_lookup = CognateLookup(ROOTS_DIR)
        _cognate_lookup.load()

        # Initialize word glosser
        _glosser = WordGlosser(_cognate_lookup, _extractor, ROOTS_DIR)

        _initialized = True


# --- Helper ---
VALID_SCRIPTS = ('latin', 'syriac', 'hebrew', 'arabic')
VALID_TRANS = ('en', 'es', 'he', 'ar')


def _get_lang() -> str:
    return request.args.get('lang', 'en')


def _get_script() -> str:
    s = request.args.get('script', 'latin')
    return s if s in VALID_SCRIPTS else 'latin'


def _get_trans() -> str:
    t = request.args.get('trans', _get_lang())
    return t if t in VALID_TRANS else _get_lang()


class TranslationProxy:
    """Supports both t('key') function calls and t.key attribute access."""
    def __init__(self, lang_fn):
        object.__setattr__(self, '_lang_fn', lang_fn)

    def __call__(self, key, lang=None):
        if lang is None:
            lang = self._lang_fn()
        return _i18n.get(lang, {}).get(key, _i18n.get('en', {}).get(key, key))

    def __getattr__(self, key):
        return self(key)


_t_proxy = TranslationProxy(_get_lang)


def _t(key: str, lang: str | None = None) -> str:
    """Translate a UI string."""
    return _t_proxy(key, lang)


def _bn(book: str, lang: str | None = None) -> str:
    """Translate a book name."""
    if lang is None:
        lang = _get_lang()
    names = _i18n.get(lang, {}).get('book_names', {})
    return names.get(book, _i18n.get('en', {}).get('book_names', {}).get(book, book))


# --- Routes ---

@app.before_request
def ensure_initialized():
    _init()


@app.route('/')
def index():
    lang = _get_lang()
    corpora_info = []
    for cid in _corpus.get_corpus_ids():
        info = _corpus.get_corpus_info(cid)
        if info:
            corpora_info.append({
                'id': info.corpus_id,
                'label': info.label,
                'verses': info.verse_count,
                'words': info.word_count,
            })
    book_names = _i18n.get(lang, {}).get('book_names', {})
    return render_template('index.html',
                           lang=lang, script=_get_script(), trans=_get_trans(),
                           t=_t_proxy, bn=_bn,
                           book_names_json=json.dumps(book_names, ensure_ascii=False),
                           corpora=corpora_info,
                           root_count=_extractor.get_root_count(),
                           total_words=_corpus.total_words(),
                           total_unique=_corpus.total_unique())


@app.route('/api/stats')
def api_stats():
    """Return corpus statistics."""
    corpora = []
    for cid in _corpus.get_corpus_ids():
        info = _corpus.get_corpus_info(cid)
        if info:
            corpora.append({
                'id': info.corpus_id,
                'label': info.label,
                'verses': info.verse_count,
                'words': info.word_count,
            })
    return jsonify({
        'corpora': corpora,
        'total_verses': sum(c['verses'] for c in corpora),
        'total_words': _corpus.total_words(),
        'total_unique': _corpus.total_unique(),
        'root_count': _extractor.get_root_count(),
    })


@app.route('/api/roots')
def api_roots():
    """Search for a root across all corpora."""
    query = request.args.get('q', '').strip()
    corpus_filter = request.args.get('corpus', None)
    lang = _get_lang()

    if not query:
        return jsonify({'error': 'Missing query parameter q'}), 400

    # Parse root input (e.g., "K-T-B" -> Syriac)
    root_syriac = parse_root_input(query)
    if not root_syriac:
        return jsonify({'error': f'Could not parse root: {query}'}), 400

    entry = _extractor.lookup_root(root_syriac)
    if not entry:
        # Try Semitic variants
        for variant in semitic_root_variants(root_syriac):
            entry = _extractor.lookup_root(variant)
            if entry:
                root_syriac = variant
                break

    if not entry:
        return jsonify({'error': f'Root not found: {query}'}), 404

    # Get cognates
    cognate = _cognate_lookup.lookup(root_syriac)

    # Build response
    matches = []
    for m in entry.matches:
        refs = m.references
        if corpus_filter:
            refs = [r for r in refs if _corpus.get_verse_corpus(r) == corpus_filter]
        if not refs:
            continue
        matches.append({
            'form': m.form,
            'transliteration': m.transliteration,
            'count': len(refs),
            'references': refs[:20],  # cap for response size
            'gloss_en': _glosser.gloss(m.form, root_syriac, 'en'),
            'gloss_es': _glosser.gloss(m.form, root_syriac, 'es'),
        })

    # Cross-corpus attestation counts
    corpus_counts = {}
    for m in entry.matches:
        for ref in m.references:
            cid = _corpus.get_verse_corpus(ref)
            corpus_counts[cid] = corpus_counts.get(cid, 0) + 1

    # Root display forms in different scripts
    root_display = _extractor.get_root_display(root_syriac)
    root_scripts = list(_extractor.get_root_scripts(root_syriac))

    result = {
        'root': root_syriac,
        'root_transliteration': _translit_to_dash(root_syriac),
        'root_academic': transliterate_syriac_academic(root_syriac),
        'total_occurrences': sum(m['count'] for m in matches),
        'matches': matches,
        'corpus_attestation': corpus_counts,
        'root_display': root_display,
        'root_scripts': root_scripts,
    }

    if cognate:
        result['cognates'] = {
            'gloss_en': cognate.gloss_en,
            'gloss_es': cognate.gloss_es,
            'sabor_raiz_en': cognate.sabor_raiz_en,
            'sabor_raiz_es': cognate.sabor_raiz_es,
            'hebrew': [{'word': h.word, 'transliteration': h.transliteration,
                        'meaning_en': h.meaning_en, 'meaning_es': h.meaning_es}
                       for h in cognate.hebrew],
            'arabic': [{'word': a.word, 'transliteration': a.transliteration,
                        'meaning_en': a.meaning_en, 'meaning_es': a.meaning_es}
                       for a in cognate.arabic],
        }

    return jsonify(result)


@app.route('/api/books')
def api_books():
    """Return list of books, optionally filtered by corpus."""
    corpus_filter = request.args.get('corpus', None)
    books = _corpus.get_books(corpus_filter)
    return jsonify({
        'books': [{'name': b, 'chapters': ch} for b, ch in books],
        'corpus': corpus_filter,
    })


@app.route('/api/chapter/<path:book>/<int:chapter>')
def api_chapter(book, chapter):
    """Return all verses in a chapter.

    If ?parallel=true, returns all corpus versions of each verse.
    Otherwise returns one version per verse (filtered or last-loaded).
    """
    corpus_filter = request.args.get('corpus', None)
    trans = request.args.get('trans', 'en')
    parallel = request.args.get('parallel', '') == 'true'

    verses = _corpus.get_chapter_verses(book, chapter, corpus_filter)
    result = []

    if parallel and not corpus_filter:
        # Return all corpus versions for each verse
        seen_refs = set()
        for v_num, ref, syriac in verses:
            if ref in seen_refs:
                continue
            seen_refs.add(ref)
            corpora = _corpus.get_verse_corpora(ref)
            for cid in corpora:
                text = _corpus.get_verse_text(ref, corpus_id=cid)
                if text:
                    translation = _corpus.get_verse_translation(ref, trans)
                    if not translation and trans != 'en':
                        translation = _corpus.get_verse_translation(ref, 'en')
                    result.append({
                        'verse': v_num,
                        'reference': ref,
                        'syriac': text,
                        'translation': translation,
                        'corpus_id': cid,
                    })
    else:
        for v_num, ref, syriac in verses:
            translation = _corpus.get_verse_translation(ref, trans)
            if not translation and trans != 'en':
                translation = _corpus.get_verse_translation(ref, 'en')
            result.append({
                'verse': v_num,
                'reference': ref,
                'syriac': syriac,
                'translation': translation,
                'corpus_id': _corpus.get_verse_corpus(ref),
            })

    return jsonify({
        'book': book,
        'chapter': chapter,
        'verses': result,
    })


@app.route('/api/search')
def api_search():
    """Search across all corpora."""
    query = request.args.get('q', '').strip()
    lang = _get_lang()
    corpus_filter = request.args.get('corpus', None)

    if not query:
        return jsonify({'error': 'Missing query parameter q'}), 400

    results = _corpus.search_text(query, lang, corpus_filter)
    return jsonify({
        'query': query,
        'count': len(results),
        'results': results[:50],
    })


@app.route('/browse')
def browse():
    lang = _get_lang()
    corpus_filter = request.args.get('corpus', None)
    books = _corpus.get_books(corpus_filter)
    return render_template('browse.html', lang=lang, script=_get_script(), trans=_get_trans(),
                           t=_t_proxy, bn=_bn, books=books, corpus_filter=corpus_filter)


@app.route('/read/<path:book>/<int:chapter>')
def read(book, chapter):
    lang = _get_lang()
    trans = request.args.get('trans', lang)
    verses = _corpus.get_chapter_verses(book, chapter)
    verse_data = []
    for v_num, ref, syriac in verses:
        translation = _corpus.get_verse_translation(ref, trans)
        if not translation and trans != 'en':
            translation = _corpus.get_verse_translation(ref, 'en')
        verse_data.append({
            'verse': v_num,
            'reference': ref,
            'syriac': syriac,
            'translation': translation,
            'corpus_id': _corpus.get_verse_corpus(ref),
        })

    books = _corpus.get_books()
    max_ch = 0
    for b_name, b_ch in books:
        if b_name == book:
            max_ch = b_ch
            break
    return render_template('read.html', lang=lang, script=_get_script(), trans=trans,
                           t=_t_proxy, bn=_bn, book=book, chapter=chapter,
                           verses=verse_data, books=books, max_ch=max_ch)


@app.route('/about')
def about():
    lang = _get_lang()
    return render_template('about.html', lang=lang, script=_get_script(), trans=_get_trans(), t=_t_proxy, bn=_bn)


@app.route('/api/verse')
def api_verse():
    """Return a single verse with word-level data for the modal."""
    ref = request.args.get('ref', '').strip()
    lang = _get_lang()
    trans = request.args.get('trans', lang)
    if not ref:
        return jsonify({'error': 'Missing ref parameter'}), 400

    syriac = _corpus.get_verse_text(ref)
    if not syriac:
        return jsonify({'error': f'Verse not found: {ref}'}), 404

    words = syriac.split()
    words_translit = [transliterate_syriac(w) for w in words]
    words_academic = [transliterate_syriac_academic(w) for w in words]

    result = {
        'reference': ref,
        'reference_display': ref,
        'words': words,
        'words_translit': words_translit,
        'words_translit_academic': words_academic,
        'translation_en': _corpus.get_verse_translation(ref, 'en'),
        'translation_es': _corpus.get_verse_translation(ref, 'es'),
        'translation_he': _corpus.get_verse_translation(ref, 'he'),
        'translation_ar': _corpus.get_verse_translation(ref, 'ar'),
    }

    result['prev_ref'] = _corpus.get_adjacent_ref(ref, -1)
    result['next_ref'] = _corpus.get_adjacent_ref(ref, 1)

    return jsonify(result)


def _translit_to_dash(syriac_root: str) -> str:
    """Convert a Syriac root to dash-separated uppercase Latin: ܫܠܡ -> SH-L-M"""
    from aramaic_core.characters import SYRIAC_TO_LATIN
    parts = []
    for ch in syriac_root:
        if ch in SYRIAC_TO_LATIN:
            parts.append(SYRIAC_TO_LATIN[ch].upper())
    return '-'.join(parts) if parts else ''


@app.route('/api/suggest')
def api_suggest():
    """Return roots matching a Latin-letter prefix for autocomplete."""
    prefix = request.args.get('prefix', '').strip().upper()
    if not prefix:
        return jsonify([])

    # Normalize: O -> E (both map to Ayin), A -> ' (alef)
    normalized = prefix.replace('O', 'E')
    alef_prefix = None
    if normalized.startswith('A'):
        alef_prefix = "'" + normalized[1:]

    results = []
    for entry in _extractor.get_all_roots():
        dash_form = _translit_to_dash(entry.root)
        if (dash_form.startswith(prefix) or
                dash_form.startswith(normalized) or
                (alef_prefix and dash_form.startswith(alef_prefix))):
            results.append({
                'root': entry.root,
                'translit': dash_form,
                'count': entry.total_occurrences,
            })
            if len(results) >= 20:
                break

    return jsonify(results)


def _get_translit_fn(script: str):
    """Return the transliteration function for a script type."""
    if script == 'syriac':
        return lambda w: w  # identity
    elif script == 'hebrew':
        return transliterate_syriac_to_hebrew
    elif script == 'arabic':
        return transliterate_syriac_to_arabic
    else:
        return transliterate_syriac


@app.route('/api/proximity-search')
def api_proximity_search():
    """Find verses where two roots co-occur."""
    root1_str = request.args.get('root1', '').strip()
    root2_str = request.args.get('root2', '').strip()
    scope = request.args.get('scope', 'verse')
    lang = _get_lang()
    trans = _get_trans()
    corpus_filter = request.args.get('corpus', None)

    if not root1_str or not root2_str:
        return jsonify({'error': 'Two roots required'}), 400

    root1_syriac = parse_root_input(root1_str)
    root2_syriac = parse_root_input(root2_str)
    if not root1_syriac or not root2_syriac:
        return jsonify({'error': 'Invalid root input'}), 400

    entry1 = _extractor.lookup_root(root1_syriac)
    entry2 = _extractor.lookup_root(root2_syriac)

    # Try sound correspondence fallback
    if not entry1:
        for v in semitic_root_variants(root1_syriac):
            entry1 = _extractor.lookup_root(v)
            if entry1:
                root1_syriac = v
                break
    if not entry2:
        for v in semitic_root_variants(root2_syriac):
            entry2 = _extractor.lookup_root(v)
            if entry2:
                root2_syriac = v
                break

    if not entry1 or not entry2:
        missing = root1_str if not entry1 else root2_str
        return jsonify({'error': f'Root not found: {missing}', 'results': []})

    # Collect references for each root
    refs1, forms1 = set(), {}
    for m in entry1.matches:
        for ref in m.references:
            if corpus_filter and _corpus.get_verse_corpus(ref) != corpus_filter:
                continue
            refs1.add(ref)
            forms1.setdefault(ref, []).append(m.form)

    refs2, forms2 = set(), {}
    for m in entry2.matches:
        for ref in m.references:
            if corpus_filter and _corpus.get_verse_corpus(ref) != corpus_filter:
                continue
            refs2.add(ref)
            forms2.setdefault(ref, []).append(m.form)

    if scope == 'chapter':
        def ref_to_chapter(r):
            parts = r.rsplit(' ', 1)
            if len(parts) == 2:
                cv = parts[1].split(':')
                return f'{parts[0]} {cv[0]}'
            return r
        ch1 = set(ref_to_chapter(r) for r in refs1)
        ch2 = set(ref_to_chapter(r) for r in refs2)
        common_chapters = sorted(ch1 & ch2)
        return jsonify({
            'root1': _translit_to_dash(root1_syriac),
            'root2': _translit_to_dash(root2_syriac),
            'scope': scope,
            'count': len(common_chapters),
            'results': [{'ref': ch, 'type': 'chapter'} for ch in common_chapters[:50]],
        })

    # Same verse
    script = _get_script()
    translit_fn = _get_translit_fn(script)

    common = sorted(refs1 & refs2)
    results = []
    for ref in common[:100]:
        text = _corpus.get_verse_text(ref) or ''
        translit = ' '.join(translit_fn(w) for w in text.split()) if text else ''
        translation = _corpus.get_verse_translation(ref, trans) or ''
        results.append({
            'ref': ref,
            'syriac': text,
            'translit': translit,
            'translation': translation[:200],
            'forms1': list(set(forms1.get(ref, []))),
            'forms2': list(set(forms2.get(ref, []))),
            'corpus_id': _corpus.get_verse_corpus(ref),
        })

    cognate1 = _cognate_lookup.lookup(root1_syriac)
    cognate2 = _cognate_lookup.lookup(root2_syriac)
    gloss_key = 'gloss_es' if lang == 'es' else 'gloss_en'

    return jsonify({
        'root1': _translit_to_dash(root1_syriac),
        'root2': _translit_to_dash(root2_syriac),
        'root1_syriac': root1_syriac,
        'root2_syriac': root2_syriac,
        'gloss1': getattr(cognate1, gloss_key, '') if cognate1 else '',
        'gloss2': getattr(cognate2, gloss_key, '') if cognate2 else '',
        'scope': scope,
        'count': len(common),
        'results': results,
    })


@app.route('/api/passage-constellation')
def api_passage_constellation():
    """Return constellation data for a passage: roots, cognates, and inter-root connections."""
    book = request.args.get('book', '').strip()
    chapter = request.args.get('chapter', 0, type=int)
    v_start = request.args.get('v_start', 0, type=int)
    v_end = request.args.get('v_end', v_start, type=int)
    lang = _get_lang()
    script = _get_script()
    trans = _get_trans()
    corpus_filter = request.args.get('corpus', None)
    meaning_lang = trans if trans in ('es', 'en') else lang

    if not book or not chapter or not v_start:
        return jsonify({'error': 'Missing book, chapter, or v_start'}), 400

    # Collect verses
    verses = []
    translit_fn = _get_translit_fn(script)
    for v_num in range(v_start, v_end + 1):
        ref = f"{book} {chapter}:{v_num}"
        syriac_text = _corpus.get_verse_text(ref)
        if syriac_text is None:
            continue
        if corpus_filter and _corpus.get_verse_corpus(ref) != corpus_filter:
            continue
        words = syriac_text.split()
        verse_words = []
        for w in words:
            root = _extractor.lookup_word_root(w)
            root_translit = _translit_to_dash(root) if root else None
            verse_words.append({
                'syriac': w,
                'translit': translit_fn(w),
                'root': root_translit,
                'root_syriac': root,
            })
        translation = _corpus.get_verse_translation(ref, trans) or \
                      _corpus.get_verse_translation(ref, 'en') or ''
        verses.append({
            'ref': ref,
            'verse_num': v_num,
            'words': verse_words,
            'translation': translation,
        })

    if not verses:
        return jsonify({'error': 'No verses found'}), 404

    # Collect unique roots
    root_map = {}
    for v in verses:
        for w in v['words']:
            rt = w['root']
            if not rt:
                continue
            if rt not in root_map:
                root_map[rt] = {
                    'root_syriac': w['root_syriac'],
                    'root_translit': rt,
                    'word_forms': [],
                    'count': 0,
                }
            root_map[rt]['count'] += 1
            form_key = w['syriac']
            existing = [f for f in root_map[rt]['word_forms'] if f['syriac'] == form_key]
            if not existing:
                root_map[rt]['word_forms'].append({
                    'syriac': w['syriac'],
                    'translit': w['translit'],
                })

    # Build root data with cognates
    roots_data = []
    for rt, info in root_map.items():
        root_syriac = info['root_syriac']
        cognate_entry = _cognate_lookup.lookup(root_syriac)

        gloss = ''
        if cognate_entry:
            gloss = cognate_entry.gloss_es if meaning_lang == 'es' else cognate_entry.gloss_en
        if not gloss:
            gloss = _extractor.get_root_gloss(root_syriac)

        hebrew, arabic, bridges_raw = [], [], []
        if cognate_entry:
            for hw in cognate_entry.hebrew:
                hebrew.append({
                    'word': hw.word, 'translit': hw.transliteration,
                    'meaning': hw.meaning_es if meaning_lang == 'es' else hw.meaning_en,
                    'outlier': hw.outlier,
                })
            for aw in cognate_entry.arabic:
                arabic.append({
                    'word': aw.word, 'translit': aw.transliteration,
                    'meaning': aw.meaning_es if meaning_lang == 'es' else aw.meaning_en,
                    'outlier': aw.outlier,
                })
            if cognate_entry.semantic_bridges:
                for b in cognate_entry.semantic_bridges:
                    bridges_raw.append({
                        'target_root': b.target_root,
                        'bridge_concept': b.bridge_concept_es if meaning_lang == 'es' else b.bridge_concept_en,
                    })

        roots_data.append({
            'root_translit': rt,
            'root_syriac': root_syriac,
            'gloss': gloss,
            'frequency': info['count'],
            'word_forms': info['word_forms'],
            'hebrew': hebrew,
            'arabic': arabic,
            'bridges': bridges_raw,
        })

    roots_data.sort(key=lambda r: -r['frequency'])

    # Detect inter-root connections
    connections = []
    passage_root_translits = {r['root_translit'] for r in roots_data}
    seen_connections = set()
    for rd in roots_data:
        for b in rd.get('bridges', []):
            target_key = b['target_root']
            target_translit = target_key.upper().replace('A-', "'-", 1) if target_key.startswith('a-') else target_key.upper()
            if target_translit in passage_root_translits:
                conn_key = tuple(sorted([rd['root_translit'], target_translit]))
                if conn_key not in seen_connections:
                    seen_connections.add(conn_key)
                    connections.append({
                        'source': rd['root_translit'],
                        'target': target_translit,
                        'concept': b['bridge_concept'],
                    })

    # Sister roots (2+ shared consonants)
    root_translits = list(passage_root_translits)
    for i in range(len(root_translits)):
        for j in range(i + 1, len(root_translits)):
            r1_parts = root_translits[i].split('-')
            r2_parts = root_translits[j].split('-')
            if len(r1_parts) >= 2 and len(r2_parts) >= 2:
                shared = sum(1 for a, b in zip(r1_parts, r2_parts) if a == b)
                if shared >= 2:
                    conn_key = tuple(sorted([root_translits[i], root_translits[j]]))
                    if conn_key not in seen_connections:
                        seen_connections.add(conn_key)
                        label = ('Raíces hermanas' if meaning_lang == 'es' else 'Sister roots') + \
                                f' ({shared}/{max(len(r1_parts), len(r2_parts))})'
                        connections.append({
                            'source': root_translits[i],
                            'target': root_translits[j],
                            'concept': label,
                            'type': 'sister',
                        })

    book_display = _bn(book, lang)
    ref_display = f"{book_display} {chapter}:{v_start}" if v_start == v_end else f"{book_display} {chapter}:{v_start}-{v_end}"

    return jsonify({
        'reference': ref_display,
        'verses': verses,
        'roots': roots_data,
        'connections': connections,
        'total_roots': len(roots_data),
    })


@app.route('/api/parallel')
def api_parallel():
    """Return parallel texts for a verse across corpora."""
    ref = request.args.get('ref', '').strip()
    lang = _get_lang()
    trans = _get_trans()
    if not ref:
        return jsonify({'error': 'Missing ref parameter'}), 400

    results = []
    for cid in _corpus.get_corpus_ids():
        text = _corpus.get_verse_text(ref, corpus_id=cid)
        if text:
            from aramaic_core.characters import detect_script as ds
            script = ds(text)
            results.append({
                'corpus_id': cid,
                'corpus_label': _corpus.get_corpus_info(cid).label,
                'text': text,
                'script': script,
                'translation': _corpus.get_verse_translation(ref, trans) or '',
            })

    return jsonify({
        'reference': ref,
        'parallels': results,
        'translation_en': _corpus.get_verse_translation(ref, 'en') or '',
        'translation_es': _corpus.get_verse_translation(ref, 'es') or '',
    })


@app.route('/parallel')
def parallel():
    """Synoptic parallel viewer page."""
    lang = _get_lang()
    book = request.args.get('book', 'Genesis')
    chapter = request.args.get('chapter', '1')
    books = _corpus.get_books()
    return render_template('parallel.html', lang=lang, script=_get_script(),
                           trans=_get_trans(), t=_t_proxy, bn=_bn, books=books,
                           book=book, chapter=chapter)


@app.route('/constellation')
def constellation():
    """Passage constellation visualization page."""
    lang = _get_lang()
    book = request.args.get('book', 'Matthew')
    chapter = request.args.get('chapter', '1')
    v_start = request.args.get('v_start', '1')
    v_end = request.args.get('v_end', '5')
    books = _corpus.get_books()
    return render_template('constellation.html', lang=lang, script=_get_script(),
                           trans=_get_trans(), t=_t_proxy, bn=_bn, books=books,
                           book=book, chapter=chapter, v_start=v_start, v_end=v_end)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
