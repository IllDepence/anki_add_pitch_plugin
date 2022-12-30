""" Definition of consonants
"""

import re


re_ja_patt = re.compile(
    r'['
    r'\u3041-\u3096'  # hiragana
    r'\u30A0-\u30FF'  # katakana
    r'\u3400-\u4DB5\u4E00-\u9FCB\uF900-\uFA6A'  # kanji
    r'\u3005'  # 々
    # r'\u2026\u301C'  # …〜 (might be used to indicate affixes)
    #                        (disabled — causes more problems than benefits)
    r']+'
)
re_variation_selectors_patt = re.compile(
    r'['
    r'\U000E0100-\U000E013D'  # variation selectors [1]
    r']+'
)
# [1] https://en.wikipedia.org/wiki/Variation_Selectors_Supplement
re_bracketed_content_patt = re.compile(
    r'[\[\(\{][^\]\)\}]*[\]\)\}]'
)
re_hira_patt = re.compile(
    r'['
    r'\u3041-\u3096'  # hiragana
    r']+'
)
re_all_hira_patt = re.compile(
    r'^['
    r'\u3041-\u3096'  # hiragana
    r']+$'
)
