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
def _get_lang() -> str:
    return request.args.get('lang', 'en')


def _t(key: str, lang: str | None = None) -> str:
    """Translate a UI string."""
    if lang is None:
        lang = _get_lang()
    return _i18n.get(key, {}).get(lang, key)


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
    return render_template('index.html',
                           lang=lang,
                           t=_t,
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

    result = {
        'root': root_syriac,
        'root_transliteration': entry.root_transliteration,
        'root_academic': transliterate_syriac_academic(root_syriac),
        'total_occurrences': sum(m['count'] for m in matches),
        'matches': matches,
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
    """Return all verses in a chapter."""
    corpus_filter = request.args.get('corpus', None)
    trans = request.args.get('trans', 'en')

    verses = _corpus.get_chapter_verses(book, chapter, corpus_filter)
    result = []
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
    return render_template('browse.html', lang=lang, t=_t,
                           books=books, corpus_filter=corpus_filter)


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
    return render_template('read.html', lang=lang, t=_t,
                           book=book, chapter=chapter,
                           verses=verse_data, books=books, trans=trans)


@app.route('/about')
def about():
    lang = _get_lang()
    return render_template('about.html', lang=lang, t=_t)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
