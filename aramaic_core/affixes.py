"""Prefix and suffix stripping rules for Syriac morphological analysis."""

from dataclasses import dataclass, field
from .characters import SYRIAC_CONSONANTS, WEAK_LETTERS


@dataclass
class StrippingResult:
    stem: str
    prefixes_removed: list[str] = field(default_factory=list)
    suffixes_removed: list[str] = field(default_factory=list)


# --- Prefix definitions ---
# Order matters: proclitics are stripped first (outermost), then verbal prefixes

# Single-letter proclitics
SINGLE_PROCLITICS = [
    '\u0718',  # ܘ w- (and)
    '\u0715',  # ܕ d- (of/that/which)
    '\u0712',  # ܒ b- (in/with)
    '\u0720',  # ܠ l- (to/for)
]

# Compound proclitics (two letters)
COMPOUND_PROCLITICS = [
    '\u0718\u0712',  # ܘܒ wb- (and in)
    '\u0718\u0720',  # ܘܠ wl- (and to)
    '\u0718\u0721',  # ܘܡ wm- (and from)
    '\u0718\u0715',  # ܘܕ wd- (and of)
    '\u0715\u0712',  # ܕܒ db- (that in)
    '\u0715\u0720',  # ܕܠ dl- (that to)
    '\u0715\u0721',  # ܕܡ dm- (that from)
    '\u0720\u0721',  # ܠܡ lm- (in order to)
]

# Verbal/derivational prefixes (applied after proclitic stripping)
VERBAL_PREFIXES = [
    '\u0710\u072C',  # ܐܬ at- (Ethpeel/Ethpaal reflexive/passive)
    '\u0710\u072B\u072C',  # ܐܫܬ asht- (Eshtaphal)
    '\u072B',  # ܫ sh- (Shafel causative)
    '\u0721',  # ܡ m- (participle prefix)
    '\u0722',  # ܢ n- (3ms imperfect)
    '\u072C',  # ܬ t- (2ms/3fs imperfect)
    '\u0710',  # ܐ a- (1s imperfect / Aphel causative)
]

# --- Suffix definitions ---
# Ordered longest-first to prevent partial matches

SUFFIXES = [
    # Compound verbal + pronominal (longest first)
    '\u072C\u0718\u0722',  # ܬܘܢ -thwn (2mp)
    '\u072C\u071D\u0722',  # ܬܝܢ -thyn (2fp)
    '\u071D\u072C\u0717',  # ܝܬܗ -yth (3ms object)
    '\u0722\u0722',        # ܢܢ -nn (1cp, as in ܝܕܥܝܢܢ)

    # Pronominal suffixes
    '\u0717\u0718\u0722',  # ܗܘܢ -hwn (3mp)
    '\u0717\u071D\u0722',  # ܗܝܢ -hyn (3fp)
    '\u071F\u0718\u0722',  # ܟܘܢ -kwn (2mp)
    '\u071F\u071D\u0722',  # ܟܝܢ -kyn (2fp)
    '\u0718\u0717\u071D',  # ܘܗܝ -why (3fs)
    '\u072C\u0717',        # ܬܗ -th (3ms possessive)
    '\u0722\u071D',        # ܢܝ -ny (1s object)

    # Plural and state markers
    '\u071D\u0722',  # ܝܢ -yn (masc. plural / participle plural)
    '\u072C\u0710',  # ܬܐ -tha (feminine / abstract noun)
    '\u0718\u072C\u0710',  # ܘܬܐ -wtha (abstract noun suffix)
    '\u0718\u072C\u0717',  # ܘܬܗ -wth (abstract + 3ms)

    # Short pronominal
    '\u0717',  # ܗ -h (3ms/3fs possessive)
    '\u071D',  # ܝ -y (1s possessive / 2fs/construct)
    '\u071F',  # ܟ -k (2ms possessive)
    '\u0722',  # ܢ -n (3mp short / energic)

    # Verbal suffixes
    '\u0718',  # ܘ -w (3mp perfect / plural imperative)
    '\u072C',  # ܬ -th (1s/2ms perfect / feminine)
    '\u0710',  # ܐ -a (emphatic state / 3fs)
]


