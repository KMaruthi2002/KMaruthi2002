#!/usr/bin/env python3
"""Generate the project cards and the footer SVG for the profile README.

Run from the repo root:  python3 tools/build_cards.py
Everything is plain SVG with SMIL animation, so it renders inside GitHub's <img>.
"""
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "cards"
OUT.mkdir(parents=True, exist_ok=True)

FONT = "'JetBrains Mono','Fira Code','SFMono-Regular',Menlo,Consolas,'Liberation Mono',monospace"
BG, PANEL, BORDER = "#070a0f", "#0b1118", "#1b2a38"
INK, DIM, MUTE = "#e6f7ff", "#9fb3c8", "#5b7a8c"

LANG_COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a",
    "Jupyter": "#DA5B0B", "Next.js": "#ffffff", "Markdown": "#083fa1",
}

PROJECTS = [
    dict(slug="rocket", idx="01", name="ROCKET", accent="#ff2d95", lang="Python",
         desc="An AI scientist whose only research domain is making PyTorch models faster on AMD MI300X. Profiles, hypothesises, applies, validates, measures. Solo, 24 hours.",
         tags="PyTorch · ROCm · multi-agent", chip="2.93× measured on Qwen2.5-7B"),
    dict(slug="eidos", idx="02", name="EIDOS", accent="#00f0ff", lang="Python",
         desc="Show it once. Compiles one video of a task into a program with a visual contract per step, then checks a live camera, a screen agent or a robot arm against it.",
         tags="Muse Spark · SAM 3.1 · Meta hackathon", chip="video → checkable program"),
    dict(slug="kepler", idx="03", name="KEPLER", accent="#f2a93b", lang="Python",
         desc="An AI scientist that discovers the laws of motion from video: tracks objects, proposes equations, fits the constants, and overlays its predictions on the footage.",
         tags="SAM 3.1 · scipy · Occam's razor", chip="video → equations"),
    dict(slug="rewind", idx="04", name="REWIND", accent="#39ff14", lang="Python",
         desc="Upload a photo of damage and watch the event get reverse-engineered: force, angle, speed and sequence, animated over the original photo in a streamed 5-stage pipeline.",
         tags="SAM 3.1 · Muse Wonder · physics sim", chip="forensic reconstruction"),
    dict(slug="quantriage", idx="05", name="QuanTriage", accent="#b388ff", lang="Python",
         desc="Quantum ML plus medical imaging across five cancers: diagnose, classify, localise in 3-D on brain MRI. Abstains and refers to a doctor when it is not sure.",
         tags="PennyLane · PyTorch · Streamlit", chip="pip install qml-oncology"),
    dict(slug="fintel", idx="06", name="fintel", accent="#00e5a0", lang="Python",
         desc="Financial telemetry and observability. OpenTelemetry discipline applied to markets: spans become anomalies, metrics become indicators, SLOs become governance.",
         tags="pandas · OpenTelemetry vocabulary", chip="pip install fintel"),
    dict(slug="pyexplain", idx="07", name="PyExplain", accent="#ffd166", lang="Python",
         desc="Paste Python, pick a style, get an animated, narrated explainer video. It runs the code in a sandbox so the narration uses the real values your variables take.",
         tags="Claude · ElevenLabs · ffmpeg", chip="code → video"),
    dict(slug="apex", idx="08", name="APEX // TELEMETRY", accent="#00f0ff", lang="Next.js",
         desc="A live, auto-updating Formula 1 command center with a sci-fi HUD: timing tower, race control feed, GPS track map, per-car onboard channel. No API keys needed.",
         tags="Next.js · OpenF1 · Jolpica", chip="live on Vercel"),
]

