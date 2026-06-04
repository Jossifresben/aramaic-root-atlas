import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import app as flask_app


def test_featured_roots_all_resolve():
    """Every curated hero/root-of-day entry must parse AND exist in the index."""
    flask_app._init()
    feat = flask_app._featured
    assert feat['hero'], 'hero list is empty'
    for key in set(feat['hero']) | set(feat['root_of_day']):
        syriac = flask_app.parse_root_input(key)
        assert syriac is not None, f'{key} does not parse'
        assert flask_app._extractor.lookup_root(syriac) is not None, f'{key} not attested'


def test_root_of_the_day_is_deterministic():
    flask_app._init()
    a = flask_app._root_of_the_day()
    b = flask_app._root_of_the_day()
    assert a == b and a in flask_app._featured['root_of_day']


def test_root_card_known_root():
    flask_app._init()
    card = flask_app._root_card('SH-L-M')
    assert card is not None
    assert card['syriac'] == 'ܫܠܡ'
    assert card['gloss']           # non-empty gloss
    assert card['total'] > 0
    assert card['key']             # round-trippable key for URLs


def test_root_card_unknown_returns_none():
    flask_app._init()
    assert flask_app._root_card('ZZZZ') is None
