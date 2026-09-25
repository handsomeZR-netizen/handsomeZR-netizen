"""Extract bitmap glyphs from a pixel font into the plain-text format read by pixel.py.

Only needed when you want characters that are not in tools/fonts/*.txt yet.
Requires:  pip install fonttools brotli

    python tools/extract_font.py ark-pixel-12px-proportional-zh_hans.otf.woff2 \
        tools/fonts/ark-pixel-12px.txt --px 12 --gb2312 --extra "你要加的字"

Font sources (both SIL OFL 1.1):
    Ark Pixel Font  https://github.com/TakWolf/ark-pixel-font  (woff2 on ark-pixel-font.takwolf.com)
    Press Start 2P / Tiny5  npm: @fontsource/press-start-2p, @fontsource/tiny5
"""

import argparse
import math

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont

PUNCT = (
    "·—–…‘’“”•←↑→↓▲▶▼◀■□▪▫●○◆◇★☆♥♦✓✔✕✗、。，：；！？「」『』（）【】《》〈〉～・"
    "①②③④⑤⑥⑦⑧⑨⑩°×÷±％＋－／"
)


def gb2312_hanzi(level2=False):
    chars = []
    last_row = 0xF7 if level2 else 0xD7
    for hi in range(0xB0, last_row + 1):
        for lo in range(0xA1, 0xFF):
            try:
                chars.append(bytes([hi, lo]).decode("gb2312"))
            except UnicodeDecodeError:
                pass
    return chars


def glyph_bitmap(font, glyphset, name, unit):
    pen = DecomposingRecordingPen(glyphset)
    glyphset[name].draw(pen)
    contours, cur = [], []
    for op, args in pen.value:
        if op == "moveTo":
            cur = [args[0]]
        elif op == "lineTo":
            cur.append(args[0])
        elif op in ("closePath", "endPath"):
            if cur:
                contours.append(cur)
            cur = []
        else:
            raise ValueError(f"glyph {name} has curves; not a pixel font")
    edges = []
    for c in contours:
        for i in range(len(c)):
            (x0, y0), (x1, y1) = c[i], c[(i + 1) % len(c)]
            if x0 == x1 and y0 != y1:
                edges.append((x0 / unit, min(y0, y1) / unit, max(y0, y1) / unit))
            elif x0 != x1 and y0 != y1:
                raise ValueError(f"glyph {name} has a diagonal edge")
    pixels = set()
    if edges:
        lo = math.floor(min(e[1] for e in edges))
        hi = math.ceil(max(e[2] for e in edges))
        for py in range(lo, hi):
            yc = py + 0.5
            xs = sorted(e[0] for e in edges if e[1] <= yc < e[2])
            for i in range(0, len(xs) - 1, 2):
                for px in range(round(xs[i]), round(xs[i + 1])):
                    pixels.add((px, py))
    return pixels


def encode(cp, adv, pixels):
    if not pixels:
        return f"{cp:x} {adv} 0 0 0 0 -"
    xs = [p[0] for p in pixels]
    ys = [p[1] for p in pixels]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, h = x1 - x0 + 1, y1 - y0 + 1
    digits = (w + 3) // 4
    rows = []
    for y in range(y1, y0 - 1, -1):  # top row first
        v = 0
        for x in range(x0, x1 + 1):
            v = (v << 1) | ((x, y) in pixels)
        v <<= digits * 4 - w
        rows.append(f"{v:0{digits}x}")
    # x0: left offset from pen origin; y1: top row height above baseline (y up)
    return f"{cp:x} {adv} {x0} {y1} {w} {h} {''.join(rows)}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("font")
    ap.add_argument("out")
    ap.add_argument("--px", type=int, required=True, help="design pixel size, e.g. 12 or 8")
    ap.add_argument("--all", action="store_true", help="every glyph in the cmap")
    ap.add_argument("--gb2312", action="store_true", help="GB2312 level-1 hanzi (3755)")
    ap.add_argument("--gb2312-full", action="store_true", help="all GB2312 hanzi (6763)")
    ap.add_argument("--extra", default="", help="extra characters, or @file to read them from")
    ap.add_argument("--name", default="")
    args = ap.parse_args()

    font = TTFont(args.font)
    cmap = font.getBestCmap()
    glyphset = font.getGlyphSet()
    hmtx = font["hmtx"]
    upm = font["head"].unitsPerEm
    unit = upm // args.px
    hhea = font["hhea"]

    if args.all:
        cps = sorted(cmap)
    else:
        chars = [chr(c) for c in range(0x20, 0x7F)] + list(PUNCT)
        if args.gb2312 or args.gb2312_full:
            chars += gb2312_hanzi(level2=args.gb2312_full)
        extra = args.extra
        if extra.startswith("@"):
            with open(extra[1:], encoding="utf-8") as f:
                extra = f.read()
        chars += [c for c in extra if not c.isspace()]
        cps = sorted({ord(c) for c in chars if ord(c) in cmap})
        missing = sorted({c for c in chars if ord(c) not in cmap})
        if missing:
            print("not in font:", "".join(missing))

    lines = [
        f"# {args.name or args.font} - bitmap subset, SIL OFL 1.1 (see OFL-*.txt)",
        "# format: codepoint(hex) advance x_offset top_row width height rows(hex, top first)",
        f"@ px={args.px} ascent={hhea.ascent // unit} descent={-hhea.descent // unit}",
    ]
    for cp in cps:
        name = cmap[cp]
        adv = round(hmtx[name][0] / unit)
        lines.append(encode(cp, adv, glyph_bitmap(font, glyphset, name, unit)))
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {len(cps)} glyphs to {args.out}")


if __name__ == "__main__":
    main()
