"""The hero 'title screen': a pixel Nanjing skyline that is day in light mode
and night in dark mode, with a cat coding on the Ming city wall."""

import math
import random

from pixel import Canvas, Doc, dilate, font, rounded, cells_path, shift

P = 4                  # one art pixel = 4 svg units
W, H = 880, 360        # svg size
FW, FH = 872, 352      # frame (shadow sits 8 units down/right)
CW, CH = FW // P, FH // P   # 218 x 88 cells

SKY = {
    "light": [(0, "#A9BEEA"), (16, "#B9CAF0"), (30, "#CAD6F3"), (42, "#DCE1F5"), (52, "#EDE4F2"), (60, "#FAE7EA")],
    "dark": [(0, "#0E0B23"), (16, "#130F30"), (30, "#1A143F"), (42, "#241B52"), (52, "#322262"), (60, "#462B70")],
}

SCENE = {
    "light": {
        "hill": "#CDC2E6", "hill_hi": "#DBD2EE", "dome": "#FFFFFF", "dome_line": "#9D90C6",
        "bld": "#A99DCC", "bld_side": "#978ABF", "win": "#D8E0F7", "win_lit": "#FFFFFF",
        "tower": "#9B8FC4", "tower_side": "#887BB6", "tower_glass": "#C9D3F2",
        "wall": "#978CBE", "wall_hi": "#B2A8D6", "mortar": "#887DB2", "wall_dark": "#7F74AB",
        "roof": "#5B4C8C", "roof_hi": "#7667A8", "hall": "#E8E0F3", "pillar": "#8C7DB9", "hall_win": "#B9AEDA",
        "lantern": "#E8667A", "cloud": "#FFFFFF", "cloud_sh": "#E2E6F7", "cloud_hi": "#FFFFFF",
        "sun": "#FFE6B0", "sun_core": "#FFF5DD", "halo": "#F8EBD9", "ray": "#FFD89A",
        "beacon": "#E8667A",
        "logo_top": "#FFFFFF", "logo_bot": "#FFE0EA", "logo_line": "#2A2140", "logo_shadow": "#E58BA8",
        "zh": "#2A2140", "zh_line": "#FFFFFF", "accent": "#7A62B0", "hud": "#5E5575", "start": "#CF6247",
        "frame": "#2A2140", "shadow": "#D5CAE4",
    },
    "dark": {
        "hill": "#261E4C", "hill_hi": "#30265C", "dome": "#8D82C4", "dome_line": "#5C519A",
        "bld": "#1C163C", "bld_side": "#171233", "win": "#262050", "win_lit": "#FFD38A",
        "tower": "#201A45", "tower_side": "#1A153A", "tower_glass": "#2E2763",
        "wall": "#2A2352", "wall_hi": "#3B3270", "mortar": "#221C46", "wall_dark": "#1D1740",
        "roof": "#120E28", "roof_hi": "#2B2458", "hall": "#2A2250", "pillar": "#1A1538", "hall_win": "#FFC56E",
        "lantern": "#FF6B81", "cloud": "#2A2352", "cloud_sh": "#211B45", "cloud_hi": "#3D3470",
        "sun": "#FFEFCB", "sun_core": "#FFF6E2", "halo": "#221A4E", "ray": "#FFEFCB",
        "beacon": "#FF5C77",
        "logo_top": "#FFF6E4", "logo_bot": "#FFD2A6", "logo_line": "#0B0818", "logo_shadow": "#8B5CF6",
        "zh": "#F4EEFF", "zh_line": "#0B0818", "accent": "#C4B0F6", "hud": "#BDB3DC", "start": "#FFAD97",
        "frame": "#5C4E9E", "shadow": "#06050F",
    },
}

CAT = [
    "..kk........kk..",
    "..kqk......kqk..",
    "..kpqk....kqpk..",
    "..kppqkkkkqppk..",
    ".kqqqqqqqqqqqqk.",
    "kqqqqqqqqqqqqqqk",
    "kqqeeqqqqqqeeqqk",
    "kqqewqqqqqqewqqk",
    "kqbqqqqnnqqqqbqk",
    ".kqqqqkqqkqqqqk.",
    ".kkkkkkkkkkkkkk.",
    "kqqkLLLLLLLLkqqk",
    "kqqkLLLggLLLkqqk",
    ".kkkLLLggLLLkkk.",
    "...kLLLLLLLLk...",
    ".kkkkkkkkkkkkkk.",
    "kbbbbbbbbbbbbbbk",
    ".kkkkkkkkkkkkkk.",
]

