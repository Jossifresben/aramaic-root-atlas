"""Core root extraction engine for Syriac triliteral roots."""

import json
import os
from collections import defaultdict
from dataclasses import dataclass, field

from .characters import (
    SYRIAC_CONSONANTS, WEAK_LETTERS, syriac_consonants_of, transliterate_syriac
)
from .corpus import AramaicCorpus
from .affixes import generate_candidate_stems


@dataclass
class RootMatch:
    """A word form matched to a root, with its verse references."""
    form: str
    transliteration: str
    references: list[str] = field(default_factory=list)
    count: int = 0


@dataclass
class RootEntry:
    """All information about a root found in the corpus."""
    root: str
    root_transliteration: str
    matches: list[RootMatch] = field(default_factory=list)
    total_occurrences: int = 0


class RootExtractor:
    """Extracts triliteral roots from Syriac words and builds a root index."""

    def __init__(self, corpus: AramaicCorpus, data_dir: str | None = None):
        self.corpus = corpus
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.data_dir = data_dir

        # Known roots: root_string -> {gloss, forms}
        self._known_roots: dict = {}
        # Form -> root mapping (built from known_roots forms lists)
        self._form_to_root: dict[str, str] = {}
        # Stopwords set
        self._stopwords: set[str] = set()
        # Pre-computed root index: root -> RootEntry
        self._root_index: dict[str, RootEntry] = {}
        # Word -> root mapping (built during build_index)
        self._word_to_root: dict[str, str] = {}
        self._built = False

    def load_data(self) -> None:
        """Load known roots and stopwords from JSON files."""
        # Load known roots
        roots_path = os.path.join(self.data_dir, 'known_roots.json')
        if os.path.exists(roots_path):
            with open(roots_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._known_roots = data.get('roots', {})
            # Build form -> root reverse mapping
            for root_str, info in self._known_roots.items():
                root_clean = root_str.strip()
                for form in info.get('forms', []):
                    self._form_to_root[form] = root_clean

        # Load stopwords
        stop_path = os.path.join(self.data_dir, 'stopwords.json')
        if os.path.exists(stop_path):
            with open(stop_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for category in data.values():
                if isinstance(category, list):
                    self._stopwords.update(category)

    def _is_stopword(self, word: str) -> bool:
        return word in self._stopwords

    def _extract_root_for_word(self, word: str) -> str | None:
        """Try to extract a root from a single word.

        Returns the root as a 2- or 3-character Syriac string, or None.
        """
        # 1. Direct form lookup in known dictionary
        if word in self._form_to_root:
            return self._form_to_root[word]

        # 2. Get consonants only
        consonants = syriac_consonants_of(word)
        if not consonants:
            return None

        # 3. If exactly 3 consonants, it might be a bare root
        if len(consonants) == 3:
            # Validate against known roots
            if consonants in self._known_roots:
                return consonants
            # Even if not known, 3-consonant words are likely roots
            return consonants

        # 3b. If exactly 2 consonants and it's a known biliteral root
        if len(consonants) == 2 and consonants in self._known_roots:
            return consonants

        # 4. Generate candidate stems via affix stripping
        candidates = generate_candidate_stems(word)

        best_root = None
        best_score = -1

        for candidate in candidates:
            stem = candidate.stem
            stem_consonants = syriac_consonants_of(stem)

            if len(stem_consonants) == 3:
                root_candidate = stem_consonants
                score = self._score_root(root_candidate, candidate)
                if score > best_score:
                    best_score = score
                    best_root = root_candidate

            elif len(stem_consonants) == 4:
                # Try removing infixed ܘ or ܝ (matres lectionis)
                for i in range(1, 3):  # check positions 1 and 2
                    if i < len(stem_consonants) and stem_consonants[i] in WEAK_LETTERS:
                        reduced = stem_consonants[:i] + stem_consonants[i+1:]
                        if len(reduced) == 3:
                            score = self._score_root(reduced, candidate) * 0.8
                            if score > best_score:
                                best_score = score
                                best_root = reduced

            elif len(stem_consonants) == 2:
                # Weak root: try inserting ܘ or ܝ as middle radical
                for weak in ['\u0718', '\u071D', '\u0710']:  # ܘ ܝ ܐ
                    reconstructed = stem_consonants[0] + weak + stem_consonants[1]
                    score = self._score_root(reconstructed, candidate) * 0.6
                    if score > best_score:
                        best_score = score
                        best_root = reconstructed

        return best_root

    def _score_root(self, root: str, candidate=None) -> float:
        """Score a root candidate. Higher = more likely correct."""
        score = 0.5  # base score

        # Known root bonus
        if root in self._known_roots:
            score += 0.4

        # Minimal stripping bonus
        if candidate and not candidate.prefixes_removed and not candidate.suffixes_removed:
            score += 0.1

        return score

    def build_index(self) -> None:
        """Process the entire corpus and build the root index."""
        if self._built:
            return

        self.load_data()
        self.corpus.load()

        root_data: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

        for word in self.corpus.get_unique_words():
            if self._is_stopword(word):
                continue
            if '-' in word:
                continue  # skip compound proper nouns

            root = self._extract_root_for_word(word)
            if root is None:
                continue

            self._word_to_root[word] = root

            # Get all references where this word appears
            refs = self.corpus.get_occurrences(word)
            root_data[root][word] = refs

        # Build RootEntry objects
        for root_str, forms_dict in root_data.items():
            entry = RootEntry(
                root=root_str,
                root_transliteration=transliterate_syriac(root_str),
            )
            for form, refs in forms_dict.items():
                match = RootMatch(
                    form=form,
                    transliteration=transliterate_syriac(form),
                    references=refs,
                    count=len(refs),
                )
                entry.matches.append(match)
                entry.total_occurrences += len(refs)

            # Sort matches by frequency (most common first)
            entry.matches.sort(key=lambda m: m.count, reverse=True)
            self._root_index[root_str] = entry

        self._built = True

    def lookup_root(self, root_syriac: str) -> RootEntry | None:
        """Look up a root in the pre-built index.

        Args:
            root_syriac: 3-character Syriac root string (e.g., ܟܬܒ)

        Returns:
            RootEntry with all matched forms and references, or None.
        """
        self.build_index()
        return self._root_index.get(root_syriac)

    def get_all_roots(self) -> list[RootEntry]:
        """Return all roots found in the corpus, sorted by frequency."""
        self.build_index()
        roots = list(self._root_index.values())
        roots.sort(key=lambda r: r.total_occurrences, reverse=True)
        return roots

    def get_root_count(self) -> int:
        """Return the number of unique roots found."""
        self.build_index()
        return len(self._root_index)

    def lookup_word_root(self, word: str) -> str | None:
        """Return the Syriac root for a given word form, or None."""
        self.build_index()
        return self._word_to_root.get(word)

    def get_root_gloss(self, root_syriac: str) -> str:
        """Return the English gloss for a root from known_roots.json."""
        self.load_data()
        info = self._known_roots.get(root_syriac)
        if info:
            return info.get('gloss', '')
        return ''
