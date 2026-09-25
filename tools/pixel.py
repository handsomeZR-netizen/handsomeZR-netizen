"""Pixel-art SVG primitives: bitmap fonts, pixel canvases, notched panels.

Everything is emitted as crisp rectangles merged into <path> data, so the
generated SVGs need no fonts, no scripts and no external requests - they
render the same inside GitHub's <img> sandbox as in a browser tab.
Python standard library only.
"""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

FONT_DIR = Path(__file__).resolve().parent / "fonts"


def num(v: float) -> str:
    """Compact number formatting for path data."""
    if abs(v - round(v)) < 1e-6:
        return str(int(round(v)))
    return f"{v:.2f}".rstrip("0").rstrip(".")


# --------------------------------------------------------------------------- fonts


class Glyph:
    __slots__ = ("adv", "x0", "top", "w", "h", "rows")

    def __init__(self, adv, x0, top, w, h, rows):
        self.adv, self.x0, self.top, self.w, self.h, self.rows = adv, x0, top, w, h, rows

    def pixels(self):
        """(x, y) cells, y pointing down, baseline at y = 0."""
        for r, bits in enumerate(self.rows):
            for c in range(self.w):
                if bits >> (self.w - 1 - c) & 1:
                    yield self.x0 + c, r - self.top - 1


class BitmapFont:
    """Glyph data extracted by extract_font.py (one glyph per line)."""

    def __init__(self, path: Path):
        self.name = path.stem
        self.glyphs: dict[int, Glyph] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#"):
                continue
            if line.startswith("@"):
                meta = dict(kv.split("=") for kv in line[1:].split())
                self.px = int(meta["px"])
                self.ascent = int(meta["ascent"])
                self.descent = int(meta["descent"])
                continue
            cp, adv, x0, top, w, h, bits = line.split()
            w, h = int(w), int(h)
            rows = []
            if w:
                digits = (w + 3) // 4
                pad = digits * 4 - w
                rows = [int(bits[i * digits:(i + 1) * digits], 16) >> pad for i in range(h)]
            self.glyphs[int(cp, 16)] = Glyph(int(adv), int(x0), int(top), w, h, rows)
        if self.px == 12:
            # a narrow middle dot reads better than the full-width CJK one in mixed text
            self.glyphs[0xB7] = Glyph(6, 2, 4, 2, 2, [0b11, 0b11])

    def glyph(self, ch: str) -> Glyph:
        g = self.glyphs.get(ord(ch))
        if g is None:
            raise KeyError(
                f"'{ch}' (U+{ord(ch):04X}) is not in {self.name}; "
                "add it with tools/extract_font.py --extra"
            )
        return g

    def measure(self, text: str, tracking: int = 0) -> int:
        if not text:
            return 0
        return sum(self.glyph(ch).adv for ch in text) + tracking * (len(text) - 1)

    def pixels(self, text: str, tracking: int = 0) -> tuple[set, int]:
        out, pen = set(), 0
        for ch in text:
            g = self.glyph(ch)
            out.update((pen + x, y) for x, y in g.pixels())
            pen += g.adv + tracking
        return out, (pen - tracking if text else 0)

    def wrap(self, text: str, max_px: int, tracking: int = 0) -> list[str]:
        """Greedy wrap: breaks Latin text at spaces and CJK anywhere."""
        lines, cur = [], ""
        tokens, word = [], ""
        for ch in text:
            if ord(ch) > 0x2E7F or ch == " ":
                if word:
                    tokens.append(word)
                    word = ""
                tokens.append(ch)
            else:
                word += ch
        if word:
            tokens.append(word)
        for tok in tokens:
            trial = cur + tok
            if cur and self.measure(trial.rstrip(), tracking) > max_px:
                lines.append(cur.rstrip())
                cur = "" if tok == " " else tok
            else:
                cur = trial
        if cur.strip():
            lines.append(cur.rstrip())
        return lines


@lru_cache(maxsize=None)
def font(name: str) -> BitmapFont:
    return BitmapFont(FONT_DIR / f"{name}.txt")


# ------------------------------------------------------------------ pixel sets


def rects(cells):
    """Merge cells into rectangles: horizontal runs, then identical runs stacked."""
    rows = defaultdict(list)
    for x, y in cells:
        rows[y].append(x)
    out, live = [], {}
    for y in sorted(rows):
        xs = sorted(rows[y])
        runs, start = [], xs[0]
        for a, b in zip(xs, xs[1:] + [None]):
            if b != a + 1:
                runs.append((start, a + 1))
                start = b
        nxt = {}
        for run in runs:
            prev = live.pop(run, None)
            if prev and prev[0] + prev[1] == y:
                nxt[run] = [prev[0], prev[1] + 1]
            else:
                if prev:
                    live[run] = prev
                nxt[run] = [y, 1]
        for run, (y0, h) in live.items():
            out.append((run[0], y0, run[1] - run[0], h))
        live = nxt
    for run, (y0, h) in live.items():
        out.append((run[0], y0, run[1] - run[0], h))
    return out


def cells_path(cells, s: float = 1, ox: float = 0, oy: float = 0) -> str:
    parts = []
    for x, y, w, h in sorted(rects(cells), key=lambda r: (r[1], r[0])):
        parts.append(
            f"M{num(ox + x * s)} {num(oy + y * s)}h{num(w * s)}v{num(h * s)}h-{num(w * s)}z"
        )
    return "".join(parts)


