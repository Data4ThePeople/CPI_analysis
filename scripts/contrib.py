"""Each leaf item's contribution to 12-month headline and core inflation.

Method (DATASETS.md, chosen October 14, 2026):

1. September 2025 weights: the December 2024 relative importances rolled
   forward by each item's price change relative to the total (how BLS computes
   the monthly relative importance it prints).
2. Chained contribution across the January 2026 weight reset:
     c = w_Sep25 x (I_Dec25/I_Sep25 - 1)
       + (All_Dec25/All_Sep25) x RI_Dec25 x (I_Sep26/I_Dec25 - 1)
   Core uses the same formula with core-only weights and the core index.
3. Items BLS does not publish (unsampled, or paused like household
   operations) get the part of their nearest published parent's contribution
   that the parent's published items do not explain, shared by weight.
   Deepest parents first, so nested fills use the already-filled values.
"""
from __future__ import annotations

import csv
import html
import json
import re
import statistics

from chain import Inputs, compute_month, months_for, pct, rolled
from common import RAW, PROCESSED, TARGET

T, B, DEC_PRIOR, DEC_NEW = months_for(f"{TARGET[0]}-{TARGET[1]:02d}")   # 2026-09, 2025-09, 2024-12, 2025-12
AVG_YEARS = range(TARGET[0] - 11, TARGET[0] - 1)   # Sep 2015->2016 ... 2024->2025
WHATIF = {"SEME": "Health insurance", "SEMF01": "Prescription drugs"}


def printed_weights(path, label):
    """Item -> relative importance printed in a release's Table 2."""
    t = html.unescape(re.sub(r"<[^>]+>", " ", path.read_text(errors="ignore")))
    t = re.sub(r"\s+", " ", t)
    i = t.find("Table 2.")
    return t[i:], label


def check_printed(leaves, w, text):
    """Compare our rolled weights to a printed column; returns rows."""
    rows = []
    for l in leaves:
        pat = re.escape(l["name"]) + r"(?: \( ?\d+ ?\))* ([0-9]+\.[0-9]{3})"
        m = re.search(pat, text)
        if m:
            rows.append((l["name"], float(m.group(1)), w[l["name"]]))
    return rows


def main():
    inp = Inputs()
    idx = inp.idx
    r = compute_month(inp, T, extra_jobs={"acode": (DEC_PRIOR, "2025-08")})
    leaves, rows, zero, fills = r["leaves"], r["items"], set(r["zero"]), r["fills"]
    for i in rows:
        i.pop("_h"), i.pop("_c")
    all_yoy, core_yoy = r["published"]["headline"], r["published"]["core"]
    head_sum, core_sum, simple_sum = r["sum"]["headline"], r["sum"]["core"], r["sum_simple"]
    core_w = r["core_w"]

    # Check rolled weights against the August 2025 column BLS printed.
    w_aug, _ = rolled(leaves, idx, "2025-08", DEC_PRIOR, "acode")
    text, _ = printed_weights(RAW / "release_2025-09.htm", "Aug 2025")
    chk = check_printed(leaves, w_aug, text)
    diffs = [abs(a - b) for _, a, b in chk]

    # What-if: health insurance and prescription drugs at their 10-year average.
    # Effective weight = chained contribution / actual change, so the swap uses
    # the same weights that produced the actual contribution.
    whatif = {}
    for code, label in WHATIF.items():
        s = idx[f"CUUR0000{code}"]
        hist = [{"year": y + 1, "yoy": round(pct(s[f"{y+1}-09"], s[f"{y}-09"]), 4)}
                for y in AVG_YEARS]
        avg = statistics.mean(h["yoy"] for h in hist)
        it = next(i for i in rows if i["code"] == code and i["own_index"])
        eff_h = it["contrib"] / it["yoy"]
        eff_c = it["contrib_core"] / it["yoy"]
        whatif[code] = {
            "name": label, "yoy": round(it["yoy"], 4), "avg10": round(avg, 4),
            "history": hist,
            "effective_weight_headline": round(100 * eff_h, 4),
            "effective_weight_core": round(100 * eff_c, 4),
            "contrib": round(it["contrib"], 5), "contrib_core": round(it["contrib_core"], 5),
            "contrib_avg": round(eff_h * avg, 5), "contrib_core_avg": round(eff_c * avg, 5),
            "delta_headline": round(eff_h * (avg - it["yoy"]), 5),
            "delta_core": round(eff_c * (avg - it["yoy"]), 5),
        }
    hist_series = {}
    for code in WHATIF:
        s = idx[f"CUUR0000{code}"]
        hist_series[code] = {m: round(pct(v, s[f"{int(m[:4])-1}{m[4:]}"]), 4)
                             for m, v in s.items() if f"{int(m[:4])-1}{m[4:]}" in s}
    d_head = sum(w["delta_headline"] for w in whatif.values())
    d_core = sum(w["delta_core"] for w in whatif.values())

    for i in rows:
        for k in ("yoy", "contrib", "contrib_simple", "core_weight", "contrib_core"):
            if i[k] is not None:
                i[k] = round(i[k], 5)
    names = [i["name"] for i in rows]
    if len(names) != len(set(names)):
        raise RuntimeError("duplicate item names")

    out = {
        "month": T, "base": B,
        "published": {"headline": round(all_yoy, 4), "core": round(core_yoy, 4)},
        "sum": {"headline": round(head_sum, 4), "core": round(core_sum, 4)},
        "sum_simple_sep2025_weights": round(simple_sum, 4),
        "weights": {
            "core_share_sep_prior": round(core_w, 4),
            "sum_sep_prior": round(sum(i["ri_sep_prior"] for i in rows), 4),
            "zero_weight_items": sorted(zero),
            "food_share": round(sum(i["ri_sep_prior"] for i in rows if i["group"] == "Food"), 4),
            "energy_share": round(sum(i["ri_sep_prior"] for i in rows if i["group"] == "Energy"), 4),
            "filled_share": round(sum(i["ri_sep_prior"] for i in rows if not i["own_index"]), 4),
            "filled_items": sum(1 for l in leaves if not l["own_index"]),
        },
        "aug2025_check": {"matched": len(chk), "max_abs_diff": round(max(diffs), 4),
                          "mean_abs_diff": round(statistics.mean(diffs), 5),
                          "worst": sorted(chk, key=lambda r: -abs(r[1] - r[2]))[:5]},
        "fills": fills,
        "whatif": whatif,
        "whatif_total": {"delta_headline": round(d_head, 4), "delta_core": round(d_core, 4),
                         "headline": round(all_yoy + d_head, 4),
                         "core": round(core_yoy + d_core, 4)},
        "history": hist_series,
        "items": sorted(rows, key=lambda i: -i["contrib"]),
    }
    PROCESSED.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "contrib.json").write_text(json.dumps(out, indent=1))
    with open(PROCESSED / "contrib.csv", "w", newline="") as fh:
        cols = ["name", "code", "own_index", "index_from", "yoy_source", "wcode",
                "wcode_from", "scode", "scode_from", "zero_weight", "major", "parent", "group", "ri_dec_prior",
                "ri_sep_prior", "ri_dec_new", "yoy", "contrib", "contrib_simple",
                "core_weight", "contrib_core"]
        wr = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(out["items"])
    print(json.dumps({k: out[k] for k in ("published", "sum", "sum_simple_sep2025_weights",
                                           "weights", "whatif_total")}, indent=1))
    for w in whatif.values():
        print(w["name"], {k: w[k] for k in w if k != "history"})


if __name__ == "__main__":
    main()
