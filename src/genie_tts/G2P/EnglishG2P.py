import re
from functools import lru_cache
from typing import Iterable, List

from g2p_en import G2p

from .SymbolsV2 import symbols_v2

# Instantiate a single G2p object - the constructor is relatively heavy.
_EN_G2P = G2p()

# Punctuation emitted by g2p_en that we want to keep in the final symbol stream.
_PUNCTUATION_MAP = {
    ".": ".",
    ",": ",",
    "!": "!",
    "?": "?",
    "-": "-",
    ";": ".",
    ":": ".",
    "...": ".",
}

def _normalise_english_text(text: str) -> str:
    # Collapse multiple whitespace characters so g2p_en does not output
    # redundant " " tokens between words.
    return re.sub(r"\s+", " ", text.strip())


@lru_cache(maxsize=1024)
def _run_g2p(text: str) -> List[str]:
    return _EN_G2P(text)


def _iter_phoneme_tokens(raw_tokens: Iterable[str]) -> Iterable[str]:
    for token in raw_tokens:
        cleaned = token.strip()
        if not cleaned:
            continue
        if cleaned in _PUNCTUATION_MAP:
            yield _PUNCTUATION_MAP[cleaned]
            continue
        # g2p_en sometimes returns the ellipsis as three separate dots
        if cleaned == ".":
            yield "."
            continue
        if cleaned == "'":
            # Apostrophes do not carry useful information for the model - skip.
            continue
        if cleaned == "\"":
            continue
        if cleaned == " ":
            # The caller can insert explicit pause symbols if needed.
            continue
        # Keep ARPAbet tokens as-is (they are already uppercase).
        yield cleaned


def english_to_phonemes(text: str) -> List[str]:
    """
    Convert English text into the phoneme inventory expected by Genie-TTS.

    Returns a list of phoneme / symbol strings. Unknown symbols are filtered out,
    so the caller can safely map the output to IDs.
    """
    norm_text = _normalise_english_text(text)
    if not norm_text:
        return []

    tokens = list(_iter_phoneme_tokens(_run_g2p(norm_text)))
    if not tokens:
        return []

    # Filter out items that are not part of the model vocabulary to avoid UNK spam.
    return [token for token in tokens if token in symbols_v2]
