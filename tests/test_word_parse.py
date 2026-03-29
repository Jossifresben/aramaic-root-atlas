def test_word_parse_missing_param_returns_400(client):
    r = client.get('/api/word-parse')
    assert r.status_code == 400
    assert 'error' in r.get_json()


def test_word_parse_empty_param_returns_400(client):
    r = client.get('/api/word-parse?word=')
    assert r.status_code == 400


def test_word_parse_unknown_word_returns_empty_root(client):
    # A nonsense string — no root in the index
    r = client.get('/api/word-parse?word=xyz')
    assert r.status_code == 200
    data = r.get_json()
    assert data['word'] == 'xyz'
    assert data['root'] == ''
    assert data['prefixes'] == []
    assert data['suffixes'] == []
    assert 'gloss_en' in data
    assert 'cognates' in data
    assert 'corpus_attestations' in data


def test_word_parse_response_schema(client):
    # Any Syriac input — even if no root found, shape must match
    r = client.get('/api/word-parse?word=\u072b\u0720\u0721&lang=en')  # ܫܠܡ
    assert r.status_code == 200
    data = r.get_json()
    required_keys = [
        'word', 'script', 'root', 'root_key', 'stem', 'confidence',
        'pos_guess', 'prefixes', 'suffixes',
        'gloss_en', 'gloss_es', 'gloss_he', 'gloss_ar',
        'cognates', 'corpus_attestations',
    ]
    for k in required_keys:
        assert k in data, f'Missing key: {k}'


def test_word_parse_prefix_suffix_structure(client):
    # ܘܫܠܡ = waw-proclitic + root SH-L-M
    r = client.get('/api/word-parse?word=\u0718\u072b\u0720\u0721')  # ܘܫܠܡ
    data = r.get_json()
    assert r.status_code == 200
    for p in data.get('prefixes', []):
        assert 'char' in p, 'Prefix missing char'
        assert 'label' in p, 'Prefix missing label'
        assert isinstance(p['label'], str)
        assert len(p['label']) > 0
    for s in data.get('suffixes', []):
        assert 'char' in s, 'Suffix missing char'
        assert 'label' in s, 'Suffix missing label'


def test_word_parse_lang_param_returns_correct_gloss_key(client):
    r = client.get('/api/word-parse?word=\u072b\u0720\u0721&lang=es')
    data = r.get_json()
    assert r.status_code == 200
    assert 'gloss_es' in data


def test_word_parse_pos_guess_values(client):
    r = client.get('/api/word-parse?word=\u072b\u0720\u0721')
    data = r.get_json()
    assert data['pos_guess'] in ('verb', 'noun', 'unknown')
