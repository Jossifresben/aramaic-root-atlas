"""
API contract tests: every public /api/* endpoint returns:
  - HTTP 200 on a valid request
  - JSON content type
  - response shape with the documented top-level keys

Failure of any of these is a breaking change for downstream consumers
of the API. These tests are the closest thing to a versioning contract
until /api/v1/... routes exist (Phase 4).
"""

import pytest


# -- Stats / discovery -------------------------------------------------------

def test_api_stats(client):
    r = client.get('/api/stats')
    assert r.status_code == 200
    data = r.get_json()
    # Must include per-corpus stats and totals
    assert 'corpora' in data
    assert 'total_verses' in data
    assert 'total_words' in data
    assert 'root_count' in data
    # Sanity: counts should be in a plausible range
    assert data['total_verses'] > 30000  # ~38,062
    assert data['total_words'] > 400000  # ~528,399
    assert data['root_count'] > 4000     # ~5,000


def test_targum_jonathan_corpus_present(client):
    """Targum Jonathan (Phase 6A) must load as a distinct corpus with the
    expected scale, be filterable, and cross-script-normalize its Hebrew
    roots into the shared root index."""
    # Present in /api/stats with plausible scale (~9,296 verses)
    stats = client.get('/api/stats').get_json()
    by_id = {c['id']: c for c in stats['corpora']}
    assert 'targum_jonathan' in by_id, 'targum_jonathan missing from /api/stats'
    tj = by_id['targum_jonathan']
    assert tj['verses'] > 9000
    assert tj['words'] > 150000

    # SH-L-M (peace) cross-script normalizes from Hebrew שלם and is attested
    root = client.get('/api/roots?q=SH-L-M').get_json()
    attest = root.get('corpus_attestation', {})
    assert attest.get('targum_jonathan', 0) > 0, \
        'SH-L-M not attested in targum_jonathan (cross-script normalization broken)'

    # Filterable
    assert client.get('/browse?corpus=targum_jonathan').status_code == 200


def test_targum_writings_corpus_present(client):
    """Targum Writings (v3.3 corpus expansion) must load as a distinct
    corpus with the expected scale, be filterable, and cross-script-
    normalize its Hebrew roots into the shared root index."""
    # Present in /api/stats with plausible scale (~7,022 verses)
    stats = client.get('/api/stats').get_json()
    by_id = {c['id']: c for c in stats['corpora']}
    assert 'targum_writings' in by_id, 'targum_writings missing from /api/stats'
    tgw = by_id['targum_writings']
    assert tgw['verses'] > 6500
    assert tgw['words'] > 90000

    # SH-L-M (peace) cross-script normalizes from Hebrew שלם and is attested
    root = client.get('/api/roots?q=SH-L-M').get_json()
    attest = root.get('corpus_attestation', {})
    assert attest.get('targum_writings', 0) > 0, \
        'SH-L-M not attested in targum_writings (cross-script normalization broken)'

    # Filterable
    assert client.get('/browse?corpus=targum_writings').status_code == 200


def test_ephrem_works_corpus_present(client):
    """Ephrem — Other Works (v3.3 corpus expansion) must load as a distinct
    corpus with the expected scale, be filterable, and be indexed into the
    shared root index."""
    # Present in /api/stats with plausible scale (~1,330 verses)
    stats = client.get('/api/stats').get_json()
    by_id = {c['id']: c for c in stats['corpora']}
    assert 'ephrem_works' in by_id, 'ephrem_works missing from /api/stats'
    epw = by_id['ephrem_works']
    assert epw['verses'] > 1200
    assert epw['words'] > 70000

    # SH-L-M (peace) is attested
    root = client.get('/api/roots?q=SH-L-M').get_json()
    attest = root.get('corpus_attestation', {})
    assert attest.get('ephrem_works', 0) > 0, \
        'SH-L-M not attested in ephrem_works'

    # Filterable
    assert client.get('/browse?corpus=ephrem_works').status_code == 200


def test_targum_writings_parallel_alignment(client):
    """Targum Writings and Peshitta OT share book names (Psalms, Chronicles,
    etc.), so the parallel viewer must align verses across them for free."""
    r = client.get('/api/parallel?ref=Psalms+23:1')
    assert r.status_code == 200
    data = r.get_json()
    corpora_ids = {p['corpus_id'] for p in data['parallels']}
    assert 'peshitta_ot' in corpora_ids
    assert 'targum_writings' in corpora_ids

    r2 = client.get('/api/parallel?ref=1+Chronicles+1:1')
    assert r2.status_code == 200
    data2 = r2.get_json()
    corpora_ids2 = {p['corpus_id'] for p in data2['parallels']}
    assert 'peshitta_ot' in corpora_ids2
    assert 'targum_writings' in corpora_ids2


def test_diachronic_root_includes_new_corpora(client):
    """/api/diachronic/root must include both v3.3 corpora in its series,
    and CORPUS_CHRONOLOGY must end with targum_writings (its slot per the
    v3.3 spec: appended last, after ephrem_works)."""
    r = client.get('/api/diachronic/root?root=SH-L-M')
    assert r.status_code == 200
    data = r.get_json()
    by_id = {c['corpus_id']: c for c in data['corpora']}
    assert 'targum_writings' in by_id and by_id['targum_writings']['raw_count'] > 0
    assert 'ephrem_works' in by_id and by_id['ephrem_works']['raw_count'] > 0

    # Chronology order: targum_writings is the last entry
    assert data['corpora'][-1]['corpus_id'] == 'targum_writings'


