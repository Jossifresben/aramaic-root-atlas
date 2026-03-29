def test_passage_profile_missing_book_returns_400(client):
    r = client.get('/api/passage-profile?ch_start=1&ch_end=1')
    assert r.status_code == 400
    assert 'error' in r.get_json()


def test_passage_profile_invalid_chapter_returns_400(client):
    r = client.get('/api/passage-profile?book=Matthew&ch_start=notanumber')
    assert r.status_code == 400


def test_passage_profile_nonexistent_book_returns_404(client):
    r = client.get('/api/passage-profile?book=FakeBook&ch_start=1&ch_end=1')
    assert r.status_code == 404


def test_passage_profile_single_chapter_shape(client):
    r = client.get('/api/passage-profile?book=Matthew&ch_start=1&ch_end=1')
    assert r.status_code == 200
    data = r.get_json()
    assert data['verse_count'] > 0
    assert data['word_count'] > 0
    assert data['unique_roots'] > 0
    assert 0.0 < data['lexical_density'] < 1.0
    assert 'hapax_in_passage' in data
    assert 'corpus_hapaxes' in data
    assert set(data['rarity_buckets'].keys()) == {'hapax', 'rare', 'common', 'very_common'}
    assert isinstance(data['stem_distribution'], dict)
    assert isinstance(data['top_roots'], list)
    assert len(data['top_roots']) <= 15
    assert isinstance(data['verse_density'], list)
    assert len(data['verse_density']) == data['verse_count']
    assert set(data['confidence_dist'].keys()) == {'high', 'medium', 'low'}


def test_passage_profile_top_roots_structure(client):
    r = client.get('/api/passage-profile?book=Matthew&ch_start=1&ch_end=1')
    data = r.get_json()
    for entry in data['top_roots']:
        assert 'root' in entry
        assert 'root_key' in entry
        assert 'gloss' in entry
        assert 'passage_count' in entry
        assert 'corpus_total' in entry
        assert entry['passage_count'] >= 1


def test_passage_profile_verse_density_structure(client):
    r = client.get('/api/passage-profile?book=Matthew&ch_start=1&ch_end=1')
    data = r.get_json()
    for entry in data['verse_density']:
        assert 'ref' in entry
        assert 'root_count' in entry
        assert 'unique' in entry


def test_passage_profile_multi_chapter(client):
    r = client.get('/api/passage-profile?book=Matthew&ch_start=5&ch_end=7')
    data = r.get_json()
    assert r.status_code == 200
    assert data['verse_count'] > 50  # Sermon on the Mount is ~109 verses
    assert data['unique_roots'] > 100


def test_passage_profile_hapax_count_consistent(client):
    r = client.get('/api/passage-profile?book=Matthew&ch_start=1&ch_end=1')
    data = r.get_json()
    assert data['hapax_in_passage'] <= data['unique_roots']
    assert data['corpus_hapaxes'] <= data['unique_roots']
    # Rarity buckets must sum to unique_roots
    bucket_sum = sum(data['rarity_buckets'].values())
    assert bucket_sum == data['unique_roots']
