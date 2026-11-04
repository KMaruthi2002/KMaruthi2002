#!/usr/bin/env python3
"""Render assets/stats.svg, a HUD-style telemetry panel, from the GitHub GraphQL API.

Needs GITHUB_TOKEN in the environment (the Actions token is enough for public data).
Run from the repo root:  GITHUB_TOKEN=... python3 tools/build_stats.py
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

LOGIN = os.environ.get("PROFILE_LOGIN", "KMaruthi2002")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
OUT = Path(__file__).resolve().parent.parent / "assets" / "stats.svg"

FONT = "'JetBrains Mono','Fira Code','SFMono-Regular',Menlo,Consolas,'Liberation Mono',monospace"
BG, PANEL, BORDER = "#070a0f", "#0b1118", "#1b2a38"
INK, DIM, MUTE, CYAN, PINK, AMBER, GREEN = "#e6f7ff", "#9fb3c8", "#5b7a8c", "#00f0ff", "#ff2d95", "#f2a93b", "#39ff14"
SKIP_LANGS = {"Jupyter Notebook", "HTML", "CSS", "Batchfile", "Procfile", "Dockerfile", "Shell"}

QUERY = """
query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login) {
    createdAt
    followers { totalCount }
    repositories(first:100, ownerAffiliations:OWNER, isFork:false, privacy:PUBLIC,
                 orderBy:{field:PUSHED_AT, direction:DESC}) {
      totalCount
      nodes {
        stargazerCount
        languages(first:10, orderBy:{field:SIZE, direction:DESC}) { edges { size node { name color } } }
      }
    }
    contributionsCollection(from:$from, to:$to) {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def gql(query: str, variables: dict) -> dict:
    if not TOKEN:
        sys.exit("GITHUB_TOKEN is not set")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json",
                 "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.load(r)
    if "errors" in body:
        sys.exit(f"GraphQL errors: {body['errors']}")
    return body["data"]["user"]


def streaks(days: list[tuple[dt.date, int]]) -> tuple[int, int, tuple[dt.date, dt.date] | None]:
    longest, run, best_span, start = 0, 0, None, None
    for d, c in days:
        if c > 0:
            run += 1
            start = start or d
            if run > longest:
                longest, best_span = run, (start, d)
        else:
            run, start = 0, None
    # current streak: today may still be empty, so allow it to be skipped
    cur = 0
    seq = [c for _, c in days]
    i = len(seq) - 1
    if seq and seq[i] == 0:
        i -= 1
    while i >= 0 and seq[i] > 0:
        cur += 1
        i -= 1
    return cur, longest, best_span


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt(n: int) -> str:
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)


def main() -> None:
    now = dt.datetime.now(dt.timezone.utc)
    u = gql(QUERY, {"login": LOGIN, "from": (now - dt.timedelta(days=365)).isoformat(),
                    "to": now.isoformat()})
    cc = u["contributionsCollection"]
    days = [(dt.date.fromisoformat(d["date"]), d["contributionCount"])
            for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    days.sort()
    cur, longest, span = streaks(days)
    commits = cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
    stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
    since = dt.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00")).year

    langs: dict[str, tuple[int, str]] = {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            if n in SKIP_LANGS:
                continue
            size, color = langs.get(n, (0, e["node"]["color"] or CYAN))
            langs[n] = (size + e["size"], color)
    total = sum(s for s, _ in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:5]

    last = days[-56:]
    peak = max((c for _, c in last), default=1) or 1

    # ---- layout ------------------------------------------------------------
    W, H = 1200, 300
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
           f'<title>GitHub telemetry for {esc(LOGIN)}</title>',
           '<defs>',
           '<filter id="g" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
           '<pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity="0.22"/></pattern>',
           f'<linearGradient id="bar" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#0aa6c0"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>',
           '</defs>',
           f'<rect width="{W}" height="{H}" rx="12" fill="{BG}"/>',
           f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{BORDER}"/>',
           f'<g fill="none" stroke="{CYAN}" stroke-width="2" opacity="0.85"><path d="M18 36V18H36"/><path d="M{W-36} 18H{W-18}V36"/><path d="M18 {H-36}V{H-18}H36"/><path d="M{W-18} {H-36}V{H-18}H{W-36}"/></g>',
           f'<text x="48" y="40" font-size="11" letter-spacing="3" fill="{MUTE}">TELEMETRY // {esc(LOGIN.upper())}</text>',
           f'<text x="{W-48}" y="40" font-size="10" letter-spacing="2" fill="{MUTE}" text-anchor="end">UPDATED {now.strftime("%Y-%m-%d %H:%M")} UTC · PUBLIC DATA</text>',
           f'<line x1="48" y1="52" x2="{W-48}" y2="52" stroke="#13202c"/>']

    # left: readouts grid
    readouts = [
        ("CONTRIBUTIONS · 365D", fmt(cc["contributionCalendar"]["totalContributions"]), CYAN),
        ("COMMITS · 365D", fmt(commits), CYAN),
        ("STARS", fmt(stars), AMBER),
        ("PUBLIC REPOS", str(u["repositories"]["totalCount"]), AMBER),
        ("CURRENT STREAK", f"{cur}d", PINK),
        ("LONGEST STREAK", f"{longest}d", PINK),
    ]
    for i, (label, val, col) in enumerate(readouts):
        x = 48 + (i % 2) * 190
        y = 100 + (i // 2) * 68
        out.append(f'<text x="{x}" y="{y}" font-size="30" font-weight="700" fill="{col}" filter="url(#g)">{esc(val)}</text>')
        out.append(f'<text x="{x}" y="{y+18}" font-size="9" letter-spacing="2" fill="{MUTE}">{esc(label)}</text>')
    if span:
        out.append(f'<text x="48" y="{H-26}" font-size="9" letter-spacing="2" fill="{MUTE}">LONGEST {span[0].strftime("%b %d").upper()} → {span[1].strftime("%b %d").upper()} · FOLLOWERS {u["followers"]["totalCount"]} · SINCE {since}</text>')

    # middle: last 56 days sparkline
    sx, sy, sw, sh = 450, 80, 330, 160
    out.append(f'<text x="{sx}" y="{sy-10}" font-size="9" letter-spacing="2" fill="{MUTE}">LAST 56 DAYS · PEAK {peak}/DAY</text>')
    out.append(f'<line x1="{sx}" y1="{sy+sh}" x2="{sx+sw}" y2="{sy+sh}" stroke="#13202c"/>')
    bw = sw / len(last) if last else sw
    for i, (d, c) in enumerate(last):
        h = max(2, round(sh * c / peak)) if c else 2
        x = sx + i * bw
        col = "url(#bar)" if c else "#13202c"
        out.append(f'<g transform="translate({x:.1f} {sy+sh})"><rect x="0.5" y="-{h}" width="{bw-1.2:.1f}" height="{h}" fill="{col}">'
                   f'<animateTransform attributeName="transform" type="scale" values="1 0;1 1" dur="0.9s" begin="{i*0.02:.2f}s" fill="freeze"/></rect></g>')
    out.append(f'<text x="{sx}" y="{sy+sh+16}" font-size="9" fill="{MUTE}">{last[0][0].strftime("%b %d").upper() if last else ""}</text>')
    out.append(f'<text x="{sx+sw}" y="{sy+sh+16}" font-size="9" fill="{MUTE}" text-anchor="end">{last[-1][0].strftime("%b %d").upper() if last else ""}</text>')

    # right: languages
    lx, ly, lw = 840, 80, 312
    out.append(f'<text x="{lx}" y="{ly-10}" font-size="9" letter-spacing="2" fill="{MUTE}">LANGUAGES · PUBLIC REPOS · NOTEBOOKS EXCLUDED</text>')
    for i, (name, (size, color)) in enumerate(top):
        pct = 100 * size / total
        y = ly + 12 + i * 34
        w = max(4, round(lw * pct / 100))
        out.append(f'<text x="{lx}" y="{y+4}" font-size="11" fill="{DIM}">{esc(name)}</text>')
        out.append(f'<text x="{lx+lw}" y="{y+4}" font-size="11" fill="{INK}" text-anchor="end">{pct:.1f}%</text>')
        out.append(f'<rect x="{lx}" y="{y+10}" width="{lw}" height="5" rx="2.5" fill="#13202c"/>')
        out.append(f'<rect x="{lx}" y="{y+10}" width="{w}" height="5" rx="2.5" fill="{esc(color)}">'
                   f'<animate attributeName="width" values="0;{w}" dur="1.2s" begin="{0.15*i:.2f}s" fill="freeze"/></rect>')

    out.append(f'<rect width="{W}" height="{H}" rx="12" fill="url(#scan)"/>')
    out.append('</svg>')
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {OUT}: {cc['contributionCalendar']['totalContributions']} contributions, {commits} commits, "
          f"{stars} stars, streak {cur}/{longest}, langs {[n for n, _ in top]}")


if __name__ == "__main__":
    main()
