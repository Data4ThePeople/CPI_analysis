"""Item contributions for every month from October 2016 to the release month.

Same method as the release month (scripts/chain.py). Writes:
- data/processed/monthly.json: every month's items, for the animated page;
- data/processed/monthly_summary.csv: one row per month with the published
  rates, what the items add up to, the gap, and how much weight was filled;
- data/processed/monthly_items.csv: one row per month and item, for checking.

Each month passes or fails the tie-out rules in CHECKS. A failing month stops
the build. October 2025 has no published index (federal funding lapse) and is
listed as missing, not computed.
"""
from __future__ import annotations

import csv
import json

from chain import Inputs, compute_month
from common import PROCESSED, TARGET

START = (2016, 10)                     # ten years of months, through the release month
MISSING = {"2025-10": "BLS did not publish October 2025 indexes (federal funding lapse)."}
CHECKS = {"max_gap_pts": 0.005,        # items vs published 12-month change, headline and core
          "max_filled_share": 10.0}    # percent of weight on items without their own index


def month_list():
    y, m = START
    out = []
    while (y, m) <= TARGET:
        out.append(f"{y}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def main():
    inp = Inputs()
    summary, item_rows, months = [], [], {}
    for t in month_list():
        if t in MISSING:
            summary.append({"month": t, "status": "missing", "note": MISSING[t]})
            continue
        r = compute_month(inp, t)
        items = r["items"]
        gh = r["sum"]["headline"] - r["published"]["headline"]
        gc = r["sum"]["core"] - r["published"]["core"]
        filled = sum(i["ri_sep_prior"] for i in items if not i["own_index"])
        ok = (abs(gh) <= CHECKS["max_gap_pts"] and abs(gc) <= CHECKS["max_gap_pts"]
              and filled <= CHECKS["max_filled_share"])
        summary.append({
            "month": t, "status": "pass" if ok else "FAIL",
            "published_headline": round(r["published"]["headline"], 4),
            "items_headline": round(r["sum"]["headline"], 4), "gap_headline": round(gh, 5),
            "published_core": round(r["published"]["core"], 4),
            "items_core": round(r["sum"]["core"], 4), "gap_core": round(gc, 5),
            "filled_items": sum(1 for i in items if not i["own_index"]),
            "filled_share": round(filled, 3),
            "weights_from": f"{r['dec_prior']} rolled to {r['base']}, then {r['dec_new']}",
            "note": "",
        })
        months[t] = {
            "base": r["base"],
            "published": r["published"], "sum": r["sum"],
            "items": [{k: i[k] for k in ("name", "group", "major", "own_index", "index_from",
                                         "zero_weight", "yoy", "contrib", "contrib_core",
                                         "ri_sep_prior", "core_weight")} for i in items],
        }
        for i in items:
            item_rows.append({"month": t, "name": i["name"], "code": i["code"],
                              "own_index": i["own_index"], "index_from": i["index_from"],
                              "group": i["group"], "weight_base": round(i["ri_sep_prior"], 4),
                              "weight_dec_new": i["ri_dec_new"],
                              "yoy": None if i["yoy"] is None else round(i["yoy"], 4),
                              "contrib": round(i["contrib"], 6),
                              "contrib_core": None if i["contrib_core"] is None else round(i["contrib_core"], 6)})

    # Notes for months with known collection problems at BLS.
    for s in summary:
        if s["month"] == "2025-11":
            s["note"] = ("BLS did not collect October 2025 prices and resumed collection on "
                         "November 14, 2025; more items than usual lack a published index.")

    PROCESSED.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "monthly.json").write_text(json.dumps(
        {"checks": CHECKS, "missing": MISSING, "order": list(months), "months": months}))
    cols = ["month", "status", "published_headline", "items_headline", "gap_headline",
            "published_core", "items_core", "gap_core", "filled_items", "filled_share",
            "weights_from", "note"]
    with open(PROCESSED / "monthly_summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(summary)
    with open(PROCESSED / "monthly_items.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(item_rows[0]))
        w.writeheader()
        w.writerows(item_rows)

    done = [s for s in summary if s["status"] != "missing"]
    fails = [s["month"] for s in done if s["status"] != "pass"]
    print(f"{len(done)} months computed, {len(summary) - len(done)} missing, {len(fails)} failing")
    print("largest gaps: headline %.4f, core %.4f; largest filled share %.2f%% (%s)" % (
        max(abs(s["gap_headline"]) for s in done), max(abs(s["gap_core"]) for s in done),
        *max((s["filled_share"], s["month"]) for s in done)))
    if fails:
        raise SystemExit(f"months failing the tie-out: {fails}")


if __name__ == "__main__":
    main()