def dilate(cells, r: int = 1, diagonal: bool = True):
    out = set(cells)
    for x, y in cells:
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if diagonal or dx == 0 or dy == 0:
                    out.add((x + dx, y + dy))
    return out


def shift(cells, dx: int, dy: int):
    return {(x + dx, y + dy) for x, y in cells}


def embolden(cells):
    return cells | shift(cells, 1, 0)


# --------------------------------------------------------------------- canvas


class Canvas:
    """A painter's-algorithm pixel grid; export() groups cells by colour."""

    def __init__(self):
        self.px: dict[tuple[int, int], str] = {}

    def set(self, x, y, color):
        if color is None:
            self.px.pop((x, y), None)
        else:
            self.px[(x, y)] = color

    def cells(self, cells, color):
        for c in cells:
            self.set(c[0], c[1], color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def sprite(self, rows, palette, x=0, y=0, flip=False):
        for r, line in enumerate(rows):
            if flip:
                line = line[::-1]
            for c, ch in enumerate(line):
                if ch in palette:
                    self.set(x + c, y + r, palette[ch])

    def disc(self, cx, cy, r, color):
        for yy in range(int(cy - r) - 1, int(cy + r) + 2):
            for xx in range(int(cx - r) - 1, int(cx + r) + 2):
                if (xx + 0.5 - cx) ** 2 + (yy + 0.5 - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def polygon(self, pts, color):
        for c in polygon_cells(pts):
            self.set(c[0], c[1], color)

    def line(self, x0, y0, x1, y1, color):
        for c in line_cells(x0, y0, x1, y1):
            self.set(c[0], c[1], color)

    def export(self, s: float = 1, ox: float = 0, oy: float = 0, extra: str = "") -> str:
        by_color = defaultdict(set)
        for c, color in self.px.items():
            by_color[color].add(c)
        return "".join(
            f'<path fill="{color}"{extra} d="{cells_path(cells, s, ox, oy)}"/>'
            for color, cells in by_color.items()
        )


def polygon_cells(pts):
    """Cells whose centres fall inside the polygon (even-odd)."""
    ys = [p[1] for p in pts]
    out = set()
    n = len(pts)
    for y in range(int(min(ys)) - 1, int(max(ys)) + 2):
        yc = y + 0.5
        xs = []
        for i in range(n):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
            if (y0 <= yc < y1) or (y1 <= yc < y0):
                xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for a, b in zip(xs[::2], xs[1::2]):
            for x in range(int(round(a)), int(round(b))):
                out.add((x, y))
    return out


def line_cells(x0, y0, x1, y1):
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err, out = dx + dy, []
    while True:
        out.append((x0, y0))
        if x0 == x1 and y0 == y1:
            return out
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


# -------------------------------------------------------------------- svg doc


def notched(x, y, w, h, n):
    """Rectangle path with n x n pixel notches cut from each corner."""
    if n <= 0:
        return f"M{num(x)} {num(y)}h{num(w)}v{num(h)}h-{num(w)}z"
    return (
        f"M{num(x + n)} {num(y)}h{num(w - 2 * n)}v{num(n)}h{num(n)}v{num(h - 2 * n)}"
        f"h-{num(n)}v{num(n)}h-{num(w - 2 * n)}v-{num(n)}h-{num(n)}v-{num(h - 2 * n)}h{num(n)}z"
    )


def rounded(x, y, w, h, p):
    """Two-step pixel rounding (like a 9-slice game window) with pixel size p."""
    return (
        f"M{num(x + 2 * p)} {num(y)}h{num(w - 4 * p)}v{num(p)}h{num(p)}v{num(p)}h{num(p)}"
        f"v{num(h - 4 * p)}h-{num(p)}v{num(p)}h-{num(p)}v{num(p)}h-{num(w - 4 * p)}"
        f"v-{num(p)}h-{num(p)}v-{num(p)}h-{num(p)}v-{num(h - 4 * p)}h{num(p)}v-{num(p)}h{num(p)}z"
    )


class Doc:
    def __init__(self, w: int, h: int, title: str, desc: str = ""):
        self.w, self.h, self.title, self.desc = w, h, title, desc
        self.body: list[str] = []
        self.defs: list[str] = []
        self.css: list[str] = []

    def add(self, *els: str):
        self.body.extend(els)

    def text(self, fnt: str, text: str, x: float, y: float, fill: str, s: float = 2,
             anchor: str = "start", tracking: int = 0, bold: bool = False,
             cls: str = "", extra: str = "") -> float:
        """Draw pixel text with its baseline at y; returns the drawn width."""
        f = font(fnt)
        cells, w = f.pixels(text, tracking)
        if bold:
            cells, w = embolden(cells), w + 1
        if anchor == "middle":
            x -= round(w * s / 2 / s) * s
        elif anchor == "end":
            x -= w * s
        attr = f' class="{cls}"' if cls else ""
        if cells:
            self.body.append(f'<path fill="{fill}"{attr}{extra} d="{cells_path(cells, s, x, y)}"/>')
        return w * s

    def render(self) -> str:
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" fill="none" role="img" '
            f'aria-labelledby="t d" shape-rendering="crispEdges">'
            f'<title id="t">{escape(self.title)}</title><desc id="d">{escape(self.desc)}</desc>'
        )
        css = ""
        if self.css:
            css = (
                "<style>" + "".join(self.css)
                + "@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>"
            )
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return head + css + defs + "".join(self.body) + "</svg>\n"
