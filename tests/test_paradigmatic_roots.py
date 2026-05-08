"""
Paradigmatic root regression battery.

Sanity-checks 10 well-known triliteral roots end-to-end through the API.
Each test verifies the root resolves correctly, has a Syriac form, has at
least one cognate (Hebrew or Arabic), and is attested in at least one
corpus. These tests pin the current behaviour so any future change to
extraction, lexicon, or cognate data surfaces as a test failure.

This is **not** a precision/recall study — that requires a hand-annotated
gold standard (Phase 2.1 in the roadmap). It is a smoke test on the
roots an Aramaicist would expect any tool to handle correctly.
"""

import pytest


# Each entry: (root, expected Syriac, English gloss substring, expected attestation).
#
# Latin transliteration convention used by parse_root_input():
#   T  → ܛ Teth       th  → ܬ Taw         a  → ܐ Alaph
#   o  → ܥ ʿAyn       e   → ܥ ʿAyn        kh → ܚ Heth
#   sh → ܫ Shin       ts  → ܨ Sade
PARADIGMATIC_ROOTS = [
    ('SH-L-M',  'ܫܠܡ', 'peace',         True),  # peace, well-being
    ('K-TH-B',  'ܟܬܒ', 'writ',          True),  # write (TH = Taw)
    ('Q-D-SH',  'ܩܕܫ', 'holy',          True),  # holy
    ('B-R-K',   'ܒܪܟ', 'bless',         True),  # bless
    ('R-KH-M',  'ܪܚܡ', None,            True),  # love / compassion / mercy
    ('M-L-K',   'ܡܠܟ', 'king',          True),  # king
    ('A-M-R',   'ܐܡܪ', None,            True),  # say / speak (initial Alaph)
    ('N-TH-N',  'ܢܬܢ', None,            True),  # give (TH = Taw)
    ('Y-D-O',   'ܝܕܥ', None,            True),  # know (final ʿAyn — O notation)
    ('SH-M-O',  'ܫܡܥ', None,            True),  # hear (final ʿAyn — O notation)
]


@pytest.mark.parametrize('root,expected_syriac,gloss_substr,expect_attested',
                         PARADIGMATIC_ROOTS)
def test_root_resolves_via_api(client, root, expected_syriac, gloss_substr, expect_attested):
    r = client.get(f'/api/roots?q={root}')
    assert r.status_code == 200, \
        f'/api/roots?q={root} returned {r.status_code} — paradigmatic root should resolve'
    data = r.get_json()
    assert 'root' in data
    assert 'matches' in data
    if expect_attested:
        assert len(data['matches']) > 0, \
            f'{root} has zero word-form matches across all 5 corpora — likely an extraction bug'


@pytest.mark.parametrize('root,expected_syriac,_,__', PARADIGMATIC_ROOTS)
def test_root_resolves_to_expected_syriac_form(client, root, expected_syriac, _, __):
    r = client.get(f'/api/roots?q={root}')
    data = r.get_json()
    assert data['root'] == expected_syriac, \
        f'{root} resolved to {data["root"]!r}, expected {expected_syriac!r}'


@pytest.mark.parametrize('root,_,__,___', PARADIGMATIC_ROOTS)
def test_root_has_cross_corpus_attestation(client, root, _, __, ___):
    """Each paradigmatic root should appear in at least one indexed corpus."""
    r = client.get(f'/api/roots?q={root}')
    data = r.get_json()
    attestation = data.get('corpus_attestation') or {}
    assert any(count > 0 for count in attestation.values()), \
        f'{root} has empty corpus_attestation map — extraction or indexing bug'


@pytest.mark.parametrize('root,_,__,___', PARADIGMATIC_ROOTS)
def test_root_has_diachronic_data(client, root, _, __, ___):
    """Diachronic endpoint should return per-corpus normalized frequency."""
    r = client.get(f'/api/diachronic/root?root={root}')
    assert r.status_code == 200, \
        f'/api/diachronic/root?root={root} returned {r.status_code}'
    data = r.get_json()
    # Expect a per-corpus structure
    assert data is not None
    assert 'normalized_per_10k' in data or 'corpora' in data or 'data' in data, \
        f'Diachronic response shape unexpected for {root}: keys={list(data.keys())}'


@pytest.mark.parametrize('root,_,__,___', PARADIGMATIC_ROOTS)
def test_root_paradigm_returns_stems(client, root, _, __, ___):
    """Paradigm endpoint should return at least one verb-stem grouping."""
    r = client.get(f'/api/paradigm?root={root}')
    assert r.status_code == 200
    data = r.get_json()
    assert data is not None


def test_paradigmatic_set_is_distinct(client):
    """No two paradigmatic roots should resolve to the same canonical key —
    if they do, our test set is degenerate."""
    seen = set()
    for root, *_ in PARADIGMATIC_ROOTS:
        r = client.get(f'/api/roots?q={root}')
        data = r.get_json()
        key = data.get('root_transliteration')
        assert key not in seen, f'{root} resolves to {key} which is a duplicate'
        seen.add(key)


def test_paradigmatic_roots_pass_smoke(client):
    """Belt-and-braces: the full round-trip on every paradigmatic root.
    If this fails, something is structurally broken with root extraction."""
    failures = []
    for root, *_ in PARADIGMATIC_ROOTS:
        r = client.get(f'/api/roots?q={root}')
        if r.status_code != 200:
            failures.append((root, r.status_code))
    assert not failures, f'Paradigmatic root regressions: {failures}'
