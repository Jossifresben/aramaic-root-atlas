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
    transliterate_syriac_to_arabic, normalize_root_to_latin,
    detect_script, transliterate_hebrew,
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
    global _i18n, _cognates_raw, _initialized, _semantic_fields

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

        # Load semantic fields if available
        sf_path = os.path.join(ROOTS_DIR, 'semantic_fields.json')
        if os.path.exists(sf_path):
            with open(sf_path, 'r', encoding='utf-8') as f:
                _semantic_fields = json.load(f)

        _initialized = True


# --- Helper ---
VALID_SCRIPTS = ('latin', 'syriac', 'hebrew', 'arabic')
VALID_TRANS = ('en', 'es', 'he', 'ar', 'el')


def _get_lang() -> str:
    return request.args.get('lang', 'en')


def _get_script() -> str:
    s = request.args.get('script', 'latin')
    return s if s in VALID_SCRIPTS else 'latin'


def _get_trans() -> str:
    t = request.args.get('trans', _get_lang())
    return t if t in VALID_TRANS else _get_lang()


def _pick_gloss(cog, lang_code: str) -> str:
    """Pick the best available gloss from a CognateEntry for the given UI language."""
    if lang_code == 'es':
        return cog.gloss_es or cog.gloss_en or ''
    if lang_code == 'he':
        return cog.gloss_he or cog.gloss_en or ''
    if lang_code == 'ar':
        return cog.gloss_ar or cog.gloss_en or ''
    return cog.gloss_en or ''


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
                    # Transliterate based on user's chosen script setting
                    from aramaic_core.characters import (detect_script,
                        transliterate_hebrew, transliterate_syriac_to_hebrew,
                        transliterate_syriac_to_arabic)
                    user_script = _get_script()
                    text_script = detect_script(text)
                    if text_script == 'hebrew':
                        translit = ' '.join(transliterate_hebrew(w) for w in text.split())
                    elif user_script == 'syriac':
                        translit = text
                    elif user_script == 'hebrew':
                        translit = ' '.join(transliterate_syriac_to_hebrew(w) for w in text.split())
                    elif user_script == 'arabic':
                        translit = ' '.join(transliterate_syriac_to_arabic(w) for w in text.split())
                    else:
                        translit = ' '.join(transliterate_syriac(w) for w in text.split())
                    result.append({
                        'verse': v_num,
                        'reference': ref,
                        'syriac': text,
                        'translit': translit,
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
    from aramaic_core.characters import transliterate_syriac, transliterate_hebrew, detect_script
    for r in results:
        if r.get('syriac'):
            script = detect_script(r['syriac'])
            if script == 'hebrew':
                r['transliteration'] = transliterate_hebrew(r['syriac'])
            else:
                r['transliteration'] = transliterate_syriac(r['syriac'])
    total = len(results)
    # Interleave results from all corpora so "All Corpora" shows a mix
    if not corpus_filter and total > 50:
        from collections import defaultdict
        by_corpus = defaultdict(list)
        for r in results:
            by_corpus[r['corpus_id']].append(r)
        interleaved = []
        max_per = max(len(v) for v in by_corpus.values()) if by_corpus else 0
        for i in range(max_per):
            for cid in sorted(by_corpus.keys()):
                if i < len(by_corpus[cid]):
                    interleaved.append(by_corpus[cid][i])
        results = interleaved
    return jsonify({
        'query': query,
        'count': total,
        'results': results[:100],
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
    script = _get_script()
    verses = _corpus.get_chapter_verses(book, chapter)
    verse_data = []
    for v_num, ref, syriac in verses:
        translation = _corpus.get_verse_translation(ref, trans)
        if not translation and trans != 'en':
            translation = _corpus.get_verse_translation(ref, 'en')
        words = syriac.split() if syriac else []
        from aramaic_core.characters import (detect_script as _ds,
            transliterate_hebrew, transliterate_syriac_to_hebrew,
            transliterate_syriac_to_arabic, transliterate_syriac_academic)
        text_script = _ds(syriac) if syriac else 'syriac'
        if text_script == 'hebrew':
            # Biblical Aramaic in Hebrew square script
            if script == 'syriac':
                translit = syriac  # already in the requested script
            else:
                translit = ' '.join(transliterate_hebrew(w) for w in words)
        else:
            # Syriac script — honour the user's chosen transliteration
            if script == 'syriac':
                translit = syriac
            elif script == 'hebrew':
                translit = ' '.join(transliterate_syriac_to_hebrew(w) for w in words)
            elif script == 'arabic':
                translit = ' '.join(transliterate_syriac_to_arabic(w) for w in words)
            else:
                translit = ' '.join(transliterate_syriac(w) for w in words)
        # Build word-level root data for popover
        word_roots = []
        for w in words:
            result = _extractor.lookup_word_root_with_confidence(w)
            if result:
                root_syr, conf = result
                root_translit = _translit_to_dash(root_syr)
                gloss = _extractor.get_root_gloss(root_syr)
                stem = _extractor.lookup_word_stem(w)
                word_roots.append({
                    'r': root_syr,
                    't': root_translit,
                    'g': gloss,
                    'c': round(conf, 2),
                    's': stem or '',
                })
            else:
                word_roots.append(None)

        verse_data.append({
            'verse': v_num,
            'reference': ref,
            'syriac': syriac,
            'transliteration': translit,
            'translation': translation,
            'corpus_id': _corpus.get_verse_corpus(ref),
            'word_roots': word_roots,
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


@app.route('/bookmarks')
def bookmarks():
    lang = _get_lang()
    book_names = _i18n.get(lang, {}).get('book_names', {})
    return render_template('bookmarks.html', lang=lang, script=_get_script(),
                           trans=_get_trans(), t=_t_proxy, bn=_bn,
                           book_names_json=json.dumps(book_names, ensure_ascii=False))


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


@app.route('/api/interlinear')
def api_interlinear():
    """Word-by-word interlinear data for a passage range.

    Query params:
        book       — book name (required)
        ch_start   — start chapter int (required)
        v_start    — start verse int (default 1)
        ch_end     — end chapter int (default ch_start)
        v_end      — end verse int (default 9999 = last verse)
        corpus     — corpus filter (optional)
        script     — latin|syriac|hebrew|arabic (default latin)
        lang       — en|es|he|ar (default en, controls gloss language)
        trans      — translation track (default = lang)
    """
    _init()
    book = request.args.get('book', '').strip()
    if not book:
        return jsonify({'error': 'Missing book parameter'}), 400

    try:
        ch_start = int(request.args.get('ch_start', 1))
        v_start_param = int(request.args.get('v_start', 1))
        ch_end = int(request.args.get('ch_end', ch_start))
        v_end_param = int(request.args.get('v_end', 9999))
    except ValueError:
        return jsonify({'error': 'Chapter and verse parameters must be integers'}), 400

    corpus_filter = request.args.get('corpus', '') or None
    script = request.args.get('script', 'latin')
    lang = request.args.get('lang', 'en')
    trans = request.args.get('trans', lang)

    verses_out = []
    truncated = False
    total = 0

    for chapter in range(ch_start, ch_end + 1):
        rows = _corpus.get_chapter_verses(book, chapter, corpus_filter)
        for v_num, ref, syriac in rows:
            # Apply verse-range filter at chapter boundaries
            if chapter == ch_start and v_num < v_start_param:
                continue
            if chapter == ch_end and v_num > v_end_param:
                continue
            if total >= 500:
                truncated = True
                break
            total += 1

            words = syriac.split() if syriac else []
            word_data = []
            for w in words:
                # Per-word transliteration honoring the script param
                text_script = detect_script(w)
                if text_script == 'hebrew':
                    if script == 'syriac':
                        t = w  # show square-script word unchanged
                    else:
                        t = transliterate_hebrew(w)
                else:
                    if script == 'syriac':
                        t = w
                    elif script == 'hebrew':
                        t = transliterate_syriac_to_hebrew(w)
                    elif script == 'arabic':
                        t = transliterate_syriac_to_arabic(w)
                    else:
                        t = transliterate_syriac(w)

                # Root, stem, gloss
                result = _extractor.lookup_word_root_with_confidence(w)
                root_translit = ''
                root_key = ''
                gloss = ''
                stem = None
                confidence = 0.0

                if result:
                    root_syr, conf = result
                    confidence = round(conf, 2)
                    root_translit = _translit_to_dash(root_syr)
                    root_key = root_translit.lower()
                    stem = _extractor.lookup_word_stem(w)
                    # Multilingual gloss: prefer cognate entry, fall back to extractor
                    cog = _cognate_lookup.lookup(root_syr) if _cognate_lookup else None
                    if cog:
                        gloss = _pick_gloss(cog, lang)
                    else:
                        gloss = _extractor.get_root_gloss(root_syr) or ''

                word_data.append({
                    'syriac': w,
                    'translit': t,
                    'root': root_translit,
                    'root_key': root_key,
                    'gloss': gloss,
                    'stem': stem,
                    'confidence': confidence,
                })

            translation = _corpus.get_verse_translation(ref, trans) or ''
            if not translation and trans != 'en':
                translation = _corpus.get_verse_translation(ref, 'en') or ''

            verses_out.append({
                'ref': ref,
                'chapter': chapter,
                'verse': v_num,
                'words': word_data,
                'translation': translation,
            })

        if truncated:
            break

    return jsonify({
        'book': book,
        'corpus': corpus_filter or '',
        'verses': verses_out,
        'truncated': truncated,
    })


def _translit_to_dash(syriac_root: str) -> str:
    """Convert a Syriac root to dash-separated uppercase Latin: ܫܠܡ -> SH-L-M"""
    from aramaic_core.characters import SYRIAC_TO_LATIN
    parts = []
    for ch in syriac_root:
        if ch in SYRIAC_TO_LATIN:
            parts.append(SYRIAC_TO_LATIN[ch].upper())
    return '-'.join(parts) if parts else ''


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
    from aramaic_core.characters import detect_script, translit_word_to_syriac, SYRIAC_CONSONANTS

    # Allow Latin transliteration input — silently convert before analysis
    input_word = word
    if detect_script(word) == 'latin':
        converted = translit_word_to_syriac(word)
        if converted:
            word = converted

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
        # Prefer candidates whose stem consonants exactly equal the root (fully stripped).
        # Fall back to candidates where root is a strict subset (partial stripping).
        # Only use the unstripped word as a last resort.
        exact_match = None
        subset_match = None
        for cand in candidates:
            cand_consonants = frozenset(ch for ch in cand.stem if ch in SYRIAC_CONSONANTS)
            if not root_consonants:
                continue
            if cand_consonants == root_consonants:
                # Prefer the exact match with the most affixes stripped
                if exact_match is None or (
                    len(cand.prefixes_removed) + len(cand.suffixes_removed) >
                    len(exact_match.prefixes_removed) + len(exact_match.suffixes_removed)
                ):
                    exact_match = cand
            elif root_consonants < cand_consonants and subset_match is None:
                subset_match = cand
        best = exact_match or subset_match or (candidates[0] if candidates else None)
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
        'input': input_word,
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


@app.route('/parse')
def parse_page():
    """Standalone word parser page."""
    lang = _get_lang()
    initial_word = request.args.get('word', '')
    return render_template('parse.html', lang=lang, script=_get_script(),
                           trans=_get_trans(), t=_t_proxy, bn=_bn,
                           initial_word=initial_word)


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


@app.route('/api/cognate-lookup')
def api_cognate_lookup():
    """Look up Aramaic roots by Hebrew, Arabic, or transliterated cognate word."""
    word = request.args.get('word', '').strip()
    if not word:
        return jsonify({'error': 'Missing word parameter'}), 400

    entries = _cognate_lookup.lookup_by_cognate_word(word)
    if not entries:
        return jsonify({'word': word, 'count': 0, 'results': []})

    results = []
    for entry in entries:
        occ = 0
        root_entry = _extractor.lookup_root(entry.root_syriac)
        if root_entry:
            occ = root_entry.total_occurrences
        results.append({
            'key': _translit_to_dash(entry.root_syriac),
            'root_syriac': entry.root_syriac,
            'gloss': entry.gloss_en,
            'gloss_es': entry.gloss_es,
            'occurrences': occ,
        })

    return jsonify({'word': word, 'count': len(results), 'results': results})


# Reverse search index (meaning → roots)
_reverse_idx: dict = {}


def _tokenize(text: str, min_len: int = 2) -> set:
    """Split text into lowercase word tokens."""
    import re
    return {w for w in re.split(r'[^a-zA-ZáéíóúñüÁÉÍÓÚÑÜ]+', text.lower()) if len(w) >= min_len}


def _build_reverse_index():
    """Build reverse search index: English/Spanish terms → Syriac roots."""
    global _reverse_idx
    if _reverse_idx:
        return
    roots = _cognates_raw.get('roots', {})

    idx = {}
    for lang_code in ('en', 'es'):
        entries = []
        gloss_key = f'gloss_{lang_code}'
        sabor_key = f'sabor_raiz_{lang_code}'
        for key, data in roots.items():
            if not isinstance(data, dict):
                continue
            gloss = data.get(gloss_key, '')
            sabor = data.get(sabor_key, '')
            root_syriac = data.get('root_syriac', '')

            terms = _tokenize(gloss, min_len=2)
            terms |= _tokenize(sabor, min_len=3)
            for cognate_list in (data.get('cognates', {}).get('hebrew', []),
                                 data.get('cognates', {}).get('arabic', []),
                                 data.get('cognates', {}).get('greek', [])):
                for cog in cognate_list:
                    terms |= _tokenize(cog.get(f'meaning_{lang_code}', ''), min_len=3)

            occ = 0
            if root_syriac:
                root_entry = _extractor.lookup_root(root_syriac)
                if root_entry:
                    occ = root_entry.total_occurrences

            entries.append({
                'key': _translit_to_dash(root_syriac) if root_syriac else key.upper(),
                'root_syriac': root_syriac,
                'gloss': gloss,
                'sabor': sabor,
                'terms': terms,
                'occurrences': occ,
            })
        idx[lang_code] = entries

    _reverse_idx.update(idx)


@app.route('/api/reverse-search')
def api_reverse_search():
    """Search Syriac roots by English/Spanish meaning."""
    _build_reverse_index()

    query = request.args.get('q', '').strip().lower()
    lang = request.args.get('lang', 'en')
    if lang not in ('en', 'es'):
        lang = 'en'

    if not query or len(query) < 2:
        return jsonify({'query': query, 'total': 0, 'results': []})

    query_words = query.split()
    entries = _reverse_idx.get(lang, [])

    scored = []
    for e in entries:
        score = 0
        if query == e['gloss'].lower():
            score += 100
        elif query in e['gloss'].lower():
            score += 50
        matched_words = 0
        for qw in query_words:
            for term in e['terms']:
                if qw == term:
                    matched_words += 3
                    break
                elif qw in term or term.startswith(qw):
                    matched_words += 1
                    break
        if matched_words:
            score += matched_words * 10
        if e['sabor'] and query in e['sabor'].lower():
            score += 5
        if score > 0:
            scored.append((score, e))

    scored.sort(key=lambda x: (-x[0], -x[1]['occurrences']))

    results = []
    for score, e in scored[:30]:
        results.append({
            'key': e['key'],
            'root_syriac': e['root_syriac'],
            'gloss': e['gloss'],
            'sabor': e['sabor'],
            'occurrences': e['occurrences'],
            'score': score,
        })

    return jsonify({'query': query, 'total': len(results), 'results': results})


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

    # Only include books that exist in 2+ corpora
    book_corpora = {}  # book_name -> set of corpus_ids
    for cid in _corpus.get_corpus_ids():
        for b_name, b_ch in _corpus.get_books(cid):
            if b_name not in book_corpora:
                book_corpora[b_name] = {'chapters': b_ch, 'corpora': set()}
            book_corpora[b_name]['corpora'].add(cid)
            book_corpora[b_name]['chapters'] = max(book_corpora[b_name]['chapters'], b_ch)

    parallel_books = [(name, info['chapters']) for name, info in book_corpora.items()
                      if len(info['corpora']) >= 2]

    if book not in book_corpora or len(book_corpora.get(book, {}).get('corpora', set())) < 2:
        book = parallel_books[0][0] if parallel_books else 'Genesis'

    return render_template('parallel.html', lang=lang, script=_get_script(),
                           trans=_get_trans(), t=_t_proxy, bn=_bn, books=parallel_books,
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


@app.route('/api/chapter-roots')
def api_chapter_roots():
    """Return all roots found in a chapter, sorted by frequency."""
    book = request.args.get('book', '')
    chapter = request.args.get('chapter', 1, type=int)
    if not book:
        return jsonify({'error': 'Missing book parameter'}), 400

    verses = _corpus.get_chapter_verses(book, chapter)
    root_counts: dict[str, dict] = {}  # root_syriac -> {count, forms, gloss, translit, conf_sum}

    for v_num, ref, syriac in verses:
        if not syriac:
            continue
        for word in syriac.split():
            result = _extractor.lookup_word_root_with_confidence(word)
            if not result:
                continue
            root_syr, conf = result
            if root_syr not in root_counts:
                gloss = _extractor.get_root_gloss(root_syr)
                root_counts[root_syr] = {
                    'root': root_syr,
                    'translit': _translit_to_dash(root_syr),
                    'gloss': gloss,
                    'count': 0,
                    'forms': set(),
                    'conf_sum': 0.0,
                }
            root_counts[root_syr]['count'] += 1
            root_counts[root_syr]['forms'].add(word)
            root_counts[root_syr]['conf_sum'] += conf

    # Convert sets to lists, compute avg confidence
    rows = []
    for rc in root_counts.values():
        avg_conf = rc['conf_sum'] / rc['count'] if rc['count'] > 0 else 0
        rows.append({
            'root': rc['root'],
            'translit': rc['translit'],
            'gloss': rc['gloss'],
            'count': rc['count'],
            'forms': sorted(rc['forms']),
            'confidence': round(avg_conf, 2),
        })

    rows.sort(key=lambda x: x['count'], reverse=True)

    return jsonify({
        'book': book,
        'chapter': chapter,
        'total_roots': len(rows),
        'roots': rows,
    })


@app.route('/api/heatmap')
def api_heatmap():
    """Return root frequency across corpora for heat map display."""
    limit = request.args.get('limit', 100, type=int)
    sort = request.args.get('sort', 'total')  # total, root, or corpus_id

    corpus_ids = _corpus.get_corpus_ids()
    roots = _extractor.get_all_roots()

    rows = []
    for entry in roots:
        corpus_counts = {}
        for m in entry.matches:
            for ref in m.references:
                cid = _corpus.get_verse_corpus(ref)
                corpus_counts[cid] = corpus_counts.get(cid, 0) + 1

        if len(corpus_counts) < 1:
            continue

        cognate = _cognate_lookup.lookup(entry.root)
        gloss = ''
        if cognate:
            gloss = cognate.gloss_en
        if not gloss:
            gloss = _extractor.get_root_gloss(entry.root)

        row = {
            'root': entry.root,
            'root_translit': _translit_to_dash(entry.root),
            'gloss': gloss,
            'total': entry.total_occurrences,
        }
        for cid in corpus_ids:
            row[cid] = corpus_counts.get(cid, 0)
        rows.append(row)

    # Sort
    if sort == 'root':
        rows.sort(key=lambda r: r['root_translit'])
    elif sort in corpus_ids:
        rows.sort(key=lambda r: r.get(sort, 0), reverse=True)
    else:
        rows.sort(key=lambda r: r['total'], reverse=True)

    return jsonify({
        'corpora': corpus_ids,
        'roots': rows if limit == 0 else rows[:limit],
        'total_roots': len(rows),
    })


@app.route('/heatmap')
def heatmap():
    """Root frequency heat map page."""
    lang = _get_lang()
    return render_template('heatmap.html', lang=lang, script=_get_script(),
                           trans=_get_trans(), t=_t_proxy, bn=_bn)


@app.route('/visualize/<root_key>')
def visualize(root_key):
    """Root family visualizer page."""
    lang = _get_lang()
    script = _get_script()
    trans = _get_trans()
    display_key = root_key.upper()
    if display_key.startswith('A-'):
        display_key = "'" + display_key[1:]
    return render_template('visualize.html', lang=lang, script=script,
                           trans=trans, t=_t_proxy, bn=_bn,
                           root_key=display_key)


@app.route('/api/root-family')
def api_root_family():
    """Return full root family data for the visualizer."""
    _init()
    root_input = request.args.get('root', '').strip()
    lang = _get_lang()
    script = _get_script()
    translit_fn = _get_translit_fn(script)
    trans = _get_trans()
    meaning_lang = trans if trans in ('es', 'en') else lang

    if not root_input:
        return jsonify({'error': 'Missing root parameter'}), 400

    root_syriac = parse_root_input(root_input)
    if root_syriac is None:
        return jsonify({'error': 'Invalid root'}), 400

    root_entry = _extractor.lookup_root(root_syriac)
    cognate_entry = _cognate_lookup.lookup(root_syriac)

    # Semitic sound correspondence fallback
    if not root_entry and not cognate_entry:
        for variant in semitic_root_variants(root_syriac):
            v_root = _extractor.lookup_root(variant)
            v_cognate = _cognate_lookup.lookup(variant)
            if v_root or v_cognate:
                root_syriac = variant
                root_entry = v_root
                cognate_entry = v_cognate
                break

    gloss = ''
    if cognate_entry:
        gloss = cognate_entry.gloss_es if meaning_lang == 'es' else cognate_entry.gloss_en
    if not gloss:
        gloss = _extractor.get_root_gloss(root_syriac)

    # Syriac word forms — filter proclitics
    PROCLITICS = {'\u0718', '\u0715', '\u0712', '\u0720'}
    COMPOUND_PROCLITICS = {
        '\u0718\u0712', '\u0718\u0720', '\u0718\u0721', '\u0718\u0715',
        '\u0715\u0712', '\u0715\u0720', '\u0715\u0721', '\u0720\u0721',
    }
    syriac_words = []
    seen_meanings = set()
    if root_entry:
        for m in root_entry.matches:
            has_proclitic = False
            if len(m.form) > 1:
                if m.form[:2] in COMPOUND_PROCLITICS:
                    has_proclitic = True
                elif m.form[0] in PROCLITICS:
                    has_proclitic = True
            if has_proclitic:
                continue

            meaning = _glosser.gloss(m.form, root_syriac, meaning_lang)
            if meaning and meaning in seen_meanings:
                continue
            if meaning:
                seen_meanings.add(meaning)

            translit_display = m.transliteration if script == 'latin' else translit_fn(m.form)
            # Corpus breakdown for this form
            corpus_counts = {}
            for ref in m.references:
                cid = _corpus.get_verse_corpus(ref)
                corpus_counts[cid] = corpus_counts.get(cid, 0) + 1

            syriac_words.append({
                'word': m.form,
                'translit': translit_display,
                'meaning': meaning,
                'references': m.references[:5],
                'count': m.count,
                'corpus_counts': corpus_counts,
                'stem': _extractor.lookup_word_stem(m.form) or '',
            })

    # Cognates
    hebrew = []
    arabic = []
    if cognate_entry:
        for hw in cognate_entry.hebrew:
            h = {
                'word': hw.word,
                'translit': hw.transliteration,
                'meaning': hw.meaning_es if meaning_lang == 'es' else hw.meaning_en,
            }
            if hw.outlier:
                h['outlier'] = True
            hebrew.append(h)
        for aw in cognate_entry.arabic:
            a = {
                'word': aw.word,
                'translit': aw.transliteration,
                'meaning': aw.meaning_es if meaning_lang == 'es' else aw.meaning_en,
            }
            if aw.outlier:
                a['outlier'] = True
            arabic.append(a)

    # Greek cognates (from raw cognates JSON, not CognateLookup dataclass)
    greek = []
    if cognate_entry:
        # Try both key formats: dashed (sh-l-m) and undashed (shlm/shlm')
        root_key_dashed = _translit_to_dash(root_syriac).lower()
        root_key_plain = transliterate_syriac(root_syriac)
        raw = _cognates_raw.get(root_key_plain) or _cognates_raw.get(root_key_dashed) or _cognates_raw.get('roots', {}).get(root_key_dashed, {})
        if isinstance(raw, dict):
            for gw in raw.get('cognates', {}).get('greek', []):
                greek.append({
                    'word': gw.get('word', ''),
                    'translit': gw.get('transliteration', ''),
                    'meaning': gw.get('meaning_es', gw.get('meaning_en', '')) if meaning_lang == 'es' else gw.get('meaning_en', ''),
                })

    # Semantic bridges
    bridges = []
    if cognate_entry and cognate_entry.semantic_bridges:
        for b in cognate_entry.semantic_bridges:
            bridges.append({
                'outlier_key': b.outlier_key,
                'target_root': b.target_root,
                'relationship': b.relationship,
                'bridge_concept': b.bridge_concept_es if meaning_lang == 'es' else b.bridge_concept_en,
            })

    # Paradigmatic citation
    paradigmatic_ref = ''
    paradigmatic_verse = ''
    paradigmatic_syriac = ''
    paradigmatic_translit = ''
    paradigmatic_form = ''
    override_ref = cognate_entry.paradigmatic_ref_override if cognate_entry else ''

    if root_entry and root_entry.matches:
        best_match = max(root_entry.matches, key=lambda m: m.count)
        paradigmatic_form = best_match.form
        if override_ref:
            paradigmatic_ref = override_ref
        elif best_match.references:
            paradigmatic_ref = best_match.references[0]
        if paradigmatic_ref:
            verse_text = _corpus.get_verse_translation(paradigmatic_ref, trans)
            if not verse_text and trans != 'en':
                verse_text = _corpus.get_verse_translation(paradigmatic_ref, 'en')
            if verse_text:
                paradigmatic_verse = verse_text
            syriac_text = _corpus.get_verse_text(paradigmatic_ref)
            if syriac_text:
                paradigmatic_syriac = syriac_text
                words = syriac_text.split()
                # Use Latin transliteration for the key verse (script=syriac means identity, which is wrong here)
                latin_fn = _get_translit_fn(script) if script != 'syriac' else transliterate_syriac
                paradigmatic_translit = ' '.join(latin_fn(w) for w in words)

    # Sister roots
    sister_roots = []
    root_parts = root_input.lower().split('-')
    if len(root_parts) == 3:
        all_keys = _cognate_lookup.get_all_keys()
        for other_key in all_keys:
            if other_key == root_input.lower():
                continue
            other_parts = other_key.split('-')
            if len(other_parts) == 3:
                shared = sum(1 for a, b in zip(root_parts, other_parts) if a == b)
                if shared >= 2:
                    other_entry = _cognate_lookup.lookup_by_key(other_key)
                    other_gloss = ''
                    other_syriac = ''
                    if other_entry:
                        other_gloss = other_entry.gloss_es if meaning_lang == 'es' else other_entry.gloss_en
                        other_syriac = other_entry.root_syriac
                    sister_roots.append({
                        'root_translit': other_key.upper().replace('A-', "'-", 1) if other_key.startswith('a-') else other_key.upper(),
                        'root_syriac': other_syriac,
                        'gloss': other_gloss,
                        'shared': shared,
                    })

    # Cross-corpus attestation
    corpus_attestation = {}
    if root_entry:
        for m in root_entry.matches:
            for ref in m.references:
                cid = _corpus.get_verse_corpus(ref)
                corpus_attestation[cid] = corpus_attestation.get(cid, 0) + 1

    # Stem distribution across all forms
    stem_distribution = {}
    if root_entry:
        for m in root_entry.matches:
            stem = _extractor.lookup_word_stem(m.form)
            if stem:
                stem_distribution[stem] = stem_distribution.get(stem, 0) + m.count

    return jsonify({
        'root': root_syriac,
        'root_translit': _translit_to_dash(root_syriac) if root_syriac else root_input.upper(),
        'gloss': gloss,
        'syriac_words': syriac_words,
        'hebrew': hebrew,
        'arabic': arabic,
        'greek': greek,
        'semantic_bridges': bridges,
        'paradigmatic_ref': paradigmatic_ref,
        'paradigmatic_verse': paradigmatic_verse,
        'paradigmatic_syriac': paradigmatic_syriac,
        'paradigmatic_translit': paradigmatic_translit,
        'paradigmatic_form': paradigmatic_form,
        'paradigmatic_form_translit': ((_get_translit_fn(script) if script != 'syriac' else transliterate_syriac)(paradigmatic_form)) if paradigmatic_form else '',
        'sister_roots': sister_roots,
        'corpus_attestation': corpus_attestation,
        'stem_distribution': stem_distribution,
    })


@app.route('/api/paradigm')
def api_paradigm():
    """Return forms grouped by verb stem for a root."""
    _init()
    root_input = request.args.get('root', '').strip()
    if not root_input:
        return jsonify({'error': 'Missing root parameter'}), 400
    root_syriac = parse_root_input(root_input)
    if root_syriac is None:
        return jsonify({'error': 'Invalid root'}), 400

    root_entry = _extractor.lookup_root(root_syriac)
    if not root_entry:
        return jsonify({'root': root_input, 'stems': {}}), 200

    stems: dict[str, list[dict]] = {}
    for m in root_entry.matches:
        stem = _extractor.lookup_word_stem(m.form) or 'Unknown'
        if stem not in stems:
            stems[stem] = []
        stems[stem].append({
            'form': m.form,
            'transliteration': m.transliteration,
            'count': m.count,
            'references': m.references[:5],
        })

    # Sort each stem's forms by frequency
    for stem in stems:
        stems[stem].sort(key=lambda x: x['count'], reverse=True)

    return jsonify({
        'root': root_syriac,
        'root_translit': _translit_to_dash(root_syriac),
        'stems': stems,
    })


# ---------------------------------------------------------------------------
# Phase 2: Hapax Legomena
# ---------------------------------------------------------------------------

@app.route('/hapax')
def hapax_page():
    """Hapax legomena finder page."""
    lang = _get_lang()
    return render_template('hapax.html', lang=lang, script=_get_script(),
                           trans=_get_trans(), t=_t_proxy, bn=_bn)


@app.route('/api/hapax')
def api_hapax():
    """Return roots/forms with occurrence count <= max_freq."""
    _init()
    try:
        max_freq = int(request.args.get('max_freq', 1))
    except ValueError:
        return jsonify({'error': 'max_freq must be an integer'}), 400
    max_freq = max(1, min(max_freq, 10))
    corpus_filter = request.args.get('corpus', '').strip() or None
    scope = request.args.get('scope', 'root')  # 'root' or 'form'
    sort = request.args.get('sort', 'alpha')   # 'alpha', 'confidence', 'corpus'
    try:
        limit = int(request.args.get('limit', 500))
    except ValueError:
        return jsonify({'error': 'limit must be an integer'}), 400

    results = []
    for root_entry in _extractor.get_all_roots():
        root_syr = root_entry.root
        gloss = _extractor.get_root_gloss(root_syr)
        cognate = _cognate_lookup.lookup(root_syr)
        if cognate and not gloss:
            gloss = cognate.gloss_en

        if scope == 'form':
            # Count per surface form
            for m in root_entry.matches:
                if corpus_filter:
                    count = sum(1 for ref in m.references
                                if _corpus.get_verse_corpus(ref) == corpus_filter)
                else:
                    count = m.count
                if 0 < count <= max_freq:
                    conf = _extractor.lookup_word_confidence(m.form) or 0.5
                    corpus_att = {}
                    for ref in m.references:
                        cid = _corpus.get_verse_corpus(ref)
                        corpus_att[cid] = corpus_att.get(cid, 0) + 1
                    results.append({
                        'root': root_syr,
                        'root_translit': _translit_to_dash(root_syr),
                        'gloss': gloss,
                        'form': m.form,
                        'form_translit': m.transliteration,
                        'count': count,
                        'references': m.references[:3],
                        'corpus_attestation': corpus_att,
                        'confidence': round(conf, 2),
                    })
        else:
            # Count per root
            if corpus_filter:
                count = sum(
                    sum(1 for ref in m.references
                        if _corpus.get_verse_corpus(ref) == corpus_filter)
                    for m in root_entry.matches
                )
            else:
                count = root_entry.total_occurrences
            if 0 < count <= max_freq:
                corpus_att = {}
                all_refs = []
                for m in root_entry.matches:
                    for ref in m.references:
                        cid = _corpus.get_verse_corpus(ref)
                        corpus_att[cid] = corpus_att.get(cid, 0) + 1
                        all_refs.append(ref)
                # Best confidence across all forms
                confs = [_extractor.lookup_word_confidence(m.form) or 0.5
                         for m in root_entry.matches]
                best_conf = max(confs) if confs else 0.5
                best_form = root_entry.matches[0] if root_entry.matches else None
                results.append({
                    'root': root_syr,
                    'root_translit': _translit_to_dash(root_syr),
                    'gloss': gloss,
                    'form': best_form.form if best_form else '',
                    'form_translit': best_form.transliteration if best_form else '',
                    'count': count,
                    'references': all_refs[:3],
                    'corpus_attestation': corpus_att,
                    'confidence': round(best_conf, 2),
                    'forms': [{'form': m.form, 'translit': m.transliteration, 'count': m.count}
                              for m in root_entry.matches[:5]],
                })

    if sort == 'confidence':
        results.sort(key=lambda x: x['confidence'], reverse=True)
    elif sort == 'corpus':
        corpus_order = {cid: i for i, (cid, _, _) in enumerate(CORPUS_CHRONOLOGY)}
        results.sort(key=lambda x: min(
            (corpus_order.get(c, 99) for c in x['corpus_attestation']), default=99
        ))
    else:  # alpha
        results.sort(key=lambda x: x['root_translit'])

    return jsonify({
        'max_freq': max_freq,
        'corpus': corpus_filter or 'all',
        'scope': scope,
        'total': len(results),
        'results': results[:limit],
    })


# ---------------------------------------------------------------------------
# Phase 3: KWIC Concordance
# ---------------------------------------------------------------------------

@app.route('/concordance')
def concordance_page():
    """KWIC concordance page."""
    lang = _get_lang()
    root = request.args.get('root', '')
    return render_template('concordance.html', lang=lang, script=_get_script(),
                           trans=_get_trans(), t=_t_proxy, bn=_bn,
                           initial_root=root)


@app.route('/api/concordance')
def api_concordance():
    """Return KWIC concordance lines for a root."""
    _init()
    root_input = request.args.get('root', '').strip()
    if not root_input:
        return jsonify({'error': 'Missing root parameter'}), 400
    root_syriac = parse_root_input(root_input)
    if root_syriac is None:
        return jsonify({'error': 'Invalid root'}), 400

    corpus_filter = request.args.get('corpus', '').strip() or None
    sort = request.args.get('sort', 'book')       # 'book', 'frequency', 'form'
    group_by = request.args.get('group_by', 'none')  # 'form' or 'none'
    try:
        context_words = int(request.args.get('context_words', 5))
    except ValueError:
        return jsonify({'error': 'context_words must be an integer'}), 400
    context_words = max(2, min(context_words, 15))
    try:
        limit = int(request.args.get('limit', 500))
    except ValueError:
        return jsonify({'error': 'limit must be an integer'}), 400
    trans = _get_trans()
    lang = _get_lang()

    root_entry = _extractor.lookup_root(root_syriac)
    if not root_entry:
        return jsonify({'root': root_input, 'lines': [], 'total': 0}), 200

    lines = []
    for m in root_entry.matches:
        for ref in m.references:
            if corpus_filter and _corpus.get_verse_corpus(ref) != corpus_filter:
                continue
            verse_text = _corpus.get_verse_text(ref)
            if not verse_text:
                continue
            words = verse_text.split()
            # Find keyword position (first occurrence of this form)
            try:
                idx = words.index(m.form)
            except ValueError:
                # Try partial match (proclitic-stripped form)
                idx = next((i for i, w in enumerate(words) if m.form in w), None)
                if idx is None:
                    continue

            left = words[max(0, idx - context_words):idx]
            right = words[idx + 1:idx + 1 + context_words]
            translation = _corpus.get_verse_translation(ref, trans) or \
                          _corpus.get_verse_translation(ref, lang) or ''

            lines.append({
                'reference': ref,
                'left_context': left,
                'keyword': words[idx],
                'right_context': right,
                'translation': translation,
                'corpus_id': _corpus.get_verse_corpus(ref),
                'form': m.form,
                'form_translit': m.transliteration,
                'stem': _extractor.lookup_word_stem(m.form) or '',
            })
            if len(lines) >= limit:
                break
        if len(lines) >= limit:
            break

    if sort == 'frequency':
        form_counts = {m.form: m.count for m in root_entry.matches}
        lines.sort(key=lambda x: form_counts.get(x['form'], 0), reverse=True)
    elif sort == 'form':
        lines.sort(key=lambda x: x['form'])
    # Default 'book' order is natural corpus order

    # Form breakdown summary
    form_summary = {}
    for line in lines:
        f = line['form']
        form_summary[f] = form_summary.get(f, 0) + 1

    return jsonify({
        'root': root_syriac,
        'root_translit': _translit_to_dash(root_syriac),
        'total': len(lines),
        'group_by': group_by,
        'form_summary': form_summary,
        'lines': lines,
    })


@app.route('/api/concordance/export')
def api_concordance_export():
    """Export concordance as TEI XML."""
    _init()
    root_input = request.args.get('root', '').strip()
    if not root_input:
        return 'Missing root parameter', 400
    root_syriac = parse_root_input(root_input)
    if root_syriac is None:
        return 'Invalid root', 400

    corpus_filter = request.args.get('corpus', '').strip() or None
    context_words = int(request.args.get('context_words', 5))
    trans = _get_trans()
    lang = _get_lang()

    root_entry = _extractor.lookup_root(root_syriac)
    root_translit = _translit_to_dash(root_syriac) if root_syriac else root_input.upper()
    gloss = _extractor.get_root_gloss(root_syriac)

    lines = []
    if root_entry:
        for m in root_entry.matches:
            for ref in m.references:
                if corpus_filter and _corpus.get_verse_corpus(ref) != corpus_filter:
                    continue
                verse_text = _corpus.get_verse_text(ref)
                if not verse_text:
                    continue
                words = verse_text.split()
                try:
                    idx = words.index(m.form)
                except ValueError:
                    idx = next((i for i, w in enumerate(words) if m.form in w), None)
                    if idx is None:
                        continue
                left = ' '.join(words[max(0, idx - context_words):idx])
                right = ' '.join(words[idx + 1:idx + 1 + context_words])
                translation = _corpus.get_verse_translation(ref, trans) or \
                              _corpus.get_verse_translation(ref, lang) or ''
                lines.append((ref, left, words[idx], right, translation))
                if len(lines) >= 1000:
                    break

    # Build TEI XML
    from xml.sax.saxutils import escape as xml_escape
    tei_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<TEI xmlns="http://www.tei-c.org/ns/1.0">',
        '  <teiHeader>',
        f'    <fileDesc><titleStmt><title>Concordance for {xml_escape(root_translit)}</title></titleStmt>',
        f'    <notesStmt><note>Root: {xml_escape(root_translit)} — {xml_escape(gloss)}</note></notesStmt></fileDesc>',
        '  </teiHeader>',
        '  <text><body>',
        f'    <div type="concordance" n="{xml_escape(root_translit)}">',
    ]
    for ref, left, kw, right, transl in lines:
        tei_lines.append(f'      <entry n="{xml_escape(ref)}">')
        tei_lines.append(f'        <cit><quote xml:lang="syc">{xml_escape(left)} <term>{xml_escape(kw)}</term> {xml_escape(right)}</quote>')
        tei_lines.append(f'        <bibl>{xml_escape(ref)}</bibl></cit>')
        if transl:
            tei_lines.append(f'        <cit type="translation"><quote>{xml_escape(transl)}</quote></cit>')
        tei_lines.append('      </entry>')
    tei_lines += ['    </div>', '  </body></text>', '</TEI>']

    tei_xml = '\n'.join(tei_lines)
    filename = f'concordance-{root_translit.lower()}.xml'
    from flask import Response
    return Response(tei_xml, mimetype='application/xml',
                    headers={'Content-Disposition': f'attachment; filename="{filename}"'})


# ---------------------------------------------------------------------------
# Phase 4: Diachronic Analysis
# ---------------------------------------------------------------------------

# Chronological ordering of corpora
CORPUS_CHRONOLOGY = [
    ('biblical_aramaic', 'Biblical Aramaic', '~6th–2nd c. BCE'),
    ('targum_onkelos',   'Targum Onkelos',   '~1st–3rd c. CE'),
    ('peshitta_nt',      'Peshitta NT',      '~2nd–5th c. CE'),
    ('peshitta_ot',      'Peshitta OT',      '~2nd–5th c. CE'),
]


@app.route('/diachronic')
def diachronic_page():
    """Diachronic root usage analysis page."""
    lang = _get_lang()
    root = request.args.get('root', '')
    return render_template('diachronic.html', lang=lang, script=_get_script(),
                           trans=_get_trans(), t=_t_proxy, bn=_bn,
                           initial_root=root)


@app.route('/api/diachronic/root')
def api_diachronic_root():
    """Return per-corpus frequency data for a root in chronological order."""
    _init()
    root_input = request.args.get('root', '').strip()
    if not root_input:
        return jsonify({'error': 'Missing root parameter'}), 400
    root_syriac = parse_root_input(root_input)
    if root_syriac is None:
        return jsonify({'error': 'Invalid root'}), 400

    trans = request.args.get('trans', 'en')
    root_entry = _extractor.lookup_root(root_syriac)
    gloss = _extractor.get_root_gloss(root_syriac)
    cognate = _cognate_lookup.lookup(root_syriac)
    if cognate and not gloss:
        gloss = (cognate.gloss_es if trans == 'es' else cognate.gloss_en) or cognate.gloss_en

    # Build per-corpus data from root entry
    corpus_forms: dict[str, list[str]] = {}
    corpus_stems: dict[str, dict[str, int]] = {}
    if root_entry:
        # Use pre-computed corpus_counts from build_index for raw counts
        for m in root_entry.matches:
            stem = _extractor.lookup_word_stem(m.form)
            for ref in m.references:
                cid = _corpus.get_verse_corpus(ref)
                if not cid:
                    continue
                if cid not in corpus_forms:
                    corpus_forms[cid] = []
                if m.form not in corpus_forms[cid]:
                    corpus_forms[cid].append(m.form)
                if stem:
                    if cid not in corpus_stems:
                        corpus_stems[cid] = {}
                    corpus_stems[cid][stem] = corpus_stems[cid].get(stem, 0) + 1
    corpus_counts = root_entry.corpus_counts if root_entry else {}

    data = []
    for cid, label, period in CORPUS_CHRONOLOGY:
        total_words = _corpus.total_words(cid)
        raw = corpus_counts.get(cid, 0)
        normalized = round((raw / total_words) * 1000, 4) if total_words else 0
        data.append({
            'corpus_id': cid,
            'label': label,
            'period': period,
            'raw_count': raw,
            'total_words': total_words,
            'normalized': normalized,
            'forms': corpus_forms.get(cid, [])[:10],
            'stem_distribution': corpus_stems.get(cid, {}),
        })

    return jsonify({
        'root': root_syriac,
        'root_translit': _translit_to_dash(root_syriac),
        'gloss': gloss,
        'corpora': data,
    })


@app.route('/api/diachronic/shifts')
def api_diachronic_shifts():
    """Return roots with the biggest frequency shifts across corpora."""
    _init()
    try:
        limit = int(request.args.get('limit', 50))
    except ValueError:
        return jsonify({'error': 'limit must be an integer'}), 400
    direction = request.args.get('direction', 'all')  # 'emerging', 'declining', 'all'
    trans = request.args.get('trans', 'en')
    try:
        min_occurrences = int(request.args.get('min_occurrences', 3))
    except ValueError:
        return jsonify({'error': 'min_occurrences must be an integer'}), 400

    # Pre-compute total words per corpus
    corpus_totals = {cid: _corpus.total_words(cid) for cid, _, _ in CORPUS_CHRONOLOGY}

    results = []
    for root_entry in _extractor.get_all_roots():
        if root_entry.total_occurrences < min_occurrences:
            continue
        root_syr = root_entry.root

        # Use pre-computed per-corpus counts from build_index
        counts = {cid: root_entry.corpus_counts.get(cid, 0) for cid, _, _ in CORPUS_CHRONOLOGY}

        # Normalized frequencies
        freqs = []
        for cid, _, _ in CORPUS_CHRONOLOGY:
            total = corpus_totals.get(cid, 0)
            freqs.append((counts[cid] / total * 1000) if total else 0)

        nonzero = [f for f in freqs if f > 0]
        if len(nonzero) < 2:
            continue

        magnitude = max(nonzero) / min(nonzero) if min(nonzero) > 0 else 0
        # Direction: compare first attested to last attested
        first_idx = next((i for i, f in enumerate(freqs) if f > 0), None)
        last_idx = next((i for i, f in enumerate(reversed(freqs)) if f > 0), None)
        if first_idx is None or last_idx is None:
            continue
        last_idx = len(freqs) - 1 - last_idx
        dir_label = 'emerging' if freqs[last_idx] > freqs[first_idx] else 'declining'

        if direction != 'all' and dir_label != direction:
            continue

        gloss = _extractor.get_root_gloss(root_syr)
        cognate = _cognate_lookup.lookup(root_syr)
        if cognate and not gloss:
            gloss = (cognate.gloss_es if trans == 'es' else cognate.gloss_en) or cognate.gloss_en

        results.append({
            'root': root_syr,
            'root_translit': _translit_to_dash(root_syr),
            'gloss': gloss,
            'freqs': freqs,
            'magnitude': round(magnitude, 2),
            'direction': dir_label,
        })

    results.sort(key=lambda x: x['magnitude'], reverse=True)
    return jsonify({
        'direction': direction,
        'min_occurrences': min_occurrences,
        'total': len(results),
        'corpora': [{'id': cid, 'label': lbl, 'period': per}
                    for cid, lbl, per in CORPUS_CHRONOLOGY],
        'results': results[:limit],
    })


@app.route('/api/diachronic/unique')
def api_diachronic_unique():
    """Return roots attested in only one corpus."""
    _init()
    corpus_filter = request.args.get('corpus', '').strip() or None
    trans = request.args.get('trans', 'en')

    results = []
    for root_entry in _extractor.get_all_roots():
        root_syr = root_entry.root
        attested = set()
        for m in root_entry.matches:
            for ref in m.references:
                cid = _corpus.get_verse_corpus(ref)
                attested.add(cid)

        if len(attested) == 1:
            only_corpus = list(attested)[0]
            if corpus_filter and only_corpus != corpus_filter:
                continue
            gloss = _extractor.get_root_gloss(root_syr)
            cognate = _cognate_lookup.lookup(root_syr)
            if cognate and not gloss:
                gloss = (cognate.gloss_es if trans == 'es' else cognate.gloss_en) or cognate.gloss_en
            results.append({
                'root': root_syr,
                'root_translit': _translit_to_dash(root_syr),
                'gloss': gloss,
                'corpus': only_corpus,
                'count': root_entry.total_occurrences,
            })

    results.sort(key=lambda x: x['root_translit'])
    return jsonify({
        'corpus_filter': corpus_filter or 'all',
        'total': len(results),
        'results': results,
    })


_coll_ref_cache: dict = {}
_semantic_fields: dict = {}


@app.route('/api/collocations')
def api_collocations():
    """PMI-scored collocations for a target root."""
    _init()
    import math
    root_input = request.args.get('root', '').strip()
    if not root_input:
        return jsonify({'error': 'root parameter required'}), 400
    scope = request.args.get('scope', 'verse')  # 'verse' or 'chapter'
    corpus_filter = request.args.get('corpus', '').strip() or None
    try:
        min_count = int(request.args.get('min_count', 3))
    except ValueError:
        min_count = 3
    try:
        limit = int(request.args.get('limit', 50))
    except ValueError:
        limit = 50

    # Normalise root input
    root_syriac = parse_root_input(root_input)
    if not root_syriac:
        return jsonify({'error': 'Could not parse root: ' + root_input}), 400

    target_entry = _extractor.lookup_root(root_syriac)
    if not target_entry:
        for v in semitic_root_variants(root_syriac):
            target_entry = _extractor.lookup_root(v)
            if target_entry:
                root_syriac = v
                break
    if not target_entry:
        return jsonify({'error': 'Root not found', 'root': root_input}), 404

    def _ref_key(ref: str) -> str:
        if scope == 'chapter':
            parts = ref.rsplit(':', 1)
            return parts[0] if len(parts) == 2 else ref
        return ref

    def _build_refs(entry) -> set:
        refs = set()
        for m in entry.matches:
            for ref in m.references:
                if corpus_filter and _corpus.get_verse_corpus(ref) != corpus_filter:
                    continue
                refs.add(_ref_key(ref))
        return refs

    # Cache total ref universe
    cache_key = (scope, corpus_filter or '')
    if cache_key not in _coll_ref_cache:
        total = set()
        for re_ in _extractor.get_all_roots():
            for m in re_.matches:
                for ref in m.references:
                    if corpus_filter and _corpus.get_verse_corpus(ref) != corpus_filter:
                        continue
                    total.add(_ref_key(ref))
        _coll_ref_cache[cache_key] = total
    total_refs = _coll_ref_cache[cache_key]
    N = len(total_refs)
    if N == 0:
        return jsonify({'root': root_input, 'collocates': []})

    target_refs = _build_refs(target_entry)
    target_n = len(target_refs)
    if target_n == 0:
        return jsonify({'root': root_input, 'collocates': []})

    lang_code = request.args.get('lang', 'en')
    target_translit = _translit_to_dash(root_syriac)
    target_gloss = _extractor.get_root_gloss(root_syriac)
    cognate = _cognate_lookup.lookup(root_syriac)
    if cognate:
        cog_gloss = _pick_gloss(cognate, lang_code)
        if cog_gloss:
            target_gloss = cog_gloss

    results = []
    for other_entry in _extractor.get_all_roots():
        other_syr = other_entry.root
        if other_syr == root_syriac:
            continue
        other_refs = _build_refs(other_entry)
        other_n = len(other_refs)
        if other_n == 0:
            continue
        cooccur = len(target_refs & other_refs)
        if cooccur < min_count:
            continue
        pmi = math.log2((N * cooccur) / (target_n * other_n))
        gloss = _extractor.get_root_gloss(other_syr)
        cog = _cognate_lookup.lookup(other_syr)
        if cog:
            cog_gloss = _pick_gloss(cog, lang_code)
            if cog_gloss:
                gloss = cog_gloss
        # Example reference
        example_ref = ''
        example_text = ''
        for m in other_entry.matches:
            for ref in m.references:
                if _ref_key(ref) in (target_refs & other_refs):
                    example_ref = ref
                    example_text = _corpus.get_verse_text(ref) or ''
                    break
            if example_ref:
                break
        results.append({
            'root': other_syr,
            'root_translit': _translit_to_dash(other_syr),
            'gloss': gloss or '',
            'cooccurrences': cooccur,
            'pmi': round(pmi, 3),
            'example_ref': example_ref,
            'example_text': example_text[:120] if example_text else '',
        })

    results.sort(key=lambda x: -x['pmi'])
    results = results[:limit]

    return jsonify({
        'root': root_input,
        'root_translit': target_translit,
        'root_gloss': target_gloss or '',
        'target_refs': target_n,
        'total_refs': N,
        'scope': scope,
        'corpus_filter': corpus_filter or 'all',
        'collocates': results,
    })


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
        return jsonify({'error': f'No verses found for {book} {ch_start}\u2013{ch_end}'}), 404

    # --- Build corpus-wide root frequency dict for rarity classification ---
    all_root_entries = _extractor.get_all_roots()
    root_total_occ: dict[str, int] = {
        entry.root: entry.total_occurrences
        for entry in all_root_entries
    }
    root_corpus_counts: dict[str, dict[str, int]] = {
        entry.root: entry.corpus_counts
        for entry in all_root_entries
    }

    # --- Aggregate per root within this passage ---
    passage_root_counts: dict[str, int] = {}
    verse_density: list[dict] = []
    total_words = sum(len(text.split()) for _, text in verse_texts)  # all tokens
    analyzed_words = 0  # tokens where a root was resolved
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
            analyzed_words += 1
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
    # lexical_density = unique distinct roots / total tokens (including stopwords)

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
        corpus_att = {
            cid: cnt
            for cid, cnt in root_corpus_counts.get(root_syr, {}).items()
            if cnt > 0
        }
        top_roots.append({
            'root': root_syr,
            'root_key': root_translit,
            'gloss': gloss,
            'passage_count': count,
            'corpus_total': root_total_occ.get(root_syr, 0),
            'corpus_attestation': corpus_att,
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
        'analyzed_word_count': analyzed_words,
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


@app.route('/collocations')
def collocations_page():
    _init()
    lang = _get_lang()
    initial_root = request.args.get('root', '')
    return render_template('collocations.html', lang=lang, trans=_get_trans(), script=_get_script(), t=lambda k, l=None: _t(k, lang),
                           initial_root=initial_root)


@app.route('/interlinear')
def interlinear_page():
    _init()
    lang = _get_lang()
    books = _corpus.get_books()
    return render_template(
        'interlinear.html',
        lang=lang,
        trans=_get_trans(),
        script=_get_script(),
        t=lambda k, l=None: _t(k, lang),
        books=books,
        initial_book=request.args.get('book', ''),
        initial_ch_start=request.args.get('ch_start', ''),
        initial_v_start=request.args.get('v_start', ''),
        initial_ch_end=request.args.get('ch_end', ''),
        initial_v_end=request.args.get('v_end', ''),
    )


@app.route('/annotations')
def annotations_page():
    _init()
    lang = _get_lang()
    return render_template('annotations.html', lang=lang, trans=_get_trans(), script=_get_script(), t=lambda k, l=None: _t(k, lang))


_SEMANTIC_DOMAINS = [
    'creation/cosmos', 'body/anatomy', 'kinship/family', 'speech/communication',
    'motion/travel', 'legal/covenant', 'worship/cultic', 'agriculture/food',
    'war/conflict', 'knowledge/wisdom', 'time', 'emotion/mental',
    'commerce/material', 'nature/elements', 'existence/being',
]


@app.route('/api/semantic-fields')
def api_semantic_fields_list():
    """List all domains with root counts."""
    _init()
    if not _semantic_fields:
        return jsonify({'domains': [], 'no_data': True})
    counts = {}
    for key, fields in _semantic_fields.items():
        for field in fields:
            counts[field] = counts.get(field, 0) + 1
    domains = [{'domain': d, 'count': counts.get(d, 0)} for d in _SEMANTIC_DOMAINS]
    return jsonify({'domains': domains})


@app.route('/api/semantic-fields/<path:field>')
def api_semantic_fields_detail(field: str):
    """Return roots in a domain."""
    _init()
    if not _semantic_fields:
        return jsonify({'field': field, 'roots': [], 'no_data': True})
    lang_code = request.args.get('lang', 'en')
    results = []
    for key, fields in _semantic_fields.items():
        if field not in fields:
            continue
        # Look up root data
        root_syr = None
        for re_ in _extractor.get_all_roots():
            if _translit_to_dash(re_.root).lower() == key:
                root_syr = re_.root
                break
        gloss = ''
        corpus_counts = {}
        total = 0
        if root_syr:
            gloss = _extractor.get_root_gloss(root_syr) or ''
            cog = _cognate_lookup.lookup(root_syr)
            if cog:
                cog_gloss = _pick_gloss(cog, lang_code)
                if cog_gloss:
                    gloss = cog_gloss
            re_entry = _extractor.lookup_root(root_syr)
            if re_entry:
                total = re_entry.total_occurrences
                for m in re_entry.matches:
                    for ref in m.references:
                        cid = _corpus.get_verse_corpus(ref)
                        if cid:
                            corpus_counts[cid] = corpus_counts.get(cid, 0) + 1
        else:
            # Try cognates for gloss
            cog_entry = _cognates_raw.get(key)
            if cog_entry:
                _lang_to_field = {'es': 'gloss_es', 'he': 'gloss_he', 'ar': 'gloss_ar'}
                gloss_field = _lang_to_field.get(lang_code, 'gloss_en')
                gloss = cog_entry.get(gloss_field, '') or cog_entry.get('gloss_en', '')
        if total > 0:
            results.append({
                'key': key,
                'root': root_syr or '',
                'gloss': gloss,
                'total_occurrences': total,
                'corpus_counts': corpus_counts,
            })
    results.sort(key=lambda x: -x['total_occurrences'])
    return jsonify({'field': field, 'count': len(results), 'roots': results})


@app.route('/semantic-fields')
def semantic_fields_page():
    _init()
    lang = _get_lang()
    has_data = bool(_semantic_fields)
    return render_template('semantic_fields.html', lang=lang, trans=_get_trans(), script=_get_script(), t=lambda k, l=None: _t(k, lang),
                           has_data=has_data)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
