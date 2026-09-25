"""Shared pixel-UI pieces: windows with striped title bars, chips, bars, icons."""

from pixel import Canvas, cells_path, dilate, font, notched, rounded

P = 4

# 9x9 icon silhouettes; the ink outline is added automatically.
ICONS = {
    "robot": [
        "....r....",
        "....s....",
        ".sssssss.",
        "ssbbsbbss",
        "ssbbsbbss",
        "sssssssss",
        "ssskkksss",
        ".sssssss.",
    ],
    "chat": [
        ".aaaaaaa.",
        "aaaaaaaaa",
        "aawawawaa",
        "aaaaaaaaa",
        ".aaaaaaa.",
        ".aa......",
        ".a.......",
    ],
    "window": [
        "aaaaaaaaa",
        "arayagaaa",
        "aaaaaaaaa",
        "wwwwwwwww",
        "wwkwwwkww",
        "wkwwwwwkw",
        "wwkwwwkww",
        "wwwwwwwww",
    ],
    "flask": [
        "..sssss..",
        "...sws...",
        "...sws...",
        "..swwws..",
        ".swwwwws.",
        "swtttttws",
        "sttwtttts",
        ".sssssss.",
    ],
    "eye": [
        "...aaa...",
        ".aawwwaa.",
        "awwkkkwwa",
        "awwkwkwwa",
        "awwkkkwwa",
        ".aawwwaa.",
        "...aaa...",
    ],
    "rocket": [
        "....w....",
        "...sss...",
        "...sbs...",
        "...sss...",
        "..rsssr..",
        ".rr.s.rr.",
        "....o....",
        "...ooo...",
        "....o....",
    ],
    "trophy": [
        ".yyyyyyy.",
        "y.wyyyY.y",
        "y.wyyyY.y",
        ".yywyyYy.",
        "...yyY...",
        "....y....",
        "....Y....",
        "..yyyyY..",
        ".yyyyyyY.",
    ],
    "star": [
        "....y....",
        "...yyy...",
        "yyywyyyYY",
        ".yyyyyyY.",
        "..yyyyY..",
        "..yy.yY..",
        ".yY...yY.",
    ],
    "check": [
        ".ttttttt.",
        "ttttttttt",
        "tttttttwt",
        "ttttttwtt",
        "twtttwttt",
        "ttwtwtttt",
        "tttwttttt",
        "ttttttttt",
        ".ttttttt.",
    ],
    "scroll": [
        "wwwwwww..",
        "wwwwwwwP.",
        "wwwwwwwPP",
        "waaaaawww",
        "wwwwwwwww",
        "waaaaaaaw",
        "wwwwwwwww",
        "waaaawwww",
        "wwwwwwwww",
    ],
    "chest": [
        ".nnnnnnn.",
        "nnnnnnnnn",
        "nNNNNNNNn",
        "yyyyyyyyy",
        "nnnnwnnnn",
        "nnnnynnnn",
        "nnnnnnnnn",
        "nNNNNNNNn",
    ],
    "heart": [
        ".rr...rr.",
        "rrrr.rrrr",
        "rwrrrrrrr",
        "rrrrrrrrr",
        ".rrrrrrr.",
        "..rrrrr..",
        "...rrr...",
        "....r....",
    ],
    "shield": [
        "aaaaaaaaa",
        "aaaaaaaaa",
        "aaaaaaawa",
        "aaaaaawaa",
        "awaaawaaa",
        ".awawaaa.",
        "..awaaa..",
        "...aaa...",
        "....a....",
    ],
    "gem": [
        "..ttttt..",
        ".twwtttT.",
        "tttttttTT",
        ".tttttTT.",
        "..tttTT..",
        "...ttT...",
        "....T....",
    ],
    "bolt": [
        ".....yyy.",
        "....yyy..",
        "...yyy...",
        "..yyyyyy.",
        "....yyy..",
        "...yyy...",
        "..yy.....",
        ".y.......",
    ],
    "pencil": [
        ".......pp",
        "......ppp",
        ".....yyp.",
        "....yyy..",
        "...yyy...",
        "..yyy....",
        ".nny.....",
        ".nn......",
        "k........",
    ],
    "circuit": [
        "..s.s.s..",
        ".sssssss.",
        "ssaaaaass",
        ".saawaas.",
        "ssawwwass",
        ".saawaas.",
        "ssaaaaass",
        ".sssssss.",
        "..s.s.s..",
    ],
    "chart": [
        "......tt.",
        "......tt.",
        "...pp.tt.",
        "...pp.tt.",
        "bb.pp.tt.",
        "bb.pp.tt.",
        "bb.pp.tt.",
        "sssssssss",
    ],
    "light": [
        ".sssss.",
        "ssrrrss",
        "ssrrrss",
        "ssyyyss",
        "ssyyyss",
        "ssgggss",
        "ssgggss",
        ".sssss.",
        "...s...",
    ],
    "note": [
        ".s.s.s.s.",
        "wwwwwwwww",
        "wwwwwwwww",
        "waaaaaaaw",
        "wwwwwwwww",
        "waaaaawww",
        "wwwwwwwww",
        "waaaaaaaw",
        "wwwwwwwww",
    ],
    "flame": [
        "....o....",
        "...oo....",
        "...ooo.o.",
        "..oooooo.",
        ".oooyyoo.",
        ".ooyyyyoo",
        "oooyyyyoo",
        ".ooyyyyo.",
        "..ooooo..",
    ],
    "people": [
        "...www...",
        "..wwwww..",
        "..wwwww..",
        "...www...",
        ".........",
        ".wwwwwww.",
        "wwwwwwwww",
        "wwwwwwwww",
    ],
    "sigma": [
        "aaaaaaa",
        "aa.....",
        ".aa....",
        "..aa...",
        "...aa..",
        "..aa...",
        ".aa....",
        "aa.....",
        "aaaaaaa",
    ],
    "mail": [
        "wwwwwwwww",
        "wkwwwwwkw",
        "wwkwwwkww",
        "wwwkwkwww",
        "wwwwkwwww",
        "wwwwwwwww",
        "wwwwwwwww",
    ],
    "clock": [
        "..wwwww..",
        ".wwwawww.",
        "wwwwawwww",
        "wwwwawwww",
        "wwwwaaaww",
        "wwwwwwwww",
        "wwwwwwwww",
        ".wwwwwww.",
        "..wwwww..",
    ],
}


