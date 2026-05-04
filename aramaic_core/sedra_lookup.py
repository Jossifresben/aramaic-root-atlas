"""
SEDRA IV lookup module with file-based cache.

API endpoint: GET https://sedra.bethmardutho.org/api/word/{syriac_word}

Each array element in the response has:
  - syriac: the queried word form
  - stem: the Syriac root string
  - category: "verb" | "noun" | etc. (may be absent on some entries)
  - kaylo: verb stem label (e.g. "paʿʿel", "peal") — verb entries only
  - isLexicalForm: "true" | "false"
  - glosses.eng: list of English gloss strings

Cache format (data/roots/sedra_cache.json):
  {
    "ܫܠܡ": {"stem": "ܫܠܡ", "gloss": "complete, finish", "category": "verb", "kaylo": "paʿʿel"},
    "ܐܝܕܐ": null
  }
  null means SEDRA has no entry for this word (cached miss).
"""

import json
import os
import time
from typing import Optional

import requests

CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'roots', 'sedra_cache.json')

_API_BASE = 'https://sedra.bethmardutho.org/api/word/{}'
_TIMEOUT = 10  # seconds


class SedraLookup:
    def __init__(self, cache_path: str = CACHE_FILE):
        self.cache_path = os.path.normpath(cache_path)
        self._cache: dict = {}

    # ------------------------------------------------------------------
    # Cache I/O
    # ------------------------------------------------------------------

    def load_cache(self) -> None:
        """Load the JSON cache from disk. Silent if the file does not exist."""
        if not os.path.exists(self.cache_path):
            return
        try:
            with open(self.cache_path, 'r', encoding='utf-8') as fh:
                self._cache = json.load(fh)
        except (json.JSONDecodeError, OSError):
            self._cache = {}

    def save_cache(self) -> None:
        """Write the current cache to disk."""
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, 'w', encoding='utf-8') as fh:
            json.dump(self._cache, fh, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def lookup(self, syriac_word: str) -> Optional[dict]:
        """
        Return the cached result for *syriac_word*.

        - Returns a dict if a cached hit exists.
        - Returns None if there is a cached miss (SEDRA had no entry).
        - Raises KeyError if the word has never been fetched (not in cache).
          Callers that want a soft fallback can catch KeyError or check
          `syriac_word in s._cache` first.
        """
        if syriac_word not in self._cache:
            raise KeyError(syriac_word)
        return self._cache[syriac_word]  # may be None (cached miss)

    def fetch_live(self, syriac_word: str) -> Optional[dict]:
        """
        Query the SEDRA API directly and return a parsed result dict,
        or None if SEDRA has no entry for this word.

        Does NOT update the cache — call save_cache() separately if needed.
        """
        url = _API_BASE.format(syriac_word)
        try:
            resp = requests.get(url, timeout=_TIMEOUT)
        except requests.RequestException:
            return None

        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            return None

        try:
            data = resp.json()
        except ValueError:
            return None

        if not data or not isinstance(data, list):
            return None

        return self._parse_response(data)

    # ------------------------------------------------------------------
    # Bulk populate
    # ------------------------------------------------------------------

    def populate(self, words, delay: float = 0.15) -> None:
        """
        Query SEDRA for each word not already in the cache.
        Saves the cache to disk every 100 words and at the end.

        :param words: iterable of Syriac word strings
        :param delay: seconds to sleep between requests (default 0.15)
        """
        pending = [w for w in words if w not in self._cache]
        for i, word in enumerate(pending):
            result = self.fetch_live(word)
            self._cache[word] = result  # None on miss

            if delay > 0:
                time.sleep(delay)

            if (i + 1) % 100 == 0:
                self.save_cache()
                print(f'[SEDRA] {i + 1}/{len(pending)} words processed, cache saved.')

        self.save_cache()
        print(f'[SEDRA] Done. {len(pending)} words fetched, cache saved to {self.cache_path}.')

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_response(self, entries: list) -> Optional[dict]:
        """
        Extract the most useful entry from the SEDRA response array.

        Preference order:
          1. First entry where isLexicalForm == "true"
          2. First entry in the array (fallback)

        Returns a normalised dict with keys: stem, gloss, category, kaylo.
        Returns None if the entry contains no usable data (empty stem).
        """
        # Prefer the lexical form
        chosen = None
        for entry in entries:
            if entry.get('isLexicalForm') == 'true':
                chosen = entry
                break
        if chosen is None:
            chosen = entries[0]

        stem = chosen.get('stem', '')
        if not stem:
            return None

        # Collect English glosses
        glosses_obj = chosen.get('glosses', {})
        eng_glosses = glosses_obj.get('eng', []) if isinstance(glosses_obj, dict) else []
        # De-duplicate while preserving order; strip whitespace
        seen: set = set()
        clean_glosses = []
        for g in eng_glosses:
            g = g.strip()
            if g and g not in seen:
                seen.add(g)
                clean_glosses.append(g)
        gloss = ', '.join(clean_glosses[:5])  # cap at 5 to keep it concise

        return {
            'stem': stem,
            'gloss': gloss,
            'category': chosen.get('category', ''),
            'kaylo': chosen.get('kaylo', ''),
        }
