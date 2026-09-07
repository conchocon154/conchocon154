#!/usr/bin/env python3
"""Render the README's images.

GitHub strips CSS from markdown, so anything that should look designed has to
arrive as a picture. These are built from the same tokens as the portfolio at
conchocon154.github.io, in a light and a dark variant, and the README picks
between them with <picture media="(prefers-color-scheme: …)">.

PNG rather than SVG on purpose: GitHub proxies README images through camo,
which sanitises SVG and has broken it before. A bitmap always renders.

Usage:
    python3 tools/render.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
BUILD = ROOT / ".render"

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

THEMES = {
    "dark": {
        "bg": "#0b0f14", "raise": "#111821", "line": "#1e2a36", "soft": "#17202a",
        "text": "#e6edf3", "dim": "#9fb0c0", "mute": "#6b7f92",
        "accent": "#4dd4ac", "warn": "#e8833a", "glow": "0.20",
    },
    "light": {
        "bg": "#fbfaf7", "raise": "#ffffff", "line": "#ddd9cf", "soft": "#e9e6de",
        "text": "#16202a", "dim": "#4a5b6b", "mute": "#7d8b98",
        "accent": "#10775f", "warn": "#b8531a", "glow": "0.13",
    },
}

BASE_CSS = """
* {{ box-sizing: border-box; margin: 0; }}
body {{
  width: {w}px; height: {h}px; overflow: hidden; position: relative;
  background: {bg}; color: {text};
  font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
}}
.grid {{
  position: absolute; inset: 0;
  background-image:
    linear-gradient({soft} 1px, transparent 1px),
    linear-gradient(90deg, {soft} 1px, transparent 1px);
  background-size: 48px 48px;
  -webkit-mask-image: radial-gradient(70% 80% at 22% 40%, #000, transparent 76%);
}}
.glow {{
  position: absolute; inset: -40% -10% auto -20%; height: 180%;
  background:
    radial-gradient(50% 44% at 18% 26%, rgba(77,212,172,{glow}), transparent 68%),
    radial-gradient(44% 40% at 88% 10%, rgba(127,209,255,0.10), transparent 72%);
}}
.mono {{ font-family: ui-monospace, "SF Mono", Menlo, monospace; }}
.in {{ position: relative; height: 100%; }}
"""

# --------------------------------------------------------------------------

BANNER = """<style>
{base}
.in {{ padding: 46px 54px; display: flex; flex-direction: column; }}
.eyebrow {{
  font-family: ui-monospace, Menlo, monospace; font-size: 13px;
  letter-spacing: .2em; text-transform: uppercase; color: {mute};
}}
h1 {{ font-size: 62px; font-weight: 700; letter-spacing: -.03em; margin-top: 14px; }}
.role {{
  font-family: "Iowan Old Style", Palatino, Georgia, serif; font-style: italic;
  font-size: 26px; color: {accent}; margin-top: 8px; letter-spacing: -.01em;
}}
.spacer {{ flex: 1; }}
.chips {{ display: flex; gap: 9px; }}
.chip {{
  font-family: ui-monospace, Menlo, monospace; font-size: 14px;
  color: {dim}; border: 1px solid {line}; border-radius: 7px;
  padding: 6px 12px; background: {raise};
}}
svg.sig {{ position: absolute; left: 0; bottom: 0; width: {w}px; height: 150px; }}
</style>
<div class="glow"></div><div class="grid"></div>
<svg class="sig" viewBox="0 0 1200 150" preserveAspectRatio="none">
  <defs>
    <linearGradient id="f" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{accent}" stop-opacity=".20"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="m" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#fff" stop-opacity="0"/>
      <stop offset="16%" stop-color="#fff" stop-opacity="1"/>
      <stop offset="84%" stop-color="#fff" stop-opacity="1"/>
      <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <mask id="mk"><rect width="1200" height="150" fill="url(#m)"/></mask>
  </defs>
  <g mask="url(#mk)">
    <path d="M0 104 C 70 104 90 64 150 64 S 230 124 300 124 S 372 46 440 46
             S 520 114 590 114 S 660 74 730 74 S 806 128 875 128 S 950 36 1020 36
             S 1120 96 1200 86 L1200 150 L0 150 Z" fill="url(#f)"/>
    <path d="M0 104 C 70 104 90 64 150 64 S 230 124 300 124 S 372 46 440 46
             S 520 114 590 114 S 660 74 730 74 S 806 128 875 128 S 950 36 1020 36
             S 1120 96 1200 86"
          fill="none" stroke="{accent}" stroke-width="2.4" stroke-linecap="round"/>
  </g>
</svg>
<div class="in">
  <div class="eyebrow">Ho Chi Minh City &middot; open to remote</div>
  <h1>L&ecirc; Minh &#272;&#259;ng</h1>
  <div class="role">Data &amp; Business Analyst &mdash; SQL, Python, and the tests that keep a number honest</div>
  <div class="spacer"></div>
  <div class="chips">
    <span class="chip">SQL</span><span class="chip">Python</span>
    <span class="chip">pandas</span><span class="chip">scikit-learn</span>
    <span class="chip">statsmodels</span><span class="chip">PyTorch</span>
    <span class="chip">FastAPI</span>
  </div>
</div>
"""

# --------------------------------------------------------------------------

PROJECTS = [
    ("retail-analytics-sql", "Discount drift nobody noticed, while revenue held steady",
     "3.1% &rarr; 6.8%", "margin leak found"),
    ("vn-product-matcher", "Recall@1 on SKUs held out of training, over a TF-IDF baseline",
     "96.9%", "+1.9 pt, p = 1.2e-3"),
    ("ev-purchase-analysis", "Buyers reached by contacting the top 30% of the scored list",
     "92%", "668,665 records"),
    ("caption-decoding-study", "Where BLEU-4 peaks before a wider beam makes it worse",
     "beam 5", "&minus;0.0064, p = 0.017"),
]

WORK = """<style>
{base}
.in {{ padding: 34px 44px; display: flex; flex-direction: column; }}
.head {{
  font-family: ui-monospace, Menlo, monospace; font-size: 13px;
  letter-spacing: .2em; text-transform: uppercase; color: {mute};
  margin-bottom: 22px;
}}
.row {{
  display: grid; grid-template-columns: 1fr 250px;
  gap: 20px; align-items: center;
  padding: 19px 0; border-top: 1px solid {soft};
}}
.row:first-of-type {{ border-top: 0; }}
.name {{
  font-family: ui-monospace, Menlo, monospace; font-size: 19px;
  font-weight: 600; color: {accent}; letter-spacing: -.01em;
}}
.what {{ font-size: 15px; color: {dim}; margin-top: 5px; }}
.metric {{ text-align: right; }}
.metric b {{
  display: block; font-family: ui-monospace, Menlo, monospace;
  font-size: 27px; font-weight: 700; color: {text}; letter-spacing: -.03em;
}}
.metric span {{ display: block; font-size: 13px; color: {mute}; margin-top: 3px; }}
</style>
<div class="glow"></div><div class="grid"></div>
<div class="in">
  <div class="head">Selected work &middot; every figure measured against a baseline</div>
  {rows}
</div>
"""

ROW = """<div class="row">
  <div>
    <div class="name">{name}</div>
    <div class="what">{what}</div>
  </div>
  <div class="metric"><b>{value}</b><span>{note}</span></div>
</div>"""


def page(body_css_html: str, w: int, h: int, theme: dict) -> str:
    base = BASE_CSS.format(w=w, h=h, **theme)
    return ("<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>"
            + body_css_html.format(base=base, w=w, **theme)
            + "</body></html>")


def shoot(html: str, out: Path, w: int, h: int) -> None:
    BUILD.mkdir(exist_ok=True)
    src = BUILD / (out.stem + ".html")
    src.write_text(html, encoding="utf-8")
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
         "--force-device-scale-factor=2", f"--window-size={w},{h}",
         f"--screenshot={out}", "--virtual-time-budget=4000", src.as_uri()],
        capture_output=True, check=True,
    )
    if not out.exists():
        sys.exit(f"chrome produced nothing for {out.name}")


def main() -> int:
    if not Path(CHROME).exists():
        sys.exit(f"Chrome not found at {CHROME}")
    OUT.mkdir(exist_ok=True)

    rows = "\n".join(
        ROW.format(name=n, what=w, value=v, note=note)
        for n, w, v, note in PROJECTS
    )
    work_html = WORK.replace("{rows}", rows)

    for name, tmpl, (w, h) in [("banner", BANNER, (1200, 340)),
                               ("work", work_html, (1200, 432))]:
        for theme_name, theme in THEMES.items():
            out = OUT / f"{name}-{theme_name}.png"
            shoot(page(tmpl, w, h, theme), out, w, h)
            print(f"  {out.relative_to(ROOT)}  {out.stat().st_size // 1024} KB")

    shutil.rmtree(BUILD, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
