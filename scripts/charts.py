"""Static charts in the dark house palette, from data/processed/contrib.json.

Every number drawn is read from contrib.json; the numbers behind each chart are
also written to posts/<slug>/images/numbers/*.csv for the tie-out.
"""
from __future__ import annotations

import csv
import json
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from common import CHARTS, PROCESSED, SHORT

BG, INK, MUTED, GRID = "#181A1B", "#BBBDC0", "#8C9094", "#2A2E31"
UP, DOWN = "#f37952", "#5598e7"            # coral = adds to inflation, blue = subtracts
DOWN_DIM = "#2f4f78"
HI_COLOR, RX_COLOR = "#3987e5", "#d55181"
NOW, WHATIF = "#8C9094", "#f37952"
SOURCE = ("Data 4 The People  ·  Source: BLS Consumer Price Index (CPI-U, not seasonally adjusted) "
          "and relative importance tables; contributions computed by Data 4 The People")
NUM = CHARTS / "numbers"
HIGHLIGHT = {"Health insurance", "Prescription drugs"}


plt.rcParams.update({"text.parse_math": False, "font.family": ["Arial", "DejaVu Sans"],
                     "axes.facecolor": BG, "figure.facecolor": BG, "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.edgecolor": GRID})


def short(name):
    return SHORT.get(name, name)


def pts(v):
    """Percentage points: two decimals, three when the value rounds below 0.01."""
    return f"{v:+.2f}" if abs(v) >= 0.01 else f"{v:+.3f}"


def month_label(ym):
    y, m = map(int, ym.split("-"))
    return date(y, m, 1).strftime("%B %Y")


def fig(title, sub, h=7.5, legend=None):
    f = plt.figure(figsize=(12, h), dpi=150)
    px = 1 / (h * 150)
    f.text(0.04, 1 - 22 * px, title, fontsize=20, fontweight="bold", va="top")
    y = 1 - 75 * px
    for line in sub.split("\n"):
        f.text(0.04, y, line, fontsize=12.5, color=MUTED, va="top")
        y -= 30 * px
    if legend:
        y -= 8 * px
        x = 0.04
        r = f.canvas.get_renderer()
        for word, color in legend:
            t = f.text(x, y, word, fontsize=12, fontweight="bold", color=color, va="top")
            x += t.get_window_extent(renderer=r).width / f.bbox.width + 0.025
        y -= 30 * px
    return f, y - 22 * px