W, H = 560, 158
CH = 7.8   # approx px per character at 13px monospace


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(p: dict, delay: float) -> str:
    lines = textwrap.wrap(p["desc"], width=62)[:3]
    desc = "".join(
        f'<text x="26" y="{70 + i * 19}" font-size="13" fill="{DIM}">{esc(l)}</text>' for i, l in enumerate(lines)
    )
    chip_w = int(len(p["chip"]) * 7.3 + 22)
    chip_x = W - 18 - chip_w
    lang_color = LANG_COLORS.get(p["lang"], "#888")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">
  <title>{esc(p["name"])}</title>
  <defs>
    <clipPath id="r"><rect width="{W}" height="{H}" rx="10"/></clipPath>
    <clipPath id="m"><rect x="0" y="{H - 36}" width="{chip_x - 12}" height="36"/></clipPath>
    <linearGradient id="sweep" x1="0" x2="1"><stop offset="0" stop-color="{p["accent"]}" stop-opacity="0"/><stop offset="0.5" stop-color="{p["accent"]}" stop-opacity="0.9"/><stop offset="1" stop-color="{p["accent"]}" stop-opacity="0"/></linearGradient>
    <filter id="g" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <rect width="{W}" height="{H}" rx="10" fill="{PANEL}" stroke="{BORDER}"/>
  <g clip-path="url(#r)">
    <rect x="0" y="0" width="4" height="{H}" fill="{p["accent"]}"/>
    <rect x="0" y="0" width="160" height="1" fill="url(#sweep)" opacity="0.9">
      <animate attributeName="x" values="-160;{W}" dur="4.5s" begin="{delay}s" repeatCount="indefinite"/>
    </rect>
    <rect x="0" y="{H - 1}" width="160" height="1" fill="url(#sweep)" opacity="0.6">
      <animate attributeName="x" values="{W};-160" dur="4.5s" begin="{delay + 1.2}s" repeatCount="indefinite"/>
    </rect>
  </g>
  <path d="M{W - 30} 14H{W - 14}V30" fill="none" stroke="{p["accent"]}" stroke-width="1.5" opacity="0.8"/>
  <text x="26" y="30" font-size="10" letter-spacing="3" fill="{p["accent"]}">// {p["idx"]}</text>
  <text x="26" y="52" font-size="19" font-weight="700" fill="{INK}" filter="url(#g)">{esc(p["name"])}</text>
  {desc}
  <g clip-path="url(#m)">
    <circle cx="30" cy="{H - 20}" r="4" fill="{lang_color}"/>
    <text x="40" y="{H - 16}" font-size="11" fill="{DIM}">{esc(p["lang"])}</text>
    <text x="{40 + len(p["lang"]) * 6.8 + 14:.0f}" y="{H - 16}" font-size="11" fill="{MUTE}">{esc(p["tags"])}</text>
  </g>
  <rect x="{chip_x}" y="{H - 32}" width="{chip_w}" height="22" rx="11" fill="{BG}" stroke="{p["accent"]}" stroke-opacity="0.7"/>
  <text x="{chip_x + chip_w / 2:.0f}" y="{H - 17}" font-size="11" fill="{p["accent"]}" text-anchor="middle">{esc(p["chip"])}</text>
</svg>
'''


def footer() -> str:
    msg = "So much more is coming."
    w = int(len(msg) * 15.6)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="120" viewBox="0 0 1200 120" font-family="{FONT}">
  <title>So much more is coming.</title>
  <defs>
    <filter id="g" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <clipPath id="t"><rect x="{600 - w / 2:.0f}" y="40" height="40" width="0"><animate attributeName="width" values="0;0;{w};{w};0;0" keyTimes="0;0.05;0.35;0.88;0.9;1" dur="9s" repeatCount="indefinite"/></rect></clipPath>
    <pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity="0.22"/></pattern>
  </defs>
  <rect width="1200" height="120" fill="{BG}"/>
  <g fill="none" stroke="#00f0ff" stroke-width="2" opacity="0.85">
    <path d="M22 40V16H46"/><path d="M1154 16H1178V40"/><path d="M22 80V104H46"/><path d="M1178 80V104H1154"/>
  </g>
  <line x1="60" y1="60" x2="{600 - w / 2 - 30:.0f}" y2="60" stroke="#13202c"/>
  <line x1="{600 + w / 2 + 30:.0f}" y1="60" x2="1140" y2="60" stroke="#13202c"/>
  <g clip-path="url(#t)"><text x="600" y="69" font-size="26" fill="{INK}" text-anchor="middle" filter="url(#g)">{esc(msg)}</text></g>
  <rect x="{600 + w / 2 + 6:.0f}" y="46" width="12" height="28" fill="#00f0ff"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>
  <text x="600" y="98" font-size="10" letter-spacing="4" fill="{MUTE}" text-anchor="middle">// END OF TRANSMISSION</text>
  <rect width="1200" height="120" fill="url(#scan)"/>
</svg>
'''


if __name__ == "__main__":
    for i, p in enumerate(PROJECTS):
        (OUT / f'{p["slug"]}.svg').write_text(card(p, delay=round(i * 0.55, 2)), encoding="utf-8")
        print("wrote", OUT / f'{p["slug"]}.svg')
    (ROOT / "assets" / "footer.svg").write_text(footer(), encoding="utf-8")
    print("wrote", ROOT / "assets" / "footer.svg")