CAT_BLINK = {6: "kqqqqqqqqqqqqqqk", 7: "kqqkkqqqqqqkkqqk"}

TAIL = [
    ["kqqk.", "kqqk.", ".kqqk", ".kqqk", ".kqqk", "kqqk.", "kqk..", ".k..."],
    [".kqqk", ".kqqk", ".kqqk", "kqqk.", "kqqk.", "kqqk.", ".kqk.", "..k.."],
]

BIRD = [["k...k", ".k.k.", "..k.."], ["..k..", ".k.k.", "k...k"]]


def sky(cv, bands, x0, x1, y0, y1):
    for i, (start, color) in enumerate(bands):
        end = bands[i + 1][0] if i + 1 < len(bands) else y1
        cv.rect(x0, max(y0, start), x1 - x0, min(end, y1) - max(y0, start), color)
        if i + 1 < len(bands):
            nxt = bands[i + 1][1]
            for x in range(x0, x1):
                if (x + end) % 4 == 0:
                    cv.set(x, end - 2, nxt)
                if (x + end) % 2 == 0:
                    cv.set(x, end - 1, nxt)


def cloud_cells(w, seed):
    rnd = random.Random(seed)
    h = max(5, w // 4)
    cells = set()
    x = 2
    while x < w - 2:
        r = rnd.uniform(h * 0.45, h * 0.8)
        cy = h - r * 0.7
        for yy in range(-2, h):
            for xx in range(int(x - r) - 1, int(x + r) + 2):
                if (xx + 0.5 - x) ** 2 + (yy + 0.5 - cy) ** 2 <= r * r and 0 <= xx < w:
                    cells.add((xx, yy))
        x += rnd.uniform(r * 0.8, r * 1.3)
    base = max(y for _, y in cells)
    return {(x, y) for x, y in cells if y <= base}, base


def ridge(x):
    """Height (cells) of the Purple Mountain ridge above row 72."""
    peaks = [(22, 7, 14), (58, 5, 10), (104, 13, 16), (126, 17, 13), (146, 11, 12), (196, 8, 16)]
    h = 2.0
    for px, ph, pw in peaks:
        h += ph * math.exp(-((x - px) / pw) ** 2)
    return h


def hero(theme, prof):
    t = theme["name"]
    c = SCENE[t]
    rnd = random.Random(7)
    pl = prof["player"]
    d = Doc(W, H, f"{pl['name'].title()} — AI-native builder, Nanjing",
            "Pixel-art title screen: a cat codes on the Nanjing city wall "
            + ("under a pastel day sky." if t == "light" else "under the night sky."))
    d.defs.append(f'<clipPath id="scr"><path d="{rounded(0, 0, FW, FH, P)}"/></clipPath>')
    d.add(f'<path fill="{c["shadow"]}" d="{rounded(8, 8, FW, FH, P)}"/>')
    d.add(f'<path fill="{c["frame"]}" d="{rounded(0, 0, FW, FH, P)}"/>')

    bg = Canvas()
    sky(bg, SKY[t], 1, CW - 1, 1, CH - 1)

    # celestial body
    mx, my = 181, 19
    if t == "dark":
        for x in range(mx - 13, mx + 14):
            for y in range(my - 13, my + 14):
                dd = ((x + .5 - mx) ** 2 + (y + .5 - my) ** 2) ** .5
                if 9 <= dd < 12.5 and (x + y) % 2 == 0:
                    bg.set(x, y, c["halo"])
                elif 12.5 <= dd < 14 and (x + y) % 4 == 0:
                    bg.set(x, y, c["halo"])
        moon = {(x, y) for x in range(mx - 9, mx + 10) for y in range(my - 9, my + 10)
                if (x + .5 - mx) ** 2 + (y + .5 - my) ** 2 <= 64}
        bite = {(x, y) for x, y in moon if (x + .5 - mx + 4) ** 2 + (y + .5 - my + 3) ** 2 <= 46}
        bg.cells(moon - bite, c["sun"])
        bg.cells({(mx + 3, my + 2), (mx + 4, my + 2), (mx + 2, my + 5), (mx + 5, my - 1)} & (moon - bite), "#F2DDB0")
    else:
        for x in range(mx - 14, mx + 15):
            for y in range(my - 14, my + 15):
                dd = ((x + .5 - mx) ** 2 + (y + .5 - my) ** 2) ** .5
                if 9 <= dd < 12 and (x + y) % 2 == 0:
                    bg.set(x, y, c["halo"])
                elif 12 <= dd < 14 and (x + y) % 4 == 0:
                    bg.set(x, y, c["halo"])
        bg.disc(mx, my, 8, c["sun"])
        bg.disc(mx - 1, my - 1, 5.5, c["sun_core"])

    # Purple Mountain + observatory dome
    top_of = {}
    for x in range(1, CW - 1):
        top = 72 - round(ridge(x))
        top_of[x] = top
        bg.rect(x, top, 1, CH - 1 - top, c["hill"])
        bg.set(x, top, c["hill_hi"])
    ox = 126
    oy = top_of[ox]
    bg.rect(ox - 2, oy - 2, 5, 2, c["dome"])
    bg.rect(ox - 1, oy - 3, 3, 1, c["dome"])
    bg.set(ox, oy - 3, c["dome_line"])
    bg.set(ox, oy - 2, c["dome_line"])

    # skyline
    lit_blink = []
    x = 1
    while x < CW - 1:
        w = rnd.randint(6, 12)
        if 138 <= x + w and x <= 158:          # keep room for Zifeng Tower
            x = 159
            continue
        h = rnd.randint(5, 14) if not (60 < x < 110) else rnd.randint(4, 9)
        top = 77 - h
        bg.rect(x, top, w, CH - 1 - top, c["bld"])
        bg.rect(x + w - 2, top, 2, CH - 1 - top, c["bld_side"])
        for wy in range(top + 2, 76, 2):
            for wx in range(x + 1, x + w - 2, 2):
                r = rnd.random()
                if t == "dark" and r < 0.28:
                    bg.set(wx, wy, c["win_lit"])
                    if r < 0.04:
                        lit_blink.append((wx, wy))
                elif r < 0.7:
                    bg.set(wx, wy, c["win"])
        x += w + rnd.choice([0, 0, 1, 2])

    # Zifeng Tower (紫峰大厦)
    tx = 144
    bg.rect(tx, 36, 12, 42, c["tower"])
    bg.rect(tx + 9, 36, 3, 42, c["tower_side"])
    for i, (dx, w) in enumerate([(1, 10), (2, 8), (3, 6), (4, 4)]):
        bg.rect(tx + dx, 35 - i * 2, w, 2, c["tower"])
    bg.rect(tx + 5, 22, 2, 7, c["tower"])
    bg.rect(tx + 6, 18, 1, 4, c["tower"])
    for wy in range(38, 76, 3):
        bg.rect(tx + 1, wy, 8, 1, c["tower_glass"])
        if t == "dark":
            for wx in range(tx + 1, tx + 9):
                if rnd.random() < 0.25:
                    bg.set(wx, wy, c["win_lit"])

    # Ming city wall
    wall_top = 76
    for x in range(1, CW - 1):
        bg.rect(x, wall_top, 1, CH - 1 - wall_top, c["wall"])
        if x % 5 in (0, 1, 2):
            bg.rect(x, wall_top - 2, 1, 2, c["wall"])
            bg.set(x, wall_top - 2, c["wall_hi"])
        else:
            bg.set(x, wall_top, c["wall_hi"])
        for y in range(wall_top + 3, CH - 1, 3):
            bg.set(x, y, c["mortar"])
            if (x + (y // 3) * 3) % 6 == 0:
                bg.set(x, y + 1, c["mortar"])
                bg.set(x, y + 2, c["mortar"])
    bg.rect(1, CH - 3, CW - 2, 2, c["wall_dark"])

    # gate tower (城楼) on the wall
    gx, base = 14, wall_top - 2
    bg.rect(gx + 2, base - 6, 30, 6, c["hall"])
    for px_ in range(gx + 3, gx + 32, 5):
        bg.rect(px_, base - 6, 1, 6, c["pillar"])
    for wx in range(gx + 5, gx + 30, 5):
        bg.rect(wx, base - 5, 2, 3, c["hall_win"])
    bg.rect(gx - 1, base - 9, 36, 3, c["roof"])
    bg.rect(gx - 2, base - 10, 2, 1, c["roof"])
    bg.rect(gx + 34, base - 10, 2, 1, c["roof"])
    bg.rect(gx + 1, base - 9, 32, 1, c["roof_hi"])
    bg.rect(gx + 6, base - 14, 22, 4, c["hall"])
    for px_ in range(gx + 7, gx + 28, 5):
        bg.rect(px_, base - 14, 1, 4, c["pillar"])
    for wx in range(gx + 9, gx + 26, 5):
        bg.rect(wx, base - 13, 2, 2, c["hall_win"])
    bg.rect(gx + 3, base - 17, 28, 3, c["roof"])
    bg.rect(gx + 2, base - 18, 2, 1, c["roof"])
    bg.rect(gx + 30, base - 18, 2, 1, c["roof"])
    bg.rect(gx + 5, base - 17, 24, 1, c["roof_hi"])
    bg.rect(gx + 8, base - 19, 18, 2, c["roof"])
    bg.rect(gx + 7, base - 20, 1, 1, c["roof"])
    bg.rect(gx + 26, base - 20, 1, 1, c["roof"])
    for lx in (gx + 4, gx + 29):
        bg.rect(lx, base - 6, 1, 1, c["pillar"])
        bg.rect(lx - 1 + 1, base - 5, 1, 2, c["lantern"])

    d.add(f'<g clip-path="url(#scr)">{bg.export(P)}')

    # stars (night) twinkle
    if t == "dark":
        stars = Canvas()
        tw = {1: Canvas(), 2: Canvas(), 3: Canvas()}
        placed = 0
        while placed < 70:
            sx, sy = rnd.randint(2, CW - 3), rnd.randint(2, 48)
            if sx < 112 and 9 <= sy <= 54:
                continue
            if (sx - mx) ** 2 + (sy - my) ** 2 < 200:
                continue
            color = rnd.choice(["#FFFFFF", "#CFC4FF", "#FFE7BD", "#9E93D6"])
            k = rnd.randint(0, 5)
            (tw[k] if k in tw else stars).set(sx, sy, color)
            placed += 1
        for sx, sy, k in [(120, 10, 1), (205, 40, 2), (160, 6, 3), (96, 5, 2), (212, 12, 1)]:
            for ddx, ddy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                tw[k].set(sx + ddx, sy + ddy, "#FFFFFF" if (ddx, ddy) == (0, 0) else "#BFB3F7")
        d.add(stars.export(P))
        for k, cv in tw.items():
            d.add(f'<g class="tw{k}">{cv.export(P)}</g>')
        d.css.append(
            "@keyframes tw{0%,100%{opacity:1}50%{opacity:.15}}"
            ".tw1{animation:tw 2.6s steps(2) infinite}.tw2{animation:tw 3.4s steps(2) infinite .9s}"
            ".tw3{animation:tw 4.2s steps(2) infinite 1.7s}"
        )
        # blinking windows
        bl = Canvas()
        bl.cells(lit_blink, "#262050")
        d.add(f'<g class="wb">{bl.export(P)}</g>')
        d.css.append("@keyframes wb{0%,60%{opacity:0}61%,100%{opacity:1}}.wb{animation:wb 7s steps(1) infinite}")
    else:
        rays = {1: Canvas(), 2: Canvas()}
        for i, (dx, dy) in enumerate([(0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]):
            k = 1 if i < 4 else 2
            r0, r1 = (11, 14) if k == 1 else (9, 11)
            for r in range(r0, r1):
                rays[k].set(mx + dx * r - (1 if dx < 0 else 0), my + dy * r - (1 if dy < 0 else 0), c["ray"])
        for k, cv in rays.items():
            d.add(f'<g class="ray{k}">{cv.export(P)}</g>')
        d.css.append(
            "@keyframes ray{0%,49%{opacity:1}50%,100%{opacity:0}}"
            ".ray1{animation:ray 2s steps(1) infinite}.ray2{animation:ray 2s steps(1) infinite -1s}"
        )

    # aviation beacon on Zifeng Tower
    bc = Canvas()
    bc.set(tx + 6, 17, c["beacon"])
    d.add(f'<g class="bcn">{bc.export(P)}</g>')
    d.css.append("@keyframes bcn{0%,70%{opacity:1}71%,100%{opacity:.1}}.bcn{animation:bcn 1.6s steps(1) infinite}")

    # drifting clouds (move one art pixel per step)
    specs = [(34, 30, 11, 230), (22, 118, 6, 170), (28, 70, 41, 260), (18, 200, 29, 200)]
    css = []
    for i, (w, x0, y0, dur) in enumerate(specs):
        cells, base = cloud_cells(w, seed=i + 3)
        cv = Canvas()
        for (cx, cy) in cells:
            color = c["cloud"]
            if cy >= base - 1:
                color = c["cloud_sh"]
            elif (cx, cy - 1) not in cells and t == "dark":
                color = c["cloud_hi"]
            cv.set(cx, cy, color)
        start = -w - 2
        dist = CW + w + 4
        d.add(f'<g class="cl{i}">{cv.export(P, start * P, y0 * P)}</g>')
        frac = (x0 - start) / dist
        css.append(
            f"@keyframes cl{i}{{from{{transform:translateX(0)}}to{{transform:translateX({dist * P}px)}}}}"
            f".cl{i}{{animation:cl{i} {dur}s steps({dist}) infinite {-frac * dur:.1f}s}}"
        )
    d.css.extend(css)

    # the cat (blinking, tail swish) with a glowing laptop
    cx0, cy0 = 190, wall_top - 2 - len(CAT)
    ink = "#2A2140" if t == "light" else "#0B0818"
    pal = {
        "k": ink, "e": ink,
        "q": "#FFF7EE" if t == "light" else "#F4ECFF",
        "p": "#F5A9BE",
        "w": "#FFFFFF",
        "b": "#F7B6C8" if t == "light" else "#E58BB0",
        "n": "#E8789A",
        "L": "#4A4468" if t == "light" else "#39336A",
        "g": "#9FE3DC" if t == "light" else "#8FFFF0",
    }
    deck = {"b": "#CFD2E6" if t == "light" else "#77729F"}
    cat = Canvas()
    cat.sprite(CAT, pal, cx0, cy0)
    cat.sprite(CAT[16:17], {**pal, **deck}, cx0, cy0 + 16)
    d.add(cat.export(P))
    blink = Canvas()
    for r, row in CAT_BLINK.items():
        blink.sprite([row], pal, cx0, cy0 + r)
    d.add(f'<g class="blink">{blink.export(P)}</g>')
    d.css.append("@keyframes blink{0%,92%{opacity:0}93%,97%{opacity:1}98%,100%{opacity:0}}"
                 ".blink{opacity:0;animation:blink 5s steps(1) infinite}")
    for k, frame in enumerate(TAIL):
        tc = Canvas()
        tc.sprite(frame, pal, cx0 + 13, wall_top - 1)
        d.add(f'<g class="tail{k}">{tc.export(P)}</g>')
    d.css.append("@keyframes tail{0%,49%{opacity:1}50%,100%{opacity:0}}"
                 ".tail0{animation:tail 1.8s steps(1) infinite}.tail1{opacity:0;animation:tail 1.8s steps(1) infinite -.9s}")
    # sparks rising from the laptop
    for i, (sx, sy, col) in enumerate([(cx0 - 3, cy0 + 9, "#F5A9BE"), (cx0 - 7, cy0 + 4, "#9FD4D1"),
                                       (cx0 - 2, cy0 + 1, "#FFD66B")]):
        sp = Canvas()
        for ddx, ddy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            sp.set(sx + ddx, sy + ddy, col)
        d.add(f'<g class="spark" style="animation-delay:{-i:.0f}s">{sp.export(P)}</g>')
    d.css.append("@keyframes spark{0%{opacity:0;transform:translateY(0)}15%{opacity:1}"
                 "75%{opacity:1}100%{opacity:0;transform:translateY(-24px)}}"
                 ".spark{animation:spark 3s steps(6) infinite}")

    if t == "light":
        # plum petals (梅花, Nanjing's city flower) drifting down
        for i in range(9):
            px0, py0 = rnd.randint(8, 210), rnd.randint(-6, 30)
            pc = Canvas()
            pc.set(px0, py0, "#F5A9BE" if i % 3 else "#FFFFFF")
            pc.set(px0 + 1, py0, "#F08AAA")
            dur = rnd.uniform(9, 14)
            d.add(f'<g class="petal" style="animation-duration:{dur:.1f}s;animation-delay:{-rnd.uniform(0, dur):.1f}s">'
                  f'{pc.export(P)}</g>')
        d.css.append("@keyframes petal{from{transform:translate(0,0)}to{transform:translate(-120px,280px)}}"
                     ".petal{animation:petal 11s steps(35) infinite}")
        # two birds gliding west
        for i, (bx, by, dur) in enumerate([(120, 27, 70), (131, 22, 70)]):
            g = []
            for k, fr in enumerate(BIRD):
                bc_ = Canvas()
                bc_.sprite(fr, {"k": "#6C60A0"}, bx, by)
                lag = ' style="animation-delay:-.3s"' if i else ""
                g.append(f'<g class="wing{k}"{lag}>{bc_.export(P)}</g>')
            d.add(f'<g class="bird">{"".join(g)}</g>')
        d.css.append("@keyframes bird{from{transform:translateX(420px)}to{transform:translateX(-560px)}}"
                     ".bird{animation:bird 60s steps(245) infinite}"
                     "@keyframes wing{0%,49%{opacity:1}50%,100%{opacity:0}}"
                     ".wing0{animation:wing .8s steps(1) infinite}.wing1{opacity:0;animation:wing .8s steps(1) infinite -.4s}")
    else:
        # a shooting star every few seconds
        ss = Canvas()
        for i, col in enumerate(["#FFFFFF", "#FFFFFF", "#E4DCFF", "#C4B8F5", "#9D8FE0", "#7565C2"]):
            ss.set(150 + i * 2, 6 - i, col)
            ss.set(151 + i * 2, 6 - i, col)
        d.add(f'<g class="ss">{ss.export(P)}</g>')
        d.css.append("@keyframes ss{0%{transform:translate(0,0);opacity:0}1%{opacity:1}"
                     "9%{transform:translate(-200px,100px);opacity:0}100%{transform:translate(-200px,100px);opacity:0}}"
                     ".ss{opacity:0;animation:ss 9s linear infinite 2s}")
    d.add("</g>")

    # ---- title text
    arcade = font("arcade-8px")
    s = 7
    cells, w = arcade.pixels(pl["name"])
    x0, base_y = 48, 104
    outline = dilate(cells, 1)
    d.add(f'<path fill="{c["logo_shadow"]}" d="{cells_path(shift(outline, 1, 1), s, x0, base_y)}"/>')
    d.add(f'<path fill="{c["logo_line"]}" d="{cells_path(outline, s, x0, base_y)}"/>')
    top_half = {(x, y) for x, y in cells if y < -4}
    d.add(f'<path fill="{c["logo_top"]}" d="{cells_path(top_half, s, x0, base_y)}"/>')
    d.add(f'<path fill="{c["logo_bot"]}" d="{cells_path(cells - top_half, s, x0, base_y)}"/>')

    # role, outlined so it reads over the sky
    rc, rw = arcade.pixels(pl["title"])
    rx, ry = 51, 150
    d.add(f'<path fill="{c["zh_line"]}" d="{cells_path(dilate(rc, 1) - rc, 3, rx, ry)}"/>')
    d.add(f'<path fill="{c["accent"]}" d="{cells_path(rc, 3, rx, ry)}"/>')
    # school line
    zh = font("pixel-12px")
    sc, sw = zh.pixels(pl["school"])
    if sw * 2 > 470:
        raise ValueError(f"player.school is too wide for the title screen: {pl['school']}")
    d.add(f'<path fill="{c["zh_line"]}" d="{cells_path(dilate(sc, 1) - sc, 2, 54, 180)}"/>')
    d.add(f'<path fill="{c["zh"]}" d="{cells_path(sc, 2, 54, 180)}"/>')

    d.text("arcade-8px", "PRESS START", 84, 208, c["start"], s=2, cls="blinkt")
    d.text("pixel-12px", "▶", 54, 210, c["start"], s=2, cls="blinkt")
    d.css.append("@keyframes bt{0%,55%{opacity:1}56%,100%{opacity:0}}.blinkt{animation:bt 1.2s steps(1) infinite}")

    d.text("tiny-5px", f"PLAYER 1  {pl['name']}", 24, 30, c["hud"], s=2)
    d.text("tiny-5px", "NANJING  32.06N 118.79E", FW - 24, 30, c["hud"], s=2, anchor="end")
    return d.render()