def finish(f, ax, name, rows, header):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    f.text(0.04, 0.02, SOURCE, fontsize=8.5, color=MUTED)
    CHARTS.mkdir(parents=True, exist_ok=True)
    f.savefig(CHARTS / name, facecolor=BG)
    plt.close(f)
    NUM.mkdir(parents=True, exist_ok=True)
    with open(NUM / name.replace(".png", ".csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    print("wrote", name)


def bars(d, positive, name, n=15):
    items = d["items"]
    sel = items[:n] if positive else sorted(items, key=lambda i: i["contrib"])[:n]
    sel = list(reversed(sel)) if positive else list(reversed(sel))
    mon = month_label(d["month"])
    if positive:
        title = f"The {n} items that added the most to inflation, {mon}"
        sub = ("Each bar is the item's share of the 12-month rise in headline CPI, in percentage points.\n"
               f"All items together: {d['published']['headline']:.1f}%.")
        legend = None
    else:
        title = f"The {n} items that pulled inflation down the most, {mon}"
        sub = ("Each bar is how much the item lowered the 12-month change in headline CPI, in percentage points.")
        legend = [("Health insurance", HI_COLOR), ("Prescription drugs", RX_COLOR), ("Other items", DOWN_DIM)]
    f, top = fig(title, sub, h=8.2, legend=legend)
    ax = f.add_axes([0.32, 0.08, 0.58, top - 0.10] if positive else [0.40, 0.08, 0.52, top - 0.10])
    ys = range(len(sel))
    vals = [i["contrib"] for i in sel]
    colors = []
    for i in sel:
        if positive:
            colors.append(UP)
        else:
            colors.append({"Health insurance": HI_COLOR, "Prescription drugs": RX_COLOR}.get(i["name"], DOWN_DIM))
    ax.barh(list(ys), vals, height=0.62, color=colors)
    lim = max(abs(v) for v in vals) * 1.22
    ax.set_xlim((0, lim) if positive else (-lim, 0))
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    for y, i, v in zip(ys, sel, vals):
        label = f"{short(i['name'])}  ({i['yoy']:+.1f}%)"
        bold = i["name"] in HIGHLIGHT
        if positive:
            ax.text(-lim * 0.015, y, label, ha="right", va="center", fontsize=11.5, color=INK,
                    fontweight="bold" if bold else "normal")
            ax.text(v + lim * 0.015, y, pts(v), ha="left", va="center", fontsize=11, color=INK)
        else:
            ax.text(-lim * 1.0, y, label, ha="right", va="center", fontsize=11.5, color=INK,
                    fontweight="bold" if bold else "normal")
            ax.text(v - lim * 0.015, y, pts(v), ha="right", va="center", fontsize=11, color=INK)
    f.text(0.04, top + 0.005, "Item (12-month price change)", fontsize=10, color=MUTED, va="bottom")
    finish(f, ax, name, [(i["name"], i["yoy"], i["contrib"]) for i in reversed(sel)],
           ["item", "yoy_pct", "contrib_pts"])


def history(d, name):
    h = d["history"]
    w = d["whatif"]
    f, top = fig("Health insurance and prescription drug prices, 12-month change",
                 f"January 2015 to {month_label(d['month'])}. Dashed lines are each item's 10-year average\n"
                 "(the September-to-September changes from 2015-16 through 2024-25). The gap is October 2025,\n"
                 "which BLS did not publish.",
                 h=7.5, legend=[("Health insurance", HI_COLOR), ("Prescription drugs", RX_COLOR)])
    ax = f.add_axes([0.07, 0.10, 0.76, top - 0.12])
    rows = []
    for code, color in (("SEME", HI_COLOR), ("SEMF01", RX_COLOR)):
        ms = sorted(m for m in h[code] if m >= "2015-01")
        xs, ys = [], []
        for k, m in enumerate(ms):
            x = int(m[:4]) + (int(m[5:]) - 1) / 12
            if k and x - xs[-1] > 1.5 / 12:      # a missing month (October 2025): break the line
                xs.append(float("nan")); ys.append(float("nan"))
            xs.append(x); ys.append(h[code][m])
        ax.plot(xs, ys, color=color, lw=2)
        ax.axhline(w[code]["avg10"], color=color, lw=1.2, ls=(0, (4, 3)))
        ax.text(xs[-1] + 0.15, ys[-1], f"{ys[-1]:+.1f}%", color=INK, fontsize=11, va="center")
        off = 1.0 if code == "SEME" else -1.0
        ax.text(xs[-1] + 0.15, w[code]["avg10"] + off,
                f"average {w[code]['avg10']:+.1f}%", color=INK, fontsize=10.5, va="center")
        rows += [(code, m, h[code][m]) for m in ms]
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_xlim(2015, int(d["month"][:4]) + 0.75)
    lo = min(min(v for m, v in h[c].items() if m >= "2015-01") for c in ("SEME", "SEMF01"))
    hi = max(max(v for m, v in h[c].items() if m >= "2015-01") for c in ("SEME", "SEMF01"))
    ax.set_ylim(lo - 4, hi + 4)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_yticks([t for t in range(-40, 41, 10) if lo - 4 <= t <= hi + 4])
    ax.set_yticklabels([f"{t:+.0f}%" if t else "0%" for t in ax.get_yticks()])
    ax.set_xticks(range(2015, int(d["month"][:4]) + 1))
    ax.set_xticklabels([str(y) for y in range(2015, int(d["month"][:4]) + 1)])
    finish(f, ax, name, rows, ["series", "month", "yoy_pct"])


def whatif(d, name):
    pub, wt = d["published"], d["whatif_total"]
    f, top = fig("Inflation with health insurance and prescription drugs at their usual pace",
                 f"12-month change, {month_label(d['month'])}. The what-if swaps each item's actual change for its\n"
                 "10-year average and leaves everything else as published.",
                 h=6.0, legend=[("As published", NOW), ("With 10-year averages", WHATIF)])
    ax = f.add_axes([0.20, 0.10, 0.72, top - 0.12])
    labels = [("Headline", pub["headline"], wt["headline"]), ("Core\n(less food\nand energy)", pub["core"], wt["core"])]
    rows = []
    for k, (lab, a, b) in enumerate(labels):
        y = 1 - k
        ax.barh(y + 0.18, a, height=0.32, color=NOW)
        ax.barh(y - 0.18, b, height=0.32, color=WHATIF)
        ax.text(a + 0.05, y + 0.18, f"{a:.2f}%", va="center", fontsize=12, color=INK)
        ax.text(b + 0.05, y - 0.18, f"{b:.2f}%", va="center", fontsize=12, color=INK)
        ax.text(-0.08, y, lab, ha="right", va="center", fontsize=12.5, color=INK, fontweight="bold")
        rows.append((lab.replace("\n", " "), a, b, b - a))
    ax.set_xlim(0, max(wt["headline"], wt["core"]) * 1.15)
    ax.set_ylim(-0.6, 1.6)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.axvline(0, color=MUTED, lw=0.8)
    finish(f, ax, name, rows, ["measure", "published_pct", "whatif_pct", "difference_pts"])


def tieout(name):
    """Every month: the published 12-month change and what our items add up to."""
    rows = [r for r in csv.DictReader(open(PROCESSED / "monthly_summary.csv")) if r["status"] == "pass"]
    gh = max(abs(float(r["gap_headline"])) for r in rows)
    gc = max(abs(float(r["gap_core"])) for r in rows)
    first, last = month_label(rows[0]["month"]), month_label(rows[-1]["month"])
    f, top = fig("Our items add up to the published inflation rate, every month",
                 f"12-month change, {first} to {last}. The line is the rate BLS publishes. Each dot is the sum\n"
                 f"of our item contributions. The largest gap in any month is {gh:.4f} points for headline and\n"
                 f"{gc:.4f} points for core. The break is October 2025, which BLS did not publish.",
                 h=8.0, legend=[("Published by BLS", INK), ("Sum of our items", UP)])
    out = []
    panels = (("Headline", "published_headline", "items_headline"), ("Core (less food and energy)", "published_core", "items_core"))
    hgt = (top - 0.12) / 2 - 0.03
    for k, (lab, pk, ik) in enumerate(panels):
        ax = f.add_axes([0.07, 0.08 + (1 - k) * (hgt + 0.06), 0.88, hgt])
        xs, ys, ds = [], [], []
        for r in rows:
            x = int(r["month"][:4]) + (int(r["month"][5:]) - 1) / 12
            if xs and x - xs[-1] > 1.5 / 12:
                xs.append(float("nan")); ys.append(float("nan")); ds.append(float("nan"))
            xs.append(x); ys.append(float(r[pk])); ds.append(float(r[ik]))
        ax.plot(xs, ys, color=INK, lw=1.6, zorder=2)
        ax.scatter(xs, ds, s=9, color=UP, zorder=3, linewidths=0)
        ax.set_ylim(-0.5, 10)
        ax.set_yticks([0, 2, 4, 6, 8, 10])
        ax.set_yticklabels([f"{v}%" for v in (0, 2, 4, 6, 8, 10)])
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.set_xlim(2016.6, 2026.9)
        ax.set_xticks(range(2017, 2027))
        ax.set_xticklabels([str(y) for y in range(2017, 2027)] if k == 1 else [])
        ax.text(2016.75, 9.3, lab, fontsize=12.5, fontweight="bold", color=INK, va="top")
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.tick_params(length=0)
    for r in rows:
        out.append((r["month"], r["published_headline"], r["items_headline"], r["published_core"], r["items_core"]))
    finish(f, ax, name, out, ["month", "published_headline", "items_headline", "published_core", "items_core"])


WATERFALL_UP, WATERFALL_DOWN = 6, 4


def waterfall(d, name):
    """Biggest items up, everything else netted, biggest items down, to the total."""
    items = sorted(d["items"], key=lambda i: -i["contrib"])
    up, down = items[:WATERFALL_UP], sorted(items, key=lambda i: i["contrib"])[:WATERFALL_DOWN]
    rest = [i for i in items if i not in up and i not in down]
    total = sum(i["contrib"] for i in items)
    steps = ([(short(i["name"]), i["contrib"], UP) for i in up]
             + [(f"The other {len(rest)} items, net", sum(i["contrib"] for i in rest), MUTED)]
             + [(short(i["name"]), i["contrib"], DOWN) for i in down])
    mon = month_label(d["month"])
    f, top = fig(f"What added up to {d['published']['headline']:.1f}% inflation, {mon}",
                 "Each bar is one item's share of the 12-month rise in headline CPI, in percentage points.\n"
                 "Bars build from left to right; the bottom bar is the total.",
                 h=8.0, legend=[("Pushed up", UP), ("Pulled down", DOWN), ("Everything else", MUTED)])
    ax = f.add_axes([0.30, 0.08, 0.64, top - 0.10])
    run, rows = 0.0, []
    n = len(steps)
    for k, (lab, v, color) in enumerate(steps):
        y = n - k
        left = run if v >= 0 else run + v
        ax.barh(y, abs(v), left=left, height=0.62, color=color)
        if k < n - 1:
            ax.plot([run + v, run + v], [y - 0.31, y - 1 + 0.31], color=MUTED, lw=0.7, ls=(0, (2, 2)))
        ax.text(-0.06, y, lab, ha="right", va="center", fontsize=11.5, color=INK)
        tx = (left + abs(v) + 0.04) if v >= 0 else (left - 0.04)
        ax.text(tx, y, pts(v), ha="left" if v >= 0 else "right", va="center", fontsize=11, color=INK)
        run += v
        rows.append((lab, round(v, 6), round(run, 6)))
    ax.barh(0, total, height=0.62, color=INK)
    ax.text(-0.06, 0, "All items", ha="right", va="center", fontsize=11.5, color=INK, fontweight="bold")
    ax.text(total + 0.04, 0, f"{total:+.2f}", ha="left", va="center", fontsize=11, color=INK, fontweight="bold")
    rows.append(("All items", round(total, 6), round(total, 6)))
    peak = max(r[2] for r in rows)
    ax.set_xlim(0, peak * 1.12)
    ax.set_ylim(-0.6, n + 0.6)
    ax.set_yticks([]); ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.axvline(0, color=MUTED, lw=0.8)
    finish(f, ax, name, rows, ["step", "contrib_pts", "running_total_pts"])


def fastest(d, name, n=15):
    """Items whose own published index rose the most over 12 months."""
    sel = sorted((i for i in d["items"] if i["own_index"] and i["yoy"] is not None),
                 key=lambda i: -i["yoy"])[:n]
    ENERGY = "#f2b84b"
    mon = month_label(d["month"])
    f, top = fig(f"The {n} items whose prices rose the most, {mon}",
                 "12-month price change. Only items with their own published BLS index. In parentheses, each item's\n"
                 "share of consumer spending in the CPI; small items can move a lot without moving the total.",
                 h=8.2, legend=[("Energy", ENERGY), ("Other items", UP)])
    ax = f.add_axes([0.40, 0.08, 0.52, top - 0.10])
    sel_r = list(reversed(sel))
    ys = range(len(sel_r))
    vals = [i["yoy"] for i in sel_r]
    ax.barh(list(ys), vals, height=0.62, color=[ENERGY if i["group"] == "Energy" else UP for i in sel_r])
    lim = max(vals) * 1.15
    ax.set_xlim(0, lim)
    for y, i, v in zip(ys, sel_r, vals):
        share = f"{i['ri_sep_prior']:.2f}%" if i["ri_sep_prior"] >= 0.005 else "under 0.01%"
        ax.text(-lim * 0.015, y, f"{short(i['name'])}  ({share})", ha="right", va="center",
                fontsize=11.5, color=INK)
        ax.text(v + lim * 0.015, y, f"{v:+.1f}%", ha="left", va="center", fontsize=11, color=INK)
    ax.set_yticks([]); ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.axvline(0, color=MUTED, lw=0.8)
    finish(f, ax, name, [(i["name"], i["yoy"], i["ri_sep_prior"], i["group"]) for i in sel],
           ["item", "yoy_pct", "weight_pct", "group"])


def main():
    d = json.loads((PROCESSED / "contrib.json").read_text())
    tieout("01-tieout.png")
    waterfall(d, "02-waterfall.png")
    fastest(d, "03-fastest-rising.png")
    bars(d, True, "04-top-adders.png")
    bars(d, False, "05-top-subtractors.png")
    history(d, "06-health-insurance-rx-history.png")
    whatif(d, "07-whatif.png")


if __name__ == "__main__":
    main()
