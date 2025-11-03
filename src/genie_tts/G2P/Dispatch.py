import re
from typing import List

from .EnglishG2P import english_to_phonemes
from .JapaneseG2P import japanese_to_phones
from .SymbolsV2 import symbols_v2, symbol_to_id_v2

def text_to_phones(text: str) -> list[int]:
    phoneme_tokens: List[str] = []

    if re.search(r'[\u3040-\u30FF\u31F0-\u31FF\uFF00-\uFFEF\u4E00-\u9FAF]', text):
        phoneme_tokens.extend(japanese_to_phones(text))
    else:
        phoneme_tokens.extend(english_to_phonemes(text))

    filtered_tokens = [
        token if token in symbols_v2 else "UNK"
        for token in phoneme_tokens
    ]
    return [symbol_to_id_v2[token] for token in filtered_tokens]
