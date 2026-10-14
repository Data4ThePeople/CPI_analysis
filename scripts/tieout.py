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


def decode(p):
    """Expand the compact page payload (see build.encode) into per-view item lists."""
    for t in p["order"]:
        M = p["months"][t]
        M["views"] = {}
        for k, v in enumerate(("headline", "core")):
            items = [{"f": p["items"][j][1], "y": r[0], "c": r[1 + k], "w": r[3 + k]}
                     for j, r in enumerate(M["r"]) if r and r[1 + k] is not None]
            M["views"][v] = {"published": M["pub"][k], "sum": M["sum"][k], "items": items}
    return p


def bls_published_rates():
    """BLS's own 12-month percent changes (one decimal) for all items and core,
    from the API's calculations option. Cached in data/raw."""
    path = RAW / "bls_12mo_published.json"
    if not path.exists():
        import urllib.request
        from common import API_URL, USER_AGENT, get_key
        body = json.dumps({"seriesid": ["CUUR0000SA0", "CUUR0000SA0L1E"], "startyear": "2016",
                           "endyear": "2026", "calculations": True,
                           "registrationkey": get_key("BLS_API_KEY")}).encode()
        req = urllib.request.Request(API_URL, data=body, headers={"Content-type": "application/json",
                                                                  "User-Agent": USER_AGENT})
        r = json.load(urllib.request.urlopen(req, timeout=120))
        out = {}
        for sr in r["Results"]["series"]:
            out[sr["seriesID"]] = {f"{x['year']}-{x['period'][1:]}": float(x["calculations"]["pct_changes"]["12"])
                                   for x in sr["data"] if x["period"].startswith("M") and x["period"] != "M13"
                                   and x.get("calculations", {}).get("pct_changes", {}).get("12") not in (None, "-")}
        path.write_text(json.dumps(out, indent=0))
    return json.loads(path.read_text())


def monthly_checks(idx):
    """Every month in the animated page: rates from raw, BLS's own rounded
    rates, items adding up, filled share, and the page payload."""
    m = json.loads((PROCESSED / "monthly.json").read_text())
    page = decode(json.loads((PROCESSED / "over-time_data.json").read_text()))
    wc = json.loads((PROCESSED / "weights_check.json").read_text())
    blsr = bls_published_rates()
    rows = []
    for t in m["order"]:
        M = m["months"][t]
        b = M["base"]
        ph = pct(idx["CUUR0000SA0"][t], idx["CUUR0000SA0"][b])
        pc = pct(idx["CUUR0000SA0L1E"][t], idx["CUUR0000SA0L1E"][b])
        sh = sum(i["contrib"] for i in M["items"])
        sc = sum(i["contrib_core"] for i in M["items"] if i["contrib_core"] is not None)
        filled = sum(i["ri_sep_prior"] for i in M["items"] if not i["own_index"])
        P = page["months"][t]["views"]
        pg = max(abs(P["headline"]["sum"] - sh), abs(P["core"]["sum"] - sc))
        rnd = (round(ph, 1) == blsr["CUUR0000SA0"].get(t) and round(pc, 1) == blsr["CUUR0000SA0L1E"].get(t))
        wy = [str(int(M["base"][:4])), t[:4]] if t[5:] != "12" else [t[:4]]
        wok = all(wc[y]["max_abs_diff"] <= 0.0015 for y in wy if y in wc)
        ok = (abs(sh - ph) <= 0.005 and abs(sc - pc) <= 0.005 and filled <= 10 and pg <= 0.001
              and abs(M["published"]["headline"] - ph) < 1e-9 and rnd and wok)
        rows.append((t, ph, sh, pc, sc, filled, rnd, wok, pg, ok))
    return rows, m.get("missing", {}), wc