def test_api_books_no_filter(client):
    r = client.get('/api/books')
    assert r.status_code == 200
    data = r.get_json()
    assert 'books' in data
    assert isinstance(data['books'], list)


def test_api_books_with_corpus_filter(client):
    r = client.get('/api/books?corpus=peshitta_nt')
    assert r.status_code == 200
    data = r.get_json()
    assert 'books' in data
    # Books are returned as a flat list of strings; must include at least
    # one NT book like Matthew
    blob = ' '.join(str(b) for b in data['books']).lower()
    assert 'matthew' in blob or 'matthaios' in blob or 'mathew' in blob


# -- Root lookup ------------------------------------------------------------

def test_api_roots_known_root(client):
    r = client.get('/api/roots?q=SH-L-M')
    assert r.status_code == 200
    data = r.get_json()
    assert 'root' in data
    assert 'root_transliteration' in data
    assert 'matches' in data
    assert isinstance(data['matches'], list)


def test_api_roots_unknown_root_does_not_500(client):
    r = client.get('/api/roots?q=X-X-X')
    # Unknown root returns 400 or 404 with a clean error envelope; never 500
    assert r.status_code in (200, 400, 404), \
        f'Unknown root returned {r.status_code}; should be 200/400/404, never 500'
    if r.status_code != 200:
        data = r.get_json()
        assert data is not None and 'error' in data, \
            'Error responses must include an "error" key'


def test_api_root_family(client):
    r = client.get('/api/root-family?root=SH-L-M')
    assert r.status_code == 200
    data = r.get_json()
    # Whatever shape it returns, it must be JSON
    assert data is not None


# -- Search -----------------------------------------------------------------

def test_api_search(client):
    r = client.get('/api/search?q=peace&lang=en')
    assert r.status_code == 200
    data = r.get_json()
    assert 'results' in data
    assert 'count' in data


def test_api_reverse_search(client):
    r = client.get('/api/reverse-search?q=peace&lang=en')
    assert r.status_code == 200
    data = r.get_json()
    assert 'results' in data


def test_api_cognate_lookup(client):
    r = client.get('/api/cognate-lookup?word=shalom')
    assert r.status_code == 200


def test_api_suggest(client):
    r = client.get('/api/suggest?prefix=SH')
    assert r.status_code == 200


# -- Verse / chapter --------------------------------------------------------

def test_api_chapter(client):
    r = client.get('/api/chapter/Genesis/1')
    assert r.status_code == 200
    data = r.get_json()
    assert data is not None


def test_api_verse(client):
    r = client.get('/api/verse?ref=Genesis+1:1')
    assert r.status_code == 200


def test_api_chapter_roots(client):
    r = client.get('/api/chapter-roots?book=Matthew&chapter=5')
    assert r.status_code == 200


def test_api_parallel(client):
    r = client.get('/api/parallel?ref=Genesis+1:1')
    assert r.status_code == 200


# -- Analytical tools -------------------------------------------------------

def test_api_proximity_search(client):
    r = client.get('/api/proximity-search?root1=SH-L-M&root2=K-TH-B&scope=chapter')
    assert r.status_code == 200


def test_api_passage_constellation(client):
    r = client.get('/api/passage-constellation?book=Matthew&chapter=5&v_start=1&v_end=10')
    assert r.status_code == 200


def test_api_heatmap(client):
    r = client.get('/api/heatmap?limit=20')
    assert r.status_code == 200


def test_api_paradigm(client):
    r = client.get('/api/paradigm?root=K-T-B')
    assert r.status_code == 200


def test_api_hapax(client):
    r = client.get('/api/hapax?max_freq=1&scope=root&limit=10')
    assert r.status_code == 200


def test_api_concordance(client):
    r = client.get('/api/concordance?root=SH-L-M&context_words=5&limit=10')
    assert r.status_code == 200


def test_api_concordance_export_csv(client):
    r = client.get('/api/concordance/export?root=SH-L-M&format=csv&limit=5')
    assert r.status_code == 200


def test_api_diachronic_root(client):
    r = client.get('/api/diachronic/root?root=K-T-B')
    assert r.status_code == 200


def test_api_diachronic_shifts(client):
    r = client.get('/api/diachronic/shifts?direction=emerging&limit=10')
    assert r.status_code == 200


def test_api_diachronic_unique(client):
    r = client.get('/api/diachronic/unique?corpus=biblical_aramaic')
    assert r.status_code == 200


def test_api_collocations(client):
    r = client.get('/api/collocations?root=SH-L-M&scope=verse&limit=10')
    assert r.status_code == 200


def test_api_semantic_fields_index(client):
    r = client.get('/api/semantic-fields')
    assert r.status_code == 200
    data = r.get_json()
    assert data is not None


# -- Word morphology --------------------------------------------------------

def test_api_word_parse_syriac(client):
    # Already covered in detail by test_word_parse.py; this is just contract.
    r = client.get('/api/word-parse?word=෈ܠܡ')  # ܫܠܡ
    assert r.status_code == 200


# -- Negative paths ---------------------------------------------------------

def test_api_search_missing_q_returns_400(client):
    r = client.get('/api/search')
    assert r.status_code == 400
