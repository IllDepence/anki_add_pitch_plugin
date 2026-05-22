from typing import NewType, Literal

# A string containing only hiragana
HiraganaStr = NewType("HiraganaStr", str)
# A string containing only katakana
KatakanaStr = NewType("KatakanaStr", str)
# A string containing only kana
KanaStr = NewType("KanaStr", str)
# A list of kana strings each representing one mora (e.g. ['しゅ', 'ん'])
MoraList = list[KanaStr]
# An expression (vocabulary word) on an Anki card
ExpressionStr = NewType("ExpressionStr", str)
# Kana displayed with the pitch accent illustration
PitchAccentDisplayKana = KanaStr
# A character level pitch accent notation (拗音 as Hh or Ll; e.g. 旬 = LlHH)
PitchAccentNotationPerCharacter = NewType("PitchAccentNotationPerCharacter", str)
# A mora level pitch accent notation (e.g. 旬 = LHH)
PitchAccentNotationPerMora = NewType("PitchAccentNotationPerMora", str)
# A pitch accent notation (may be character or mora level)
PitchAccentNotation = PitchAccentNotationPerCharacter | PitchAccentNotationPerMora
# Reading of an expression together with character level pitch accent information
ReadingWithPitchPatternPerCharacter = tuple[
    PitchAccentDisplayKana, PitchAccentNotationPerCharacter
]
# Reading of an expression together with mora level pitch accent information
ReadingWithPitchPatternPerMora = tuple[
    PitchAccentDisplayKana, PitchAccentNotationPerMora
]
# Reading of an expression together with pitch accent information (may be character or mora level)
ReadingWithPitchPattern = (
    ReadingWithPitchPatternPerCharacter | ReadingWithPitchPatternPerMora
)
# A dictionary of expressions and their pitch accents
AccentDict = dict[
    ExpressionStr,
    list[ReadingWithPitchPatternPerCharacter | ReadingWithPitchPatternPerMora],
]
# An SVG string
SvgStr = NewType("SvgStr", str)
# Direction change of pitch (straight, up, down)
PitchChangeDirection = Literal["s"] | Literal["u"] | Literal["d"]
