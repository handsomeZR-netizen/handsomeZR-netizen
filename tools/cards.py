"""README panels: dialog, status, quest cards, inventory, achievements, headers, footer."""

import math
import random

from pixel import (Canvas, Doc, cells_path, dilate, font, line_cells, notched, polygon_cells, rounded,
                   shift)
from scene import CAT, SCENE, SKY, sky
from ui import (P, chip, chip_width, fit, icon, icon_size, path, segbar, titlebar, window)

WIDE = 880
BODY = "pixel-12px"

PORTRAIT = CAT[:10] + [
    ".kkkkkkkkkkkkkk.",
    "kcccccwccwccccck",
    "kccccccwwcccccck",
    "kcccccccccccccck",
]


def _pal(th):
    light = th["name"] == "light"
    ink = "#2A2140" if light else "#0B0818"
    return {
        "k": ink, "e": ink,
        "q": "#FFF7EE" if light else "#F4ECFF",
        "p": "#F5A9BE", "w": "#FFFFFF",
        "b": "#F7B6C8" if light else "#E58BB0",
        "n": "#E8789A",
        "c": th["lav"][0],
    }


# ------------------------------------------------------------------ dialog


def dialog(th, prof):
    dlg = prof["dialog"]
    h = 256
    d = Doc(WIDE, h, "Ziray says hello", " / ".join(dlg["lines"] + [dlg["seeking"]]))
    fill, ink = th["pink"]
    light = th["name"] == "light"
    top = 22
    window(d, th, 0, top, WIDE - 8, h - top - 8)
    # inner rule, like a classic RPG text box
    d.add(path(rounded(10, top + 10, WIDE - 28, h - top - 28, 2), th["line"]))
    d.add(path(notched(12, top + 12, WIDE - 32, h - top - 32, 2), th["panel"]))

    # speaker tab
    sp = dlg["speaker"]
    sw = font(BODY).measure(sp) * 2 + 32
    window(d, th, 28, 0, sw, 40, shadow=0, fill=fill)
    d.text(BODY, sp, 44, 28, th["text"] if light else "#15122A", s=2)

    # portrait
    px, py, pw = 32, top + 34, 148
    d.add(path(rounded(px, py, pw, pw, P), th["frame"]))
    d.add(path(notched(px + P, py + P, pw - 2 * P, pw - 2 * P, P), th["well"]))
    cv = Canvas()
    cv.sprite(PORTRAIT, _pal(th))
    s = 8
    d.add(cv.export(s, px + (pw - 16 * s) // 2, py + pw - 4 - len(PORTRAIT) * s))
    blink = Canvas()
    blink.sprite(["kqqqqqqqqqqqqqqk", "kqqkkqqqqqqkkqqk"], _pal(th), 0, 6)
    d.add(f'<g class="blink">{blink.export(s, px + (pw - 16 * s) // 2, py + pw - 4 - len(PORTRAIT) * s)}</g>')
    d.css.append("@keyframes blink{0%,92%{opacity:0}93%,97%{opacity:1}98%,100%{opacity:0}}"
                 ".blink{opacity:0;animation:blink 4.5s steps(1) infinite}")

    # typed lines
    f = font(BODY)
    tx, ty, lh = 212, top + 58, 36
    t = 0.4
    lines = [(ln, th["text"]) for ln in dlg["lines"]] + [("▶ " + dlg["seeking"], th["coral"][1])]
    for i, (ln, color) in enumerate(lines):
        fit(ln, BODY, 2, WIDE - 8 - tx - 40, "dialog line")
        base = ty + i * lh + (8 if i == len(lines) - 1 else 0)
        pen = tx
        for ch in ln:
            g = f.glyph(ch)
            if ch != " ":
                cells, _ = f.pixels(ch)
                d.add(path(cells_path(cells, 2, pen, base), color, f' class="ty" style="animation-delay:{t:.2f}s"'))
                t += 0.035
            pen += g.adv * 2
        t += 0.25
    d.css.append("@keyframes ty{from{opacity:0}to{opacity:0}}.ty{animation:ty .01s backwards}")
    # blinking "next" arrow
    arrow = Canvas()
    for r, row in enumerate(["kkkkkkk", ".kkkkk.", "..kkk..", "...k..."]):
        for c, ch in enumerate(row):
            if ch == "k":
                arrow.set(c, r, ink)
    d.add(f'<g class="nx" style="animation-delay:{t:.1f}s">{arrow.export(3, WIDE - 8 - 58, h - 8 - 44)}</g>')
    d.css.append("@keyframes nx{0%,49%{opacity:1}50%,100%{opacity:0}}.nx{animation:nx 1s steps(1) infinite}")
    return d.render()


# ------------------------------------------------------------------ status


def status(th, prof):
    abil = prof["ability"]
    h = 432
    desc = "; ".join(f'{a["code"]} {a["name"]} Lv.{a["level"]} ({a["keywords"]})' for a in abil)
    d = Doc(WIDE, h, "Status — abilities", desc)
    window(d, th, 0, 0, WIDE - 8, h - 8)
    body_top = titlebar(d, th, 0, 0, WIDE - 8, "lav", "STATUS", "能力面板",
                        right="CLASS  " + prof["status"]["class"])

    # --- hexagon radar
    cx, cy, R = 164, body_top + 196, 118          # svg units
    gcx, gcy, gr = cx / P, cy / P, R / P          # cells
    n = len(abil)
    ang = [-math.pi / 2 + i * 2 * math.pi / n for i in range(n)]

    def vert(i, frac):
        return gcx + math.cos(ang[i]) * gr * frac, gcy + math.sin(ang[i]) * gr * frac

    grid = Canvas()
    for k, frac in enumerate((0.2, 0.4, 0.6, 0.8, 1.0)):
        pts = [vert(i, frac) for i in range(n)]
        for i in range(n):
            for j, c in enumerate(line_cells(*pts[i], *pts[(i + 1) % n])):
                if frac == 1.0 or j % 2 == 0:
                    grid.set(c[0], c[1], th["line"] if frac < 1 else th["text3"])
    for i in range(n):
        for j, c in enumerate(line_cells(gcx, gcy, *vert(i, 1.0))):
            if j % 2 == 0:
                grid.set(c[0], c[1], th["line"])
    d.add(grid.export(P))

    data = [vert(i, a["level"] / 10) for i, a in enumerate(abil)]
    fill, ink = th["lav"]
    area = Canvas()
    area.cells(polygon_cells([(x + 0.5, y + 0.5) for x, y in data]), th["radar"])
    for i in range(n):
        for c in line_cells(*data[i], *data[(i + 1) % n]):
            area.set(c[0], c[1], ink)
    d.add(f'<g class="pulse">{area.export(P)}</g>')
    d.css.append("@keyframes pulse{0%,100%{opacity:1}50%{opacity:.8}}.pulse{animation:pulse 3s steps(3) infinite}")
    for i, a in enumerate(abil):
        x, y = data[i]
        dot = Canvas()
        dot.rect(round(x) - 1, round(y) - 1, 3, 3, th[a["color"]][1])
        dot.set(round(x) - 1, round(y) - 1, th[a["color"]][0])
        d.add(dot.export(P))
        lx, ly = vert(i, 1.0)
        lx, ly = lx * P + math.cos(ang[i]) * 34, ly * P + math.sin(ang[i]) * 24
        code = a["code"]
        tw = font("arcade-8px").measure(code) * 2
        d.text("arcade-8px", code, round(lx - tw / 2), round(ly + 8), th[a["color"]][1], s=2)

    # --- ability rows
    x0, y0, row_h = 320, body_top + 18, 60
    kw_x = x0 + 48
    for i, a in enumerate(abil):
        y = y0 + i * row_h
        fill, ink = th[a["color"]]
        d.add(path(notched(x0, y, 36, 36, 2), fill))
        d.add(icon(a["icon"], th, x0 + 2, y + 2, s=3, accent=a["color"]))
        fit(a["name"], BODY, 2, 230, "ability name", bold=True)
        d.text(BODY, a["name"], kw_x, y + 20, th["text"], s=2, bold=True)
        nw = font(BODY).measure(a["name"]) * 2 + 2
        chip(d, th, kw_x + nw + 10, y + 4, a["code"], fill, "#15122A" if th["name"] == "dark" else th["text"])
        segbar(d, th, 636, y + 6, 10, a["level"], fill, seg=12, gap=4, h=14)
        d.text("arcade-8px", f'LV{a["level"]}', WIDE - 8 - 24, y + 20, ink, s=2, anchor="end")
        fit(a["keywords"], BODY, 2, WIDE - 8 - 24 - kw_x, "ability keywords")
        d.text(BODY, a["keywords"], kw_x, y + 46, th["text2"], s=2)
    return d.render()


# ------------------------------------------------------------------ quests


def quest(th, q, idx, abil_color):
    main = q["kind"] == "main"
    w, h = 432, (252 if main else 184)
    colors = [abil_color[s] for s in q["skills"]]
    fill, ink = th[colors[0]]
    light = th["name"] == "light"
    label = "MAIN QUEST" if main else "SIDE QUEST"
    d = Doc(w, h, f'{q["repo"]} — {q["zh"]}', q.get("desc", ""))
    window(d, th, 0, 0, w - 8, h - 8)
    iw = w - 8
    # band
    d.add(path(notched(P, P, iw - 2 * P, 36, P), fill))
    d.add(path(f"M{P} {P + 36}h{iw - 2 * P}v{P}h-{iw - 2 * P}z", th["frame"]))
    band_ink = th["text"] if light else "#15122A"
    d.add(path(notched(12, 10, 28, 28, 2), th["panel"]))
    d.add(icon(q["icon"], th, 15, 13, s=2, accent=colors[0]))
    lx = 50
    if main:
        dot = Canvas()
        dot.rect(0, 0, 2, 2, band_ink)
        d.add(f'<g class="live">{dot.export(3, lx, 18)}</g>')
        d.css.append("@keyframes live{0%,59%{opacity:1}60%,100%{opacity:0}}.live{animation:live 1.2s steps(1) infinite}")
        lx += 14
    d.text("tiny-5px", f"{label}  Q{idx:02d}", lx, 29, band_ink, s=2, tracking=1)
    # skills this quest trains, right side of the band
    sx = iw - 12
    for s_, col in reversed(list(zip(q["skills"], colors))):
        sw = chip_width("+" + s_, pad=7)
        sx -= sw
        chip(d, th, sx, 14, "+" + s_, th["panel"], th[col][1] if light else th[col][0], pad=7)
        sx -= 5
    # body
    tx, maxw = 18, iw - 36
    fit(q["repo"], BODY, 2, maxw, "quest title", bold=True)
    d.text(BODY, q["repo"], tx, 72, th["text"], s=2, bold=True)
    fit(q["zh"], BODY, 2, maxw, "quest subtitle")
    d.text(BODY, q["zh"], tx, 100, ink, s=2)
    lines = font(BODY).wrap(q["desc"], maxw // 2)
    if len(lines) > (2 if main else 1):
        raise ValueError(f'quest {q["repo"]}: desc needs {len(lines)} lines, max {2 if main else 1}: {q["desc"]}')
    for i, ln in enumerate(lines):
        d.text(BODY, ln, tx, 128 + i * 26, th["text2"], s=2)
    # footer: tech chips on the left, reward on the right
    cy = h - 8 - 40
    right = tx + maxw
    reward = q.get("reward")
    if reward:
        fit(reward, BODY, 2, maxw - 30, "quest reward")
        rw = 22 + 8 + font(BODY).measure(reward) * 2
        if main:                      # own line above the chips
            rx, ry = tx, cy - 34
        else:                         # shares the chip row, right-aligned
            rx, ry = right - rw, cy
            right = rx - 10
        d.add(icon("trophy" if "奖" in reward else "star", th, rx, ry - 1, s=2))
        d.text(BODY, reward, rx + 30, ry + 19, th["gold"][1], s=2)
    cx = tx
    for tag in q["tags"]:
        cw = chip_width(tag.upper(), pad=7)
        if cx + cw > right:
            print(f"  note: {q['repo']}: tag '{tag}' dropped (no room)")
            continue
        cx += chip(d, th, cx, cy, tag.upper(), th["well"], th["text2"], pad=7) + 5
    return d.render()


# ------------------------------------------------------------------ headers


def header(th, title, zh, right, accent, h=64):
    d = Doc(WIDE, h, f"{title} · {zh}")
    window(d, th, 0, 0, WIDE - 8, h - 8)
    titlebar(d, th, 0, 0, WIDE - 8, accent, title, zh, right=right, h=h - 8 - 2 * P)
    return d.render()


# ------------------------------------------------------------------ inventory


def inventory(th, prof):
    cats = prof["inventory"]
    f = font(BODY)
    x_items, right = 196, WIDE - 8 - 24
    ch_h, gap, row_gap = 30, 8, 12
    # layout pass
    rows = []
    y = 0
    for cat in cats:
        x, lines = x_items, 1
        placed = []
        for it in cat["items"]:
            star = it.endswith("*")
            name = it.rstrip("*")
            w = f.measure(name) * 2 + 24 + (20 if star else 0)
            if x + w > right:
                x, lines = x_items, lines + 1
            placed.append((name, star, x, lines - 1, w))
            x += w + gap
        rows.append((cat, placed, lines))
    total_lines = sum(r[2] for r in rows)
    body_top = 56
    h = body_top + 20 + total_lines * (ch_h + gap) + (len(rows) - 1) * row_gap + 28
    n_items = sum(len(c["items"]) for c in cats)
    desc = "; ".join(f'{c["code"]}: ' + ", ".join(i.rstrip("*") for i in c["items"]) for c in cats)
    d = Doc(WIDE, h, "Inventory — tech stack", desc)
    window(d, th, 0, 0, WIDE - 8, h - 8)
    titlebar(d, th, 0, 0, WIDE - 8, "teal", "INVENTORY", "装备栏", right=f"{n_items} ITEMS")
    y = body_top + 20
    for cat, placed, lines in rows:
        fill, ink = th[cat["color"]]
        # category label
        d.add(path(notched(24, y, 156, ch_h, 2), th["well"]))
        d.add(path(f"M24 {y}h6v{ch_h}h-6z", fill))
        d.text("tiny-5px", cat["code"], 40, y + 20, ink, s=2, tracking=1)
        cw = font("tiny-5px").measure(cat["code"], 1) * 2
        d.text(BODY, cat["name"], 40 + cw + 10, y + 22, th["text2"], s=2)
        for name, star, x, line, w in placed:
            yy = y + line * (ch_h + gap)
            d.add(path(notched(x, yy, w, ch_h, 2), th["chip_line"]))
            d.add(path(notched(x + 2, yy + 2, w - 4, ch_h - 4, 2), th["panel2"]))
            d.add(path(f"M{x + 10} {yy + 12}h6v6h-6z", fill))
            tx = x + 22
            if star:
                star_c = Canvas()
                for r_, row in enumerate(["..y..", "yyyyy", ".yyy.", ".y.y."]):
                    for c_, chh in enumerate(row):
                        if chh == "y":
                            star_c.set(c_, r_, th["gold"][0] if th["name"] == "dark" else "#E3A435")
                d.add(star_c.export(3, tx - 2, yy + 9))
                tx += 18
            d.text(BODY, name, tx, yy + 22, th["text"], s=2)
        y += lines * (ch_h + gap) + row_gap
    return d.render()


# ------------------------------------------------------------------ achievements


def achievements(th, prof):
    ach = prof["achievement"]
    cols, cell_w, cell_h = 2, 412, 76
    rows_n = (len(ach) + cols - 1) // cols
    body_top = 56
    h = body_top + 20 + rows_n * cell_h + 16
    d = Doc(WIDE, h, "Achievements", "; ".join(f'{a["title"]} — {a["sub"]}' for a in ach))
    window(d, th, 0, 0, WIDE - 8, h - 8)
    titlebar(d, th, 0, 0, WIDE - 8, "peach", "ACHIEVEMENTS", "成就", right=f"{len(ach)}/{len(ach)} UNLOCKED")
    for i, a in enumerate(ach):
        x = 24 + (i % cols) * (cell_w + 12)
        y = body_top + 20 + (i // cols) * cell_h
        tile = 60
        d.add(path(rounded(x, y, tile, tile, 2), th["frame"] if th["name"] == "light" else th["line"]))
        d.add(path(notched(x + 3, y + 3, tile - 6, tile - 6, 2), th["well"]))
        iw, ih = icon_size(a["icon"])
        s = 4
        d.add(icon(a["icon"], th, x + (tile - iw * s) // 2, y + (tile - ih * s) // 2, s=s, accent="lav"))
        # shine sweep
        d.defs.append(f'<clipPath id="tile{i}"><path d="{notched(x + 3, y + 3, tile - 6, tile - 6, 2)}"/></clipPath>')
        d.add(f'<g clip-path="url(#tile{i})"><path class="shine" style="animation-delay:{i * 0.35:.2f}s" '
              f'fill="#FFFFFF" opacity=".55" d="M{x - 30} {y}h8l-24 {tile}h-8z"/></g>')
        tx = x + tile + 16
        fit(a["title"], BODY, 2, cell_w - tile - 20, "achievement title", bold=True)
        d.text(BODY, a["title"], tx, y + 26, th["text"], s=2, bold=True)
        fit(a["sub"], BODY, 2, cell_w - tile - 20, "achievement sub")
        d.text(BODY, a["sub"], tx, y + 54, th["text3"], s=2)
    d.css.append("@keyframes shine{0%{transform:translateX(0)}30%,100%{transform:translateX(130px)}}"
                 ".shine{animation:shine 4s steps(12) infinite}")
    return d.render()


# ------------------------------------------------------------------ footer + buttons


def footer(th, prof):
    t = th["name"]
    c = SCENE[t]
    h = 208
    d = Doc(WIDE, h, "Thanks for playing", "Thanks for playing — continue?")
    fw, fh = WIDE - 8, h - 8
    d.defs.append(f'<clipPath id="ft"><path d="{rounded(0, 0, fw, fh, P)}"/></clipPath>')
    d.add(path(rounded(8, 8, fw, fh, P), c["shadow"]))
    d.add(path(rounded(0, 0, fw, fh, P), c["frame"]))
    cv = Canvas()
    cw, chh = fw // P, fh // P
    bands = [(0, SKY[t][2][1]), (18, SKY[t][3][1]), (30, SKY[t][4][1]), (40, SKY[t][5][1])]
    sky(cv, bands, 1, cw - 1, 1, chh - 1)
    rnd = random.Random(11)
    x = 1
    while x < cw - 1:
        w = rnd.randint(5, 11)
        top = chh - 1 - rnd.randint(4, 10)
        cv.rect(x, top, w, chh - 1 - top, c["bld"])
        cv.rect(x + w - 2, top, 2, chh - 1 - top, c["bld_side"])
        for wy in range(top + 2, chh - 3, 2):
            for wx in range(x + 1, x + w - 2, 2):
                r = rnd.random()
                if t == "dark" and r < 0.3:
                    cv.set(wx, wy, c["win_lit"])
                elif r < 0.6:
                    cv.set(wx, wy, c["win"])
        x += w + rnd.choice([0, 1, 2])
    for x in range(1, cw - 1):
        cv.rect(x, chh - 4, 1, 3, c["wall"])
        cv.set(x, chh - 4, c["wall_hi"])
    if t == "dark":
        for _ in range(30):
            sx, sy = rnd.randint(2, cw - 3), rnd.randint(2, 26)
            cv.set(sx, sy, rnd.choice(["#FFFFFF", "#CFC4FF", "#FFE7BD"]))
    d.add(f'<g clip-path="url(#ft)">{cv.export(P)}</g>')
    title = "THANKS FOR PLAYING!"
    arc = font("arcade-8px")
    cells, w = arc.pixels(title)
    s = 3
    x0 = (fw - w * s) // 2
    outline = dilate(cells, 1)
    d.add(path(cells_path(shift(outline, 1, 1), s, x0, 70), c["logo_shadow"]))
    d.add(path(cells_path(outline, s, x0, 70), c["logo_line"]))
    d.add(path(cells_path(cells, s, x0, 70), c["logo_top"]))
    sub = "CONTINUE?"
    sw = arc.measure(sub) * 2
    d.text("arcade-8px", sub, (fw - sw) // 2 - 40, 112, c["hud"], s=2)
    for i in range(10):
        n = str(9 - i)
        d.text("arcade-8px", n, (fw + sw) // 2 - 22, 112, c["start"], s=2, cls=f"cd cd{i}",
               extra=f' style="animation-delay:{i}s"')
    d.css.append("@keyframes cd{0%,9.99%{opacity:1}10%,100%{opacity:0}}.cd{opacity:0;animation:cd 10s steps(1) infinite}"
                 "@media (prefers-reduced-motion: reduce){.cd0{opacity:1}}")
    mot = prof["player"]["motto"]
    mw = font("tiny-5px").measure(mot, 1) * 2
    d.text("tiny-5px", mot, (fw - mw) // 2, 140, c["hud"], s=2, tracking=1)
    return d.render()


def button(th, text, zh, icon_name, accent):
    fill, ink = th[accent]
    f = font(BODY)
    arc = font("arcade-8px")
    tw = arc.measure(text) * 2 + (f.measure(zh) * 2 + 12 if zh else 0)
    w = 20 + 36 + 12 + tw + 24 + 8
    h = 64
    d = Doc(w, h, f"{text} {zh}")
    d.add(path(rounded(6, 6, w - 6, h - 6, P), th["shadow"]))
    d.add(path(rounded(0, 0, w - 6, h - 6, P), th["frame"]))
    d.add(path(notched(P, P, w - 6 - 2 * P, h - 6 - 2 * P, P), fill))
    d.add(path(f"M{2 * P} {P}h{w - 6 - 4 * P}v{P}h-{w - 6 - 4 * P}z", "#FFFFFF", ' opacity=".45"'))
    iw, ih = icon_size(icon_name)
    d.add(icon(icon_name, th, 20, (h - 6 - ih * 3) // 2, s=3, accent=accent))
    txt = th["text"] if th["name"] == "light" else "#15122A"
    x = 20 + iw * 3 + 12
    d.text("arcade-8px", text, x, 38, txt, s=2)
    if zh:
        d.text(BODY, zh, x + arc.measure(text) * 2 + 12, 40, txt, s=2)
    return d.render()