def icon_palette(th, accent="lav"):
    light = th["name"] == "light"
    return {
        "k": "#2A2140" if light else "#0B0818",
        "a": th[accent][0],
        "A": th[accent][1],
        "w": "#FFFFFF" if light else "#F4EEFF",
        "y": "#FFD15C",
        "Y": "#E3A435",
        "s": "#C9CCE2" if light else "#9D98C8",
        "b": "#7FA8F0",
        "r": "#F07C8C",
        "g": "#6ED3A8",
        "t": "#5CCBBE",
        "T": "#3A9F96",
        "p": "#F5A9BE",
        "P": "#D9C9D3",
        "n": "#B98458",
        "N": "#8F6240",
        "o": "#FFA25C",
    }


def icon(name, th, x, y, s=P, accent="lav", outline=True):
    """Render an icon at (x, y) (top-left of the outline box). Returns svg."""
    rows = ICONS[name]
    pal = icon_palette(th, accent)
    cv = Canvas()
    cells = set()
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != ".":
                cells.add((c + 1, r + 1))
    if outline:
        cv.cells(dilate(cells, 1, diagonal=False) - cells, pal["k"])
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != ".":
                cv.set(c + 1, r + 1, pal[ch])
    return cv.export(s, x, y)


def icon_size(name):
    rows = ICONS[name]
    return max(len(r) for r in rows) + 2, len(rows) + 2


def path(d, fill, extra=""):
    return f'<path fill="{fill}"{extra} d="{d}"/>'


