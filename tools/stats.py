"""Pixel 'save data' stats card, rebuilt daily by .github/workflows/profile-data.yml.

    GITHUB_TOKEN=... python3 tools/stats.py --user handsomeZR-netizen --out dist
    python3 tools/stats.py --mock --out /tmp/preview      # layout preview, fake numbers

Writes save-data-light.svg and save-data-dark.svg. If the GitHub API call fails,
it re-uses yesterday's cards from the output branch so the README never shows
a broken image. Standard library only.
"""

import argparse
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pixel import Doc, notched  # noqa: E402
from theme import THEMES  # noqa: E402
from ui import chip, icon, path, window  # noqa: E402

BODY = "pixel-12px"
SKIP_LANGS = {"Jupyter Notebook"}

QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100, after: $cursor) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def graphql(token, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "pixel-profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]


def streaks(days):
    """Current streak (today may still be empty) and longest streak, in days."""
    counts = [d["contributionCount"] for d in sorted(days, key=lambda d: d["date"])]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:
        i -= 1
    current = 0
    while i >= 0 and counts[i]:
        current += 1
        i -= 1
    return current, longest


def collect(user, token):
    cursor, stars, repos, langs, first = None, 0, 0, {}, None
    while True:
        data = graphql(token, {"login": user, "cursor": cursor})
        first = first or data
        conn = data["repositories"]
        repos = conn["totalCount"]
        for node in conn["nodes"]:
            stars += node["stargazerCount"]
            for e in node["languages"]["edges"]:
                name = e["node"]["name"]
                if name not in SKIP_LANGS:
                    langs[name] = langs.get(name, 0) + e["size"]
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]
    cal = first["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    current, longest = streaks(days)
    return {
        "stars": stars,
        "repos": repos,
        "followers": first["followers"]["totalCount"],
        "contribs": cal["totalContributions"],
        "streak": current,
        "best": longest,
        "since": first["createdAt"][:4],
        "langs": sorted(langs.items(), key=lambda kv: -kv[1]),
        "date": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"),
    }


def short(n):
    return f"{n / 1000:.1f}K".replace(".0K", "K") if n >= 10000 else str(n)


def card(th, s):
    W, H = 880, 256
    langs = s["langs"][:5]
    total = sum(v for _, v in s["langs"]) or 1
    desc = (f'{s["stars"]} stars, {s["repos"]} public repos, {s["followers"]} followers, '
            f'{s["contribs"]} contributions in the last year, {s["streak"]}-day streak. Top languages: '
            + ", ".join(f"{k} {v * 100 / total:.0f}%" for k, v in langs))
    d = Doc(W, H, "GitHub stats", desc)
    window(d, th, 0, 0, W - 8, H - 8)
    light = th["name"] == "light"
    tiles = [
        ("star", "gold", short(s["stars"]), "星标", "STARS"),
        ("chest", "peach", short(s["repos"]), "仓库", "REPOS"),
        ("people", "pink", short(s["followers"]), "关注", "FOLLOWERS"),
        ("chart", "teal", short(s["contribs"]), "年度贡献", "1Y"),
        ("flame", "coral", f'{s["streak"]}D', "连续", "STREAK"),
        ("clock", "lav", f'{s["best"]}D', "最长", "BEST"),
    ]
    for i, (ic, col, num, zh, en) in enumerate(tiles):
        x = 24 + (i % 3) * 164
        y = 24 + (i // 3) * 96
        d.add(path(notched(x, y, 44, 44, 2), th[col][0]))
        d.add(icon(ic, th, x + 5, y + 5, s=3, accent=col))
        d.text("arcade-8px", num, x + 56, y + 32, th["text"], s=3)
        zw = d.text(BODY, zh, x, y + 76, th["text2"], s=2)
        d.text("tiny-5px", en, x + zw + 8, y + 74, th["text3"], s=2, tracking=1)
    # languages
    lx, lw = 536, W - 8 - 24 - 536
    d.text("arcade-8px", "TOP LANGS", lx, 44, th["text"], s=2)
    d.text(BODY, "常用语言", lx + 160, 46, th["lav"][1] if light else th["lav"][0], s=2)
    cols = ["lav", "pink", "blue", "teal", "peach"]
    # split the bar into whole 4-unit cells (largest remainder), at least 2 cells each
    cells = lw // 4
    shown = sum(v for _, v in langs) or 1
    raw = [max(2.0, cells * v / shown) for _, v in langs]
    alloc = [int(r) for r in raw]
    for i in sorted(range(len(raw)), key=lambda i: raw[i] - alloc[i], reverse=True)[:max(0, cells - sum(alloc))]:
        alloc[i] += 1
    while sum(alloc) > cells:
        alloc[alloc.index(max(alloc))] -= 1
    bx = lx
    for i, n in enumerate(alloc):
        d.add(path(f"M{bx} 60h{n * 4 - 4}v16h-{n * 4 - 4}z", th[cols[i]][0]))
        bx += n * 4
    for i, (name, v) in enumerate(langs):
        y = 100 + i * 26
        d.add(path(f"M{lx} {y - 14}h12v12h-12z", th[cols[i]][0]))
        d.text(BODY, name, lx + 22, y, th["text"], s=2)
        d.text(BODY, f"{v * 100 / total:.1f}%", lx + lw, y, th["text3"], s=2, anchor="end")
    foot = f'LAST SAVE {s["date"]} UTC   PLAYING SINCE {s["since"]}'
    chip(d, th, 24, H - 8 - 36, foot, th["well"], th["text3"])
    return d.render()


def fallback(user, out):
    """Keep yesterday's cards if today's API call failed."""
    ok = True
    for t in ("light", "dark"):
        url = f"https://raw.githubusercontent.com/{user}/{user}/output/save-data-{t}.svg"
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                (out / f"save-data-{t}.svg").write_bytes(r.read())
        except Exception as e:  # noqa: BLE001
            print(f"fallback for {t} failed: {e}", file=sys.stderr)
            ok = False
    return ok


MOCK = {
    "stars": 128, "repos": 42, "followers": 36, "contribs": 1234, "streak": 12, "best": 47, "since": "2023",
    "langs": [("TypeScript", 52), ("Python", 31), ("TeX", 9), ("JavaScript", 5), ("HTML", 3)],
    "date": "2026-09-25",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "handsomeZR-netizen"))
    ap.add_argument("--out", default="dist")
    ap.add_argument("--mock", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    try:
        stats = MOCK if args.mock else collect(args.user, os.environ["GITHUB_TOKEN"])
    except Exception as e:  # noqa: BLE001
        print(f"stats: API failed ({e}); keeping previous cards", file=sys.stderr)
        if fallback(args.user, out):
            return
        raise
    for th in THEMES:
        (out / f"save-data-{th['name']}.svg").write_text(card(th, stats), encoding="utf-8")
    print(json.dumps({k: v for k, v in stats.items() if k != "langs"}), stats["langs"][:5])


if __name__ == "__main__":
    main()
