#!/usr/bin/env python3
"""Build the animated chart panel for the README.

Four small charts that draw themselves, one per project, each on the real
series from that project's result files rather than a shape invented to look
busy. Numbers count up alongside the drawing so the finished figure is on
screen, not just implied by a line.

An animated GIF rather than SVG: README images are proxied through GitHub's
camo, which sanitises SVG and has broken animation there before. GIF always
plays.

Every frame is rendered in ONE Chrome pass — the frames are stacked into a tall
filmstrip page, screenshotted together, then sliced. Launching Chrome 24 times
instead takes about forty times as long.

Usage:
    python3 tools/render_charts.py
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
HOME = ROOT.parent
OUT = ROOT / "assets"
BUILD = ROOT / ".render"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

W, H = 1200, 560
ANIM_FRAMES = 18            # frames spent drawing
HOLD_FRAMES = 6             # frames holding the finished chart
FRAMES = ANIM_FRAMES + HOLD_FRAMES
STEP_MS = 70
HOLD_MS = 2600              # the finished state is what people actually read

THEMES = {
    "dark": {
        "bg": "#0b0f14", "panel": "#111821", "line": "#1e2a36", "soft": "#17202a",
        "text": "#e6edf3", "dim": "#9fb0c0", "mute": "#6b7f92",
        # one hue per project, all legible on the dark ground
        "c1": "#f0913f", "c2": "#2dd4a7", "c3": "#5aa9f0", "c4": "#c084fc",
        "ramp": ["#64748b", "#7c8ea3", "#38bdf8", "#22d3ee", "#f0913f", "#2dd4a7"],
    },
    "light": {
        "bg": "#fbfaf7", "panel": "#ffffff", "line": "#ddd9cf", "soft": "#eceae3",
        "text": "#16202a", "dim": "#4a5b6b", "mute": "#7d8b98",
        "c1": "#b8601a", "c2": "#0f7a5f", "c3": "#1667a8", "c4": "#6d43c9",
        "ramp": ["#94a3b8", "#7b8b9c", "#1667a8", "#0e7490", "#b8601a", "#0f7a5f"],
    },
}


# --------------------------------------------------------------------------
# real series, read from the project repositories
# --------------------------------------------------------------------------

def rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load() -> dict:
    r = rows(HOME / "retail-analytics-sql/reports/tables/06_margin_erosion.csv")
    credit = [x for x in r if x["segment"] == "contractor"]
    retail = {
        "months": [x["sale_month"] for x in credit],
        "discount": [float(x["avg_discount_pct"]) for x in credit],
        "margin": [float(x["margin_pct"]) for x in credit],
    }

    data = json.loads((HOME / "vn-product-matcher/reports/results.json").read_text())
    res = data["datasets"]["test_unseen"]["results"]
    labels = {"exact": "exact", "bm25_fts5": "BM25", "rapidfuzz": "fuzzy",
              "tfidf_char": "TF-IDF", "dense_base": "encoder", "dense_finetuned": "tuned"}
    matcher = sorted(
        [(labels[x["retriever"]], x["recall"]["1"] * 100)
         for x in res if x["retriever"] in labels],
        key=lambda p: p[1],
    )

    lift = rows(HOME / "ev-purchase-analysis/reports/tables/lift_by_decile.csv")
    ev = {"x": [0.0] + [float(x["top_pct"]) for x in lift],
          "y": [0.0] + [float(x["capture_pct"]) for x in lift]}

    cap = sorted(rows(HOME / "caption-decoding-study/reports/tables/decoding_results.csv"),
                 key=lambda x: float(x["beam_width"]))
    caption = {"labels": [x["strategy"] for x in cap],
               "bleu": [float(x["bleu_4"]) for x in cap]}

    return {"retail": retail, "matcher": matcher, "ev": ev, "caption": caption}


# --------------------------------------------------------------------------
# svg helpers
# --------------------------------------------------------------------------

def ease(t: float) -> float:
    return 1 - (1 - t) ** 3


def polyline(pts, color, width=2.2):
    if len(pts) < 2:
        return ""
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def partial(xs, ys, t, px, py):
    """The first t-fraction of a series, with the head interpolated."""
    n = len(xs)
    if n < 2:
        return []
    pos = t * (n - 1)
    k = int(pos)
    pts = [(px(xs[i]), py(ys[i])) for i in range(min(k + 1, n))]
    if k + 1 < n:
        f = pos - k
        x = xs[k] + (xs[k + 1] - xs[k]) * f
        y = ys[k] + (ys[k + 1] - ys[k]) * f
        pts.append((px(x), py(y)))
    return pts


# --------------------------------------------------------------------------
# the four panels
# --------------------------------------------------------------------------

PW, PH = 562, 242          # panel box
CW, CH = 530, 118          # chart area inside it


def panel(title, colour, value, note, chart_svg, th):
    return (
        f'<div class="panel">'
        f'<div class="ptitle" style="color:{colour}">{title}</div>'
        f'<div class="pval">{value}<em>{note}</em></div>'
        f'<svg class="chart" viewBox="0 0 {CW} {CH}">{chart_svg}</svg>'
        f'</div>'
    )


def p_retail(d, t, th):
    """The headline uses the repo's own definition of the drift: the mean of the
    first quarter of the series against the mean of the last. Quoting the final
    month instead would print 8.0% and contradict every other place the finding
    appears."""
    m, dis = d["margin"], d["discount"]
    n = len(m)
    q = max(n // 4, 1)
    d_start, d_end = sum(dis[:q]) / q, sum(dis[-q:]) / q
    m_start, m_end = sum(m[:q]) / q, sum(m[-q:]) / q

    x0, x1, y0, y1 = 34, CW - 58, 10, CH - 18
    # separate scales: 3-8% against 18-21% on one axis would flatten both
    def px(i): return x0 + (i / (n - 1)) * (x1 - x0)
    def py_m(v): return y1 - ((v - 17.5) / (21.5 - 17.5)) * (y1 - y0) * 0.44 - (y1 - y0) * 0.56
    def py_d(v): return y1 - ((v - 2.0) / (9.0 - 2.0)) * (y1 - y0) * 0.44

    idx = list(range(n))
    g = "".join(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" '
                f'stroke="{th["soft"]}" stroke-width="1"/>'
                for yy in (py_m(20), py_m(19), py_d(7), py_d(4)))
    a = polyline(partial(idx, m, t, px, py_m), th["c2"])
    b = polyline(partial(idx, dis, t, px, py_d), th["c1"])
    k = min(int(t * (n - 1)), n - 1)
    heads = (f'<circle cx="{px(k):.1f}" cy="{py_m(m[k]):.1f}" r="3.4" fill="{th["c2"]}"/>'
             f'<circle cx="{px(k):.1f}" cy="{py_d(dis[k]):.1f}" r="3.4" fill="{th["c1"]}"/>')
    lab = (f'<text x="0" y="{py_m(20):.1f}" font-size="9" fill="{th["mute"]}" '
           f'font-family="ui-monospace,monospace">20%</text>'
           f'<text x="0" y="{py_d(4):.1f}" font-size="9" fill="{th["mute"]}" '
           f'font-family="ui-monospace,monospace">4%</text>'
           f'<text x="{x0}" y="{CH - 4}" font-size="9" fill="{th["mute"]}" '
           f'font-family="ui-monospace,monospace">2024-08</text>'
           f'<text x="{x1}" y="{CH - 4}" font-size="9" fill="{th["mute"]}" '
           f'text-anchor="end" font-family="ui-monospace,monospace">2026-08</text>'
           f'<text x="{x1 + 6:.1f}" y="{py_m(m[-1]) + 3:.1f}" font-size="10" '
           f'fill="{th["c2"]}" font-weight="600" '
           f'font-family="ui-monospace,monospace">margin</text>'
           f'<text x="{x1 + 6:.1f}" y="{py_d(dis[-1]) + 3:.1f}" font-size="10" '
           f'fill="{th["c1"]}" font-weight="600" '
           f'font-family="ui-monospace,monospace">discount</text>')
    shown = d_start + (d_end - d_start) * t
    mm = m_start + (m_end - m_start) * t
    return panel("retail-analytics-sql", th["c1"], f"{shown:.1f}%",
                 f"discount to credit accounts, from {d_start:.1f}% "
                 f"&middot; margin {m_start:.1f}% &rarr; {mm:.1f}%",
                 g + a + b + heads + lab, th)


def p_matcher(d, t, th):
    x0, x1 = 62, CW - 46
    rh = CH / len(d)
    out = []
    for i, (name, v) in enumerate(d):
        y = i * rh + 2
        shown = v * ease(min(1.0, t * 1.15))
        w = (shown / 100) * (x1 - x0)
        col = th["ramp"][i]
        out.append(f'<rect x="{x0}" y="{y:.1f}" width="{w:.1f}" height="{rh - 5:.1f}" '
                   f'rx="2.5" fill="{col}"/>')
        out.append(f'<text x="{x0 - 6}" y="{y + rh / 2 + 1:.1f}" font-size="9.5" '
                   f'fill="{th["dim"]}" text-anchor="end" '
                   f'font-family="ui-monospace,monospace">{name}</text>')
        out.append(f'<text x="{x0 + w + 6:.1f}" y="{y + rh / 2 + 1:.1f}" font-size="9.5" '
                   f'fill="{th["text"]}" font-family="ui-monospace,monospace">'
                   f'{shown:.1f}%</text>')
    top = d[-1][1] * ease(min(1.0, t * 1.15))
    return panel("vn-product-matcher", th["c2"], f"{top:.1f}%",
                 "Recall@1, SKUs held out of training", "".join(out), th)


def p_ev(d, t, th):
    xs, ys = d["x"], d["y"]
    x0, x1, y0, y1 = 30, CW - 10, 8, CH - 18

    def px(v): return x0 + v / 100 * (x1 - x0)
    def py(v): return y1 - v / 100 * (y1 - y0)

    g = "".join(f'<line x1="{x0}" y1="{py(v):.1f}" x2="{x1}" y2="{py(v):.1f}" '
                f'stroke="{th["soft"]}" stroke-width="1"/>' for v in (25, 50, 75, 100))
    ref = (f'<line x1="{px(0)}" y1="{py(0)}" x2="{px(100)}" y2="{py(100)}" '
           f'stroke="{th["mute"]}" stroke-width="1" stroke-dasharray="3 4" opacity=".7"/>')
    pts = partial(xs, ys, t, px, py)
    fill = ""
    if len(pts) > 1:
        d2 = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        fill = (f'<path d="{d2} L{pts[-1][0]:.1f} {y1} L{px(0)} {y1} Z" '
                f'fill="{th["c3"]}" opacity="0.16"/>')
    ln = polyline(pts, th["c3"], 2.4)
    head = (f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="3.6" '
            f'fill="{th["c3"]}"/>') if pts else ""
    marker = ""
    if t > 0.30:
        marker = (f'<line x1="{px(30):.1f}" y1="{y1}" x2="{px(30):.1f}" y2="{py(92.2):.1f}" '
                  f'stroke="{th["c1"]}" stroke-width="1.3" stroke-dasharray="3 3"/>'
                  f'<circle cx="{px(30):.1f}" cy="{py(92.2):.1f}" r="3.6" fill="{th["c1"]}"/>'
                  f'<text x="{px(30) + 8:.1f}" y="{py(92.2) + 3:.1f}" font-size="10" '
                  f'fill="{th["c1"]}" font-weight="600" '
                  f'font-family="ui-monospace,monospace">top 30% &rarr; 92%</text>')
    lab = (f'<text x="0" y="{py(100):.1f}" font-size="9" fill="{th["mute"]}" '
           f'font-family="ui-monospace,monospace">100</text>'
           f'<text x="0" y="{py(50):.1f}" font-size="9" fill="{th["mute"]}" '
           f'font-family="ui-monospace,monospace">50</text>'
           f'<text x="{x1}" y="{CH - 4}" font-size="9" fill="{th["mute"]}" '
           f'text-anchor="end" font-family="ui-monospace,monospace">% of list contacted</text>')
    target = ys[3]                       # capture at the top 30% of the list
    cur = target * min(1.0, t / 0.55)
    return panel("ev-purchase-analysis", th["c3"], f"{cur:.0f}%",
                 "of buyers reached from the top 30% &middot; 668,665 records",
                 g + ref + fill + ln + head + marker + lab, th)


def p_caption(d, t, th):
    ys = d["bleu"]
    n = len(ys)
    x0, x1, y0, y1 = 40, CW - 26, 12, CH - 20
    lo, hi = 0.236, 0.286

    def px(i): return x0 + (i / (n - 1)) * (x1 - x0)
    def py(v): return y1 - ((v - lo) / (hi - lo)) * (y1 - y0)

    g = "".join(f'<line x1="{x0}" y1="{py(v):.1f}" x2="{x1}" y2="{py(v):.1f}" '
                f'stroke="{th["soft"]}" stroke-width="1"/>' for v in (0.25, 0.26, 0.27, 0.28))
    pts = partial(list(range(n)), ys, t, px, py)
    ln = polyline(pts, th["c4"], 2.4)
    dots, lab = [], []
    shown = int(t * (n - 1)) + 1
    for i in range(min(shown, n)):
        peak = i == 2
        dots.append(f'<circle cx="{px(i):.1f}" cy="{py(ys[i]):.1f}" '
                    f'r="{5 if peak else 3.4}" fill="{th["c4"]}"/>')
        lab.append(f'<text x="{px(i):.1f}" y="{py(ys[i]) - 9:.1f}" font-size="9.5" '
                   f'fill="{th["text"] if peak else th["dim"]}" text-anchor="middle" '
                   f'font-weight="{600 if peak else 400}" '
                   f'font-family="ui-monospace,monospace">{ys[i]:.4f}</text>')
        lab.append(f'<text x="{px(i):.1f}" y="{CH - 5}" font-size="9" '
                   f'fill="{th["mute"]}" text-anchor="middle" '
                   f'font-family="ui-monospace,monospace">{d["labels"][i]}</text>')
    warn = ""
    if t > 0.92:
        warn = (f'<text x="{px(3):.1f}" y="{py(ys[3]) + 18:.1f}" font-size="9.5" '
                f'fill="{th["c1"]}" text-anchor="end" font-weight="600" '
                f'font-family="ui-monospace,monospace">&minus;0.0064, p = 0.017</text>')
    return panel("caption-decoding-study", th["c4"], "beam 5",
                 "BLEU-4 peak, then it falls again",
                 g + ln + "".join(dots) + "".join(lab) + warn, th)


# --------------------------------------------------------------------------

CSS = """
* { box-sizing: border-box; margin: 0; }
body { background: BG; }
.frame {
  width: WPX; height: HPX; position: relative; overflow: hidden;
  background: BG; color: TEXT;
  font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
  padding: 26px 28px;
}
.grid {
  position: absolute; inset: 0;
  background-image: linear-gradient(SOFT 1px, transparent 1px),
                    linear-gradient(90deg, SOFT 1px, transparent 1px);
  background-size: 48px 48px;
  -webkit-mask-image: radial-gradient(70% 80% at 20% 30%, #000, transparent 78%);
}
.wrap { position: relative; display: grid; grid-template-columns: 1fr 1fr;
        grid-template-rows: 1fr 1fr; gap: 18px; height: 100%; }
.panel {
  background: PANEL; border: 1px solid LINE; border-radius: 11px;
  padding: 13px 16px 8px; display: flex; flex-direction: column;
}
.ptitle { font-family: ui-monospace, Menlo, monospace; font-size: 13px;
          font-weight: 600; letter-spacing: -.01em; }
.pval { font-family: ui-monospace, Menlo, monospace; font-size: 23px;
        font-weight: 700; color: TEXT; letter-spacing: -.03em; margin-top: 2px; }
.pval em { font-style: normal; font-family: -apple-system, Arial, sans-serif;
           font-size: 11.5px; font-weight: 400; color: MUTE; margin-left: 9px; }
.chart { width: 100%; flex: 1; margin-top: 6px; overflow: visible; }
"""


def build_frames(data, th) -> str:
    css = (CSS.replace("BG", th["bg"]).replace("PANEL", th["panel"])
              .replace("LINE", th["line"]).replace("SOFT", th["soft"])
              .replace("TEXT", th["text"]).replace("MUTE", th["mute"])
              .replace("WPX", f"{W}px").replace("HPX", f"{H}px"))
    out = [f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style>"
           "</head><body>"]
    for i in range(FRAMES):
        # start part-drawn: frame 0 is what any viewer that does not animate
        # GIFs will see, and an empty chart is a poor thing to show them
        t = ease(0.15 + 0.85 * min(1.0, i / (ANIM_FRAMES - 1)))
        out.append('<div class="frame"><div class="grid"></div><div class="wrap">')
        out.append(p_retail(data["retail"], t, th))
        out.append(p_matcher(data["matcher"], t, th))
        out.append(p_ev(data["ev"], t, th))
        out.append(p_caption(data["caption"], t, th))
        out.append("</div></div>")
    out.append("</body></html>")
    return "".join(out)


def render(name: str, html: str) -> Path:
    BUILD.mkdir(exist_ok=True)
    src = BUILD / f"{name}.html"
    src.write_text(html, encoding="utf-8")
    strip = BUILD / f"{name}.png"
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
         f"--window-size={W},{H * FRAMES}", f"--screenshot={strip}",
         "--virtual-time-budget=8000", src.as_uri()],
        capture_output=True, check=True,
    )
    if not strip.exists():
        sys.exit(f"chrome produced no filmstrip for {name}")
    return strip


def to_gif(strip: Path, out: Path) -> None:
    sheet = Image.open(strip).convert("RGB")
    if sheet.height < H * FRAMES:
        sys.exit(f"filmstrip short: {sheet.height} < {H * FRAMES}")

    frames = [sheet.crop((0, i * H, W, (i + 1) * H)) for i in range(FRAMES)]
    # one palette for every frame, taken from the finished chart, so the
    # colours do not shift while it plays
    base = frames[-1].quantize(colors=200, method=Image.MEDIANCUT)
    quant = [f.quantize(palette=base, dither=Image.Dither.NONE) for f in frames]
    durations = [STEP_MS] * ANIM_FRAMES + [STEP_MS] * (HOLD_FRAMES - 1) + [HOLD_MS]

    quant[0].save(out, save_all=True, append_images=quant[1:],
                  duration=durations, loop=0, optimize=True, disposal=2)


def main() -> int:
    if not Path(CHROME).exists():
        sys.exit(f"Chrome not found at {CHROME}")
    OUT.mkdir(exist_ok=True)
    data = load()

    for theme_name, th in THEMES.items():
        strip = render(f"charts-{theme_name}", build_frames(data, th))
        gif = OUT / f"charts-{theme_name}.gif"
        to_gif(strip, gif)
        print(f"  {gif.relative_to(ROOT)}  {gif.stat().st_size / 1024:.0f} KB  "
              f"{FRAMES} frames")

    shutil.rmtree(BUILD, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
