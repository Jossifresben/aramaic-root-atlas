"""
CSV loader sanity checks for the two v3.3 corpora (targum_writings,
ephrem_works): schema, row counts, and basic data hygiene. These read the
raw CSVs directly rather than going through the Flask app/client, so a
regression here pinpoints a data problem rather than a wiring problem.
"""

import csv
import os

import pytest

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'corpora')

EXPECTED_HEADER = ['book_order', 'book', 'chapter', 'verse', 'reference', 'syriac']

# Hebrew niqqud (vowel points + cantillation-adjacent points) block.
NIQQUD_RANGE = (0x05B0, 0x05C7)


def _read_rows(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        rows = list(reader)
    return header, rows


# -- targum_writings.csv -----------------------------------------------------

def test_targum_writings_csv_header():
    header, _ = _read_rows('targum_writings.csv')
    assert header == EXPECTED_HEADER


def test_targum_writings_csv_row_count():
    _, rows = _read_rows('targum_writings.csv')
    assert len(rows) == 7022


def test_targum_writings_csv_no_empty_syriac():
    _, rows = _read_rows('targum_writings.csv')
    empty = [r['reference'] for r in rows if not r['syriac'].strip()]
    assert empty == [], f'{len(empty)} rows with empty syriac field: {empty[:5]}'


def test_targum_writings_csv_no_niqqud():
    """Targum Writings text is consonantal (diacritics stripped at fetch
    time per fetch_targum_jonathan.py's strip_diacritics pattern); no
    Hebrew vowel-point codepoints should remain."""
    _, rows = _read_rows('targum_writings.csv')
    lo, hi = NIQQUD_RANGE
    offenders = [
        r['reference'] for r in rows
        if any(lo <= ord(ch) <= hi for ch in r['syriac'])
    ]
    assert offenders == [], \
        f'{len(offenders)} rows contain niqqud codepoints: {offenders[:5]}'


# -- ephrem_works.csv --------------------------------------------------------

def test_ephrem_works_csv_header():
    header, _ = _read_rows('ephrem_works.csv')
    assert header == EXPECTED_HEADER


def test_ephrem_works_csv_row_count():
    _, rows = _read_rows('ephrem_works.csv')
    assert len(rows) == 1330


def test_ephrem_works_csv_no_empty_syriac():
    _, rows = _read_rows('ephrem_works.csv')
    empty = [r['reference'] for r in rows if not r['syriac'].strip()]
    assert empty == [], f'{len(empty)} rows with empty syriac field: {empty[:5]}'


def test_ephrem_works_csv_references_unique():
    _, rows = _read_rows('ephrem_works.csv')
    refs = [r['reference'] for r in rows]
    assert len(refs) == len(set(refs)), 'duplicate reference values found in ephrem_works.csv'