def main():
    idx = json.loads((RAW / "indexes.json").read_text())
    d = json.loads((PROCESSED / "contrib.json").read_text())
    page = decode(json.loads((PROCESSED / "index_data.json").read_text()))
    items = {i["name"]: i for i in d["items"]}
    T, B = d["month"], d["base"]

    # 1. Published aggregates straight from the raw indexes.
    check("Headline 12-month change (SA0)", d["published"]["headline"], pct(idx["CUUR0000SA0"][T], idx["CUUR0000SA0"][B]), 1e-4)
    check("Core 12-month change (SA0L1E)", d["published"]["core"], pct(idx["CUUR0000SA0L1E"][T], idx["CUUR0000SA0L1E"][B]), 1e-4)
    # Rounded to one decimal, these must match the BLS release (3.7, 2.6).
    check("Headline rounds to 3.7", round(d["published"]["headline"], 1), 3.7, 1e-9)
    check("Core rounds to 2.6", round(d["published"]["core"], 1), 2.6, 1e-9)

    # 2. Items reconcile to the published aggregates.
    check("Headline: sum of item contributions", sum(i["contrib"] for i in d["items"]), d["published"]["headline"], 0.002)
    check("Core: sum of item contributions",
          sum(i["contrib_core"] for i in d["items"] if i["contrib_core"] is not None), d["published"]["core"], 0.002)

    # 3. Weights: leaves sum to 100 in both files; rolled Sep 2025 weights sum to 100; core share.
    for y in (2024, 2025):
        check(f"Dec {y} leaf weights sum to 100", sum(n.weight for n in build_tree(y) if not n.kids), 100, 0.05)
    check("Sep 2025 rolled weights sum to 100", sum(i["ri_sep_prior"] for i in d["items"]), 100, 0.01)
    check("Aug 2025 rolled weights vs printed: mean abs diff", d["aug2025_check"]["mean_abs_diff"], 0, 0.002)

    # 4. Every item with its own index: 12-month change recomputed from raw.
    bad = 0
    for i in d["items"]:
        s = idx[f"CUUR0000{i['code']}"]
        if i["own_index"] and not i["zero_weight"] and abs(pct(s[T], s[B]) - i["yoy"]) > 1e-3:
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
    for name, sel in (("05-top-adders.csv", top), ("06-top-subtractors.csv", bot)):
        r = rows(name)
        same = [x["item"] for x in r] == [i["name"] for i in sel] and all(
            abs(float(x["contrib_pts"]) - i["contrib"]) < 1e-6 for x, i in zip(r, sel))
        check(f"Chart {name[:2]}: items and values match contrib.json", int(same), 1, 0)

    # Chart 02 (waterfall): steps add to the item total; chart 03: the fastest risers.
    wf = rows("02-waterfall.csv")
    check("Chart 02: waterfall steps add to the items total", sum(float(x["contrib_pts"]) for x in wf[:-1]),
          sum(i["contrib"] for i in d["items"]), 1e-4)
    check("Chart 02: waterfall total", float(wf[-1]["contrib_pts"]), d["published"]["headline"], 2e-3)
    wc3 = rows("03-waterfall-core.csv")
    core_items = [i for i in d["items"] if i["contrib_core"] is not None]
    check("Chart 03: core waterfall steps add to the core items total", sum(float(x["contrib_pts"]) for x in wc3[:-1]),
          sum(i["contrib_core"] for i in core_items), 1e-4)
    check("Chart 03: core waterfall total", float(wc3[-1]["contrib_pts"]), d["published"]["core"], 2e-3)
    fr = rows("04-fastest-rising.csv")
    own = sorted((i for i in d["items"] if i["own_index"] and i["yoy"] is not None), key=lambda i: -i["yoy"])[:15]
    same = [x["item"] for x in fr] == [i["name"] for i in own] and all(
        abs(float(x["yoy_pct"]) - pct(idx[f"CUUR0000{i['code']}"][T], idx[f"CUUR0000{i['code']}"][B])) < 1e-3
        for x, i in zip(fr, own))
    check("Chart 04: fastest risers match raw indexes", int(same), 1, 0)

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
    w4 = rows("08-whatif.csv")
    check("Chart 08: headline what-if value", float(w4[0]["whatif_pct"]), wt["headline"], 1e-9)
    check("Chart 08: core what-if value", float(w4[1]["whatif_pct"]), wt["core"], 1e-9)

    # 8. History chart end values.
    h = rows("07-health-insurance-rx-history.csv")
    for code in ("SEME", "SEMF01"):
        last = [x for x in h if x["series"] == code][-1]
        check(f"Chart 07: {code} last value is {T}", int(last["month"] == T), 1, 0)
        check(f"Chart 07: {code} last value", float(last["yoy_pct"]), d["whatif"][code]["yoy"], 1e-3)

    # Source coverage: how much weight rests on a measured index vs a fill.
    filled = [i for i in d["items"] if not i["own_index"]]
    cov = {
        "items": len(d["items"]), "own_index_items": len(d["items"]) - len(filled), "filled_items": len(filled),
        "filled_weight_headline": round(sum(i["ri_sep_prior"] for i in filled), 3),
        "filled_contrib_headline": round(sum(i["contrib"] for i in filled), 4),
        "filled_weight_core": round(sum(i["core_weight"] or 0 for i in filled), 3),
        "filled_contrib_core": round(sum(i["contrib_core"] or 0 for i in filled), 4),
    }

    mrows, missing, wc = monthly_checks(idx)
    mfail = [r[0] for r in mrows if not r[-1]]
    check(f"Monthly series: months passing every check (of {len(mrows)})", len(mrows) - len(mfail), len(mrows), 0)
    check("Monthly series: largest headline gap (pts)", max(abs(r[2] - r[1]) for r in mrows), 0, 0.005)
    check("Monthly series: largest core gap (pts)", max(abs(r[4] - r[3]) for r in mrows), 0, 0.005)
    check("Weight roll-forward vs printed December weights, 2015-2025: largest diff",
          max(v["max_abs_diff"] for v in wc.values()), 0, 0.0015)
    sep = next(r for r in mrows if r[0] == T)
    check("Monthly series September 2026 equals contrib.json (headline sum)", sep[2], sum(i["contrib"] for i in d["items"]), 1e-3)   # contrib.json rounds items to 5 decimals

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
    lines += ["", "## Monthly series, October 2016 to September 2026", "",
              "Each month passes when: the published 12-month rate recomputed from the raw all-items and core "
              "indexes matches, rounded to one decimal, the rate BLS itself reports (API calculations); "
              "the items add up to within 0.005 points of it, for headline and for core; items without their "
              "own index carry no more than 10% of the weight; the weight years it uses pass the "
              "roll-forward check; and the page draws the same totals.", "",
              "Missing: " + "; ".join(f"{k}: {v}" for k, v in missing.items()), "",
              "### Weight roll-forward check", "",
              "Each December's weights rolled forward a year, compared with what BLS printed for the next "
              "December on the same weight basis (`scripts/weights_check.py`).", "",
              "| December | Compared with | Items | Mean abs diff | Max abs diff |", "|---|---|---|---|---|"]
    for y, v in wc.items():
        lines.append(f"| {y} | {v['source']} | {v['matched']} | {v['mean_abs_diff']:.5f} | {v['max_abs_diff']:.4f} |")
    lines += ["", "### Every month", "",
              "| Month | Headline | Items add up to | Gap | Core | Items add up to | Gap | Filled weight | Matches BLS rounded | Result |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for t, ph, sh, pc, sc, f, rnd, wok, pg, ok in mrows:
        lines.append(f"| {t} | {ph:.3f} | {sh:.3f} | {sh - ph:+.4f} | {pc:.3f} | {sc:.3f} | {sc - pc:+.4f} | {f:.2f}% | "
                     f"{'yes' if rnd else 'no'} | {'pass' if ok else '**FAIL**'} |")
    (ROOT / "TIEOUT.md").write_text("\n".join(lines) + "\n")
    fails = [c for c in checks if not c[4]]
    print(f"{len(checks) - len(fails)} of {len(checks)} checks pass")
    for c in fails:
        print("FAIL", c)
    print(cov)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