def window(d, th, x, y, w, h, shadow=8, fill=None):
    """Pixel window body: shadow, frame (2-step corners), panel fill."""
    if shadow:
        d.add(path(rounded(x + shadow, y + shadow, w, h, P), th["shadow"]))
    d.add(path(rounded(x, y, w, h, P), th["frame"]))
    d.add(path(notched(x + P, y + P, w - 2 * P, h - 2 * P, P), fill or th["panel"]))


def titlebar(d, th, x, y, w, accent, title, zh="", right="", h=40):
    """Classic striped title bar across the top of a window at (x, y, w)."""
    fill, ink = th[accent]
    bx, by, bw = x + P, y + P, w - 2 * P
    d.add(path(notched(bx, by, bw, h, P), fill))
    stripe = ink if th["name"] == "light" else th["frame"]
    rows = "".join(f"M{bx + 2 * P} {by + yy}h{bw - 4 * P}v{P // 2}h-{bw - 4 * P}z" for yy in range(8, h - 6, 6))
    d.add(path(rows, stripe, ' opacity=".28"'))
    d.add(path(f"M{bx} {by + h}h{bw}v{P}h-{bw}z", th["frame"]))
    # title plate
    arcade, zhf = font("arcade-8px"), font("pixel-12px")
    tw = arcade.measure(title) * 2
    zw = zhf.measure(zh) * 2 if zh else 0
    plate_w = 16 + tw + (12 + zw if zh else 0) + 16
    px_, py_ = bx + 20, by + 8
    d.add(path(notched(px_, py_, plate_w, h - 16, 2), th["panel"]))
    d.text("arcade-8px", title, px_ + 16, py_ + 20, th["text"], s=2)
    if zh:
        d.text("pixel-12px", zh, px_ + 16 + tw + 12, py_ + 21, ink if th["name"] == "light" else fill, s=2)
    if right:
        rf = font("tiny-5px")
        rw = rf.measure(right, 1) * 2
        rx = bx + bw - 20 - rw - 16
        d.add(path(notched(rx, py_, rw + 16, h - 16, 2), th["panel"]))
        d.text("tiny-5px", right, rx + 8, py_ + 17, th["text2"], s=2, tracking=1)
    return by + h + P


def chip(d, th, x, y, text, fill, color, h=20, fnt="tiny-5px", s=2, pad=8, tracking=1):
    """Small pill label. (x, y) = top-left. Returns width."""
    f = font(fnt)
    tw = f.measure(text, tracking) * s
    w = tw + 2 * pad
    d.add(path(notched(x, y, w, h, 2), fill))
    base = y + h - (h - 5 * s) // 2 if fnt == "tiny-5px" else y + h - 6
    d.text(fnt, text, x + pad, base, color, s=s, tracking=tracking)
    return w


def chip_width(text, fnt="tiny-5px", s=2, pad=8, tracking=1):
    return font(fnt).measure(text, tracking) * s + 2 * pad


def segbar(d, th, x, y, n, filled, fill, seg=24, gap=4, h=12, empty=None):
    """Segmented pixel bar: n segments, `filled` of them lit."""
    for i in range(n):
        sx = x + i * (seg + gap)
        if i < filled:
            d.add(path(f"M{sx} {y}h{seg}v{h}h-{seg}z", fill))
            d.add(path(f"M{sx} {y}h{seg}v{h // 3}h-{seg}z", "#FFFFFF", ' opacity=".35"'))
        else:
            d.add(path(f"M{sx} {y}h{seg}v{h}h-{seg}z", empty or th["track"]))


def fit(text, fnt, s, max_w, what, tracking=0, bold=False):
    w = font(fnt).measure(text, tracking) * s + (s if bold else 0)
    if w > max_w:
        raise ValueError(f"{what}: '{text}' is {w} units wide, max {max_w}. Shorten it in profile.toml.")
    return w


def cells_svg(cells, fill, s, x, y, extra=""):
    return path(cells_path(cells, s, x, y), fill, extra)