def strip_proclitics(word: str) -> list[tuple[str, str]]:
    """Try stripping proclitic prefixes from the word.

    Returns list of (prefix_removed, remaining_stem) pairs.
    Always includes the original word (no stripping) as a candidate.
    """
    candidates = [('', word)]
    min_remaining = 2  # stem must have at least 2 consonants

    consonant_count = sum(1 for ch in word if ch in SYRIAC_CONSONANTS)

    # Try compound proclitics first (longer prefixes)
    for proclitic in COMPOUND_PROCLITICS:
        if word.startswith(proclitic):
            remaining = word[len(proclitic):]
            rem_consonants = sum(1 for ch in remaining if ch in SYRIAC_CONSONANTS)
            if rem_consonants >= min_remaining:
                candidates.append((proclitic, remaining))

    # Then single proclitics
    for proclitic in SINGLE_PROCLITICS:
        if word.startswith(proclitic) and consonant_count > min_remaining:
            remaining = word[len(proclitic):]
            rem_consonants = sum(1 for ch in remaining if ch in SYRIAC_CONSONANTS)
            if rem_consonants >= min_remaining:
                candidates.append((proclitic, remaining))

    return candidates


def strip_verbal_prefixes(word: str) -> list[tuple[str, str]]:
    """Try stripping verbal/derivational prefixes.

    Returns list of (prefix_removed, remaining_stem) pairs.
    Always includes the original word.
    """
    candidates = [('', word)]
    min_remaining = 2

    # Try longest prefixes first
    for prefix in VERBAL_PREFIXES:
        if word.startswith(prefix):
            remaining = word[len(prefix):]
            rem_consonants = sum(1 for ch in remaining if ch in SYRIAC_CONSONANTS)
            if rem_consonants >= min_remaining:
                candidates.append((prefix, remaining))

    return candidates


def strip_suffixes(word: str) -> list[tuple[str, str]]:
    """Try stripping suffixes from the word.

    Returns list of (suffix_removed, remaining_stem) pairs.
    Always includes the original word.
    """
    candidates = [('', word)]
    min_remaining = 2

    for suffix in SUFFIXES:
        if word.endswith(suffix):
            remaining = word[:-len(suffix)]
            rem_consonants = sum(1 for ch in remaining if ch in SYRIAC_CONSONANTS)
            if rem_consonants >= min_remaining:
                candidates.append((suffix, remaining))

    return candidates


def generate_candidate_stems(word: str) -> list[StrippingResult]:
    """Generate all plausible stem candidates by trying combinations of
    proclitic stripping, verbal prefix stripping, and suffix stripping.

    Returns a list of StrippingResult with unique stems.
    """
    seen_stems = set()
    results = []

    # Step 1: try proclitic stripping
    proclitic_candidates = strip_proclitics(word)

    for proclitic, after_proclitic in proclitic_candidates:
        # Step 2: try verbal prefix stripping on the result
        verbal_candidates = strip_verbal_prefixes(after_proclitic)

        for verbal_prefix, after_verbal in verbal_candidates:
            # Step 3: try suffix stripping on the result
            suffix_candidates = strip_suffixes(after_verbal)

            for suffix, stem in suffix_candidates:
                if stem and stem not in seen_stems:
                    seen_stems.add(stem)
                    prefixes = []
                    if proclitic:
                        prefixes.append(proclitic)
                    if verbal_prefix:
                        prefixes.append(verbal_prefix)
                    suffixes = [suffix] if suffix else []

                    results.append(StrippingResult(
                        stem=stem,
                        prefixes_removed=prefixes,
                        suffixes_removed=suffixes,
                    ))

    return results
