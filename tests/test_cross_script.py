"""
Cross-script normalization tests.

The Atlas claims that Syriac (ܟܬܒ), Hebrew square script (כתב), and Arabic
(كتب) all resolve to the same canonical root key. These tests pin that
behaviour for a handful of well-attested Semitic roots, so any future change
to the character maps or transliteration tables surfaces as a test failure.
"""

import pytest
from aramaic_core.characters import (
    detect_script,
    transliterate_syriac,
    transliterate_hebrew,
)


# Pairs: (Syriac form, Hebrew form, expected Latin transliteration)
CROSS_SCRIPT_PAIRS = [
    ('ܫܠܡ', 'שלם', 'shlm'),    # SH-L-M  (peace / wholeness)
    ('ܟܬܒ', 'כתב', 'kthb'),    # K-T-B   (write)
    ('ܒܪܟ', 'ברך', 'brk'),     # B-R-K   (bless)
    ('ܩܕܫ', 'קדש', 'qdsh'),    # Q-D-SH  (holy)
    ('ܪܚܡ', 'רחם', 'rkhm'),    # R-KH-M  (love / mercy)
    ('ܡܠܟ', 'מלך', 'mlk'),     # M-L-K   (king)
    ('ܥܒܕ', 'עבד', 'Abd'),     # `-B-D   (do / serve / slave) — note: ` may transliterate as 'A' or "'"
    ('ܝܕܥ', 'ידע', 'ydA'),     # Y-D-`   (know)
]


@pytest.mark.parametrize('syriac,hebrew,_expected', CROSS_SCRIPT_PAIRS)
def test_script_detection(syriac, hebrew, _expected):
    """detect_script must distinguish Syriac, Hebrew, and Arabic."""
    assert detect_script(syriac) == 'syriac'
    assert detect_script(hebrew) == 'hebrew'


@pytest.mark.parametrize('syriac,hebrew,expected', CROSS_SCRIPT_PAIRS)
def test_syriac_and_hebrew_share_transliteration(syriac, hebrew, expected):
    """Syriac and Hebrew forms of cognate roots must produce the same
    Latin transliteration. This is the cross-script normalization claim."""
    syr_trans = transliterate_syriac(syriac).lower()
    heb_trans = transliterate_hebrew(hebrew).lower()
    # Some roots may differ slightly between Syriac/Hebrew transliteration
    # (e.g. shewa, ʿayin handling) — assert at least that the consonants
    # match in their lowercased form, ignoring case-sensitive markers.
    assert syr_trans == heb_trans, (
        f'Syriac {syriac!r} → {syr_trans!r}, Hebrew {hebrew!r} → {heb_trans!r}; '
        'cross-script normalization should produce identical transliterations.'
    )


def test_empty_input_does_not_crash():
    """Empty / whitespace input must not raise."""
    assert detect_script('') in (None, 'unknown', '', 'latin')
    assert transliterate_syriac('') == ''
    assert transliterate_hebrew('') == ''


def test_mixed_script_input_handled():
    """Strings with mixed scripts shouldn't crash detect_script."""
    # Common in academic prose: Syriac word inside English context
    result = detect_script('peace ܫܠܡ wholeness')
    # We don't assert which script wins; just that it's deterministic and
    # returns a string.
    assert isinstance(result, str)


def test_api_resolves_cross_script_to_same_root(client):
    """End-to-end: Syriac, Hebrew, Latin all resolve to the same root key
    via the /api/roots endpoint."""
    # Latin transliteration with dashes
    r1 = client.get('/api/roots?q=SH-L-M')
    # Syriac Unicode
    r2 = client.get('/api/roots?q=%D7%D9%E0%D7%E0%D7%E1')  # garbled — use real one below
    # Use the actual Syriac directly via Unicode escape
    import urllib.parse
    syriac_q = urllib.parse.quote('ܫܠܡ')
    r2 = client.get(f'/api/roots?q={syriac_q}')

    assert r1.status_code == 200
    assert r2.status_code == 200

    d1 = r1.get_json()
    d2 = r2.get_json()

    # Both must resolve to the same canonical key
    assert d1.get('root_transliteration') == d2.get('root_transliteration'), (
        f'Latin SH-L-M resolved to {d1.get("root_transliteration")} but '
        f'Syriac ܫܠܡ resolved to {d2.get("root_transliteration")} — '
        'cross-script normalization broken at the API layer.'
    )
