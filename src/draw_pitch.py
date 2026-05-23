import sys
from .types import (
    KanaStr,
    MoraList,
    PitchAccentNotationPerMora,
    SvgStr,
    PitchChangeDirection,
)


def hira_to_mora(hira: KanaStr) -> MoraList:
    """Example:
    in:  'しゅんかしゅうとう'
    out: ['しゅ', 'ん', 'か', 'しゅ', 'う', 'と', 'う']
    """

    mora_arr: MoraList = []
    # below is more readable in two lines; don't auto-format
    # fmt: off
    combiners = [
        "ゃ", "ゅ", "ょ", "ぁ", "ぃ", "ぅ", "ぇ", "ぉ",
        "ャ", "ュ", "ョ", "ァ", "ィ", "ゥ", "ェ", "ォ",
    ]
    # fmt: on

    i = 0
    mora: KanaStr
    while i < len(hira):
        if i + 1 < len(hira) and hira[i + 1] in combiners:
            mora = KanaStr(f"{hira[i]}{hira[i + 1]}")
            mora_arr.append(mora)
            i += 2
        else:
            mora = KanaStr(hira[i])
            mora_arr.append(mora)
            i += 1
    return mora_arr


def circle(x: int, y: int, o: bool = False) -> SvgStr:
    r = f'<circle r="5" cx="{x}" cy="{y}" style="opacity:1;fill:#000;" />'
    if o:
        r += f'<circle r="3.25" cx="{x}" cy="{y}" style="opacity:1;fill:#fff;" />'
    return SvgStr(r)


def text(x: int, mora: KanaStr) -> SvgStr:
    # letter positioning tested with Noto Sans CJK JP
    if len(mora) == 1:
        return SvgStr(
            (
                f'<text x="{x}" y="67.5" style="font-size:20px;'
                f'font-family:sans-serif;fill:#000;">{mora}</text>'
            )
        )
    else:
        return SvgStr(
            (
                f'<text x="{x - 5}" y="67.5" style="font-size:20px;'
                f'font-family:sans-serif;fill:#000;">{mora[0]}</text>'
                f'<text x="{x + 12}" y="67.5" style="font-size:14px;'
                f'font-family:sans-serif;fill:#000;">{mora[1]}</text>'
            )
        )


def path(x: int, y: int, typ: PitchChangeDirection, step_width: int) -> SvgStr:
    if typ == "s":  # straight
        delta = f"{step_width},0"
    elif typ == "u":  # up
        delta = f"{step_width},-25"
    elif typ == "d":  # down
        delta = f"{step_width},25"
    return SvgStr(
        (
            f'<path d="m {x},{y} {delta}" style="fill:none;stroke:#000;stroke-width:1.5;" />'
        )
    )


def pitch_svg(
    word: KanaStr, patt: PitchAccentNotationPerMora, silent: bool = False
) -> SvgStr:
    """Draw pitch accent patterns in SVG

    Examples:
        はし HLL (箸)
        はし LHL (橋)
        はし LHH (端)
    """

    mora = hira_to_mora(word)

    if len(patt) - len(mora) != 1 and not silent:
        print(f"pattern should be number of morae + 1 (got: {word}, {patt})")
    positions: int = max(len(mora), len(patt))
    step_width: int = 35
    margin_lr: int = 16
    svg_width: int = max(0, ((positions - 1) * step_width) + (margin_lr * 2))

    svg: str = (
        f'<svg class="pitch" width="{svg_width}px" height="75px" viewBox="0 0 {svg_width} 75">'
    )

    chars: str = ""
    for pos, mor in enumerate(mora):
        x_center = margin_lr + (pos * step_width)
        chars += text(x_center - 11, mor)

    circles: str = ""
    paths: str = ""
    prev_center: tuple[int, int]
    path_typ: PitchChangeDirection
    for pos, accent in enumerate(patt):
        x_center = margin_lr + (pos * step_width)
        if accent in ["H", "h", "1", "2"]:
            y_center = 5
        elif accent in ["L", "l", "0"]:
            y_center = 30
        else:
            # in case of an invalid accent mark, annotate in the center
            y_center = 17
        circles += circle(x_center, y_center, pos >= len(mora))
        if pos > 0:
            if prev_center[1] == y_center:
                path_typ = "s"
            elif prev_center[1] < y_center:
                path_typ = "d"
            elif prev_center[1] > y_center:
                path_typ = "u"
            paths += path(prev_center[0], prev_center[1], path_typ, step_width)
        prev_center = (x_center, y_center)

    svg += chars
    svg += paths
    svg += circles
    svg += "</svg>"

    return SvgStr(svg)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python3 draw_pitch.py <word> <patt>")
        sys.exit()

    word: KanaStr = KanaStr(sys.argv[1])
    patt: PitchAccentNotationPerMora = PitchAccentNotationPerMora(sys.argv[2])
    print(pitch_svg(word, patt, silent=True))
