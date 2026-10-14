"""Tie-out: every number on a chart, in the page, or in a headline stat.

Recomputes from data/raw (indexes.json and the weight files) where it can, and
checks that contrib.json, the page payload and the chart CSVs all agree.
Writes TIEOUT.md. Exits non-zero on any failure.
"""
from __future__ import annotations

import csv
import json
import statistics
import sys

from common import CHARTS, PROCESSED, RAW, ROOT
from weights import build_tree

checks = []


def check(name, ours, ref, tol):
    ok = abs(ours - ref) <= tol
    checks.append((name, ours, ref, tol, ok))
    return ok


def pct(a, b):
    return (a / b - 1) * 100


def main():
    idx = json.loads((RAW / "indexes.json").read_text())
    d = json.loads((PROCESSED / "contrib.json").read_text())
    page = json.loads((PROCESSED / "page_data.json").read_text())
    items = {i["name"]: i for i in d["items"]}
    T, B = d["month"], d["base"]

    # 1. Published aggregates straight from the raw indexes.
    check("Headline 12-month change (SA0)", d["published"]["headline"], pct(idx["CUUR0000SA0"][T], idx["CUUR0000SA0"][B]), 1e-4)
    check("Core 12-month change (SA0L1E)", d["published"]["core"], pct(idx["CUUR0000SA0L1E"][T], idx["CUUR0000SA0L1E"][B]), 1e-4)
    # Rounded to one decimal, these must match the BLS release (3.7, 2.6).
    check("Headline rounds to 3.7", round(d["published"]["headline"], 1), 3.7, 1e-9)
    check("Core rounds to 2.6", round(d["published"]["core"], 1), 2.6, 1e-9)

    # 2. Items reconcile to the published aggregates.
    check("Headline: sum of item contributions", sum(i["contrib"] for i in d["items"]), d["published"]["headline"], 0.005)
    check("Core: sum of item contributions",
          sum(i["contrib_core"] for i in d["items"] if i["contrib_core"] is not None), d["published"]["core"], 0.005)

    # 3. Weights: leaves sum to 100 in both files; rolled Sep 2025 weights sum to 100; core share.
    for y in (2024, 2025):
        check(f"Dec {y} leaf weights sum to 100", sum(n.weight for n in build_tree(y) if not n.kids), 100, 0.05)
    check("Sep 2025 rolled weights sum to 100", sum(i["ri_sep_prior"] for i in d["items"]), 100, 0.01)
    check("Aug 2025 rolled weights vs printed: mean abs diff", d["aug2025_check"]["mean_abs_diff"], 0, 0.002)

    # 4. Every item with its own index: 12-month change recomputed from raw.
    bad = 0
    for i in d["items"]:
        s = idx[f"CUUR0000{i['code']}"]
        if i["own_index"] and abs(pct(s[T], s[B]) - i["yoy"]) > 1e-3:
            bad += 1
    check("Own-index items: 12-month change matches raw (count of mismatches)", bad, 0, 0)

    # 5. Page payload equals contrib.json, item by item.
    for view, key, ckey in (("headline", "ri_sep_prior", "contrib"), ("core", "core_weight", "contrib_core")):
        v = page["months"][T]["views"][view]
        mism = sum(1 for p in v["items"]
                   if abs(p["c"] - items[p["f"]][ckey]) > 1e-4 or abs(p["y"] - items[p["f"]]["yoy"]) > 1e-3
                   or abs(p["w"] - items[p["f"]][key]) > 1e-3)
        check(f"Page {view}: items matching contrib.json (mismatches)", mism, 0, 0)
        check(f"Page {view}: published rate", v["published"], d["published"][view], 1e-9)
        check(f"Page {view}: items add up to", v["sum"], sum(p["c"] for p in v["items"]), 1e-3)

    # 6. Chart CSVs equal contrib.json.
    def rows(name):
        with open(CHARTS / "numbers" / name) as fh:
            return list(csv.DictReader(fh))
    top = sorted(d["items"], key=lambda i: -i["contrib"])[:15]
    bot = sorted(d["items"], key=lambda i: i["contrib"])[:15]
    for name, sel in (("01-top-adders.csv", top), ("02-top-subtractors.csv", bot)):
        r = rows(name)
        same = [x["item"] for x in r] == [i["name"] for i in sel] and all(
            abs(float(x["contrib_pts"]) - i["contrib"]) < 1e-6 for x, i in zip(r, sel))
        check(f"Chart {name[:2]}: items and values match contrib.json", int(same), 1, 0)

    # 7. What-if, recomputed from raw.
    for code, name in (("SEME", "Health insurance"), ("SEMF01", "Prescription drugs")):
        s = idx[f"CUUR0000{code}"]
        avg = statistics.mean(pct(s[f"{y+1}-09"], s[f"{y}-09"]) for y in range(2015, 2025))
        w = d["whatif"][code]
        check(f"{name}: 10-year average Sep-Sep change", w["avg10"], avg, 1e-3)
        check(f"{name}: 12-month change", w["yoy"], pct(s[T], s[B]), 1e-3)
        it = items[name]
        check(f"{name}: headline effect of swap", w["delta_headline"], it["contrib"] / it["yoy"] * (avg - it["yoy"]), 1e-4)
        check(f"{name}: core effect of swap", w["delta_core"], it["contrib_core"] / it["yoy"] * (avg - it["yoy"]), 1e-4)
    wt = d["whatif_total"]
    check("What-if headline", wt["headline"], d["published"]["headline"] + sum(w["delta_headline"] for w in d["whatif"].values()), 1e-3)
    check("What-if core", wt["core"], d["published"]["core"] + sum(w["delta_core"] for w in d["whatif"].values()), 1e-3)
    w4 = rows("04-whatif.csv")
    check("Chart 04: headline what-if value", float(w4[0]["whatif_pct"]), wt["headline"], 1e-9)
    check("Chart 04: core what-if value", float(w4[1]["whatif_pct"]), wt["core"], 1e-9)

    # 8. History chart end values.
    h = rows("03-health-insurance-rx-history.csv")
    for code in ("SEME", "SEMF01"):
        last = [x for x in h if x["series"] == code][-1]
        check(f"Chart 03: {code} last value is {T}", int(last["month"] == T), 1, 0)
        check(f"Chart 03: {code} last value", float(last["yoy_pct"]), d["whatif"][code]["yoy"], 1e-3)

    # Source coverage: how much weight rests on a measured index vs a fill.
    filled = [i for i in d["items"] if not i["own_index"]]
    cov = {
        "items": len(d["items"]), "own_index_items": len(d["items"]) - len(filled), "filled_items": len(filled),
        "filled_weight_headline": round(sum(i["ri_sep_prior"] for i in filled), 3),
        "filled_contrib_headline": round(sum(i["contrib"] for i in filled), 4),
        "filled_weight_core": round(sum(i["core_weight"] or 0 for i in filled), 3),
        "filled_contrib_core": round(sum(i["contrib_core"] or 0 for i in filled), 4),
    }

    lines = ["# Tie-out", "", f"Run by `scripts/tieout.py` on the October 14, 2026 pull. Release month {T}.", "",
             "| Check | Ours | Reference | Tolerance | Result |", "|---|---|---|---|---|"]
    for name, o, r, t, ok in checks:
        lines.append(f"| {name} | {o:.4f} | {r:.4f} | {t:g} | {'pass' if ok else '**FAIL**'} |")
    lines += ["", "## Source coverage", "",
              f"- {cov['own_index_items']} of {cov['items']} items have their own published index for the months used.",
              f"- {cov['filled_items']} items ({cov['filled_weight_headline']}% of the CPI's weight) do not. Their change is filled "
              f"from the part of their parent's published change that the parent's published items do not explain.",
              f"- Those filled items contribute {cov['filled_contrib_headline']:+.4f} points of the headline and "
              f"{cov['filled_contrib_core']:+.4f} points of core ({cov['filled_weight_core']}% of core's weight).",
              "- BLS's own uncertainty (standard errors, https://www.bls.gov/cpi/tables/variance-estimates/) has not been "
              "pulled yet. Single items are less precise than the total.",
              "", "### Filled items by parent", "", "| Parent (published index) | Items filled | Weight | Contribution | Implied change |",
              "|---|---|---|---|---|"]
    for f in d["fills"]:
        imp = f"{f['implied_yoy']:+.1f}%" if f["implied_yoy"] is not None else "n/a (weight about 0)"
        lines.append(f"| {f['parent']} | {', '.join(f['items'])} | {f['weight']:.3f} | {f['contrib']:+.4f} | {imp} |")
    (ROOT / "TIEOUT.md").write_text("\n".join(lines) + "\n")
    fails = [c for c in checks if not c[4]]
    print(f"{len(checks) - len(fails)} of {len(checks)} checks pass")
    for c in fails:
        print("FAIL", c)
    print(cov)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
