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

from common import RAW, PROCESSED, TARGET
from fetch import item_codes, norm
from weights import build_tree

T = f"{TARGET[0]}-{TARGET[1]:02d}"          # 2026-09
B = f"{TARGET[0]-1}-{TARGET[1]:02d}"        # 2025-09
DEC_PRIOR = f"{TARGET[0]-2}-12"             # 2024-12, base of the 2025 weights
DEC_NEW = f"{TARGET[0]-1}-12"               # 2025-12, base of the 2026 weights
AVG_YEARS = range(TARGET[0] - 11, TARGET[0] - 1)   # Sep 2015->2016 ... 2024->2025
WHATIF = {"SEME": "Health insurance", "SEMF01": "Prescription drugs"}
ENERGY_PARENTS = {"Household energy", "Motor fuel"}
FOOD_PARENT = "Food"


def series():
    return json.loads((RAW / "indexes.json").read_text())


YOY_MONTHS = (B, T)
ROLL_MONTHS = (DEC_PRIOR, "2025-08", B, DEC_NEW)


def leaves_with_index(nodes, codes, idx):
    """Every leaf with the series it is priced by.

    `code` prices the 12-month change: the leaf's own index when it has both
    September values, otherwise the nearest parent that does. `wcode` rolls the
    weights forward and needs the four weight months. BLS has paused or stopped
    some indexes (legal services, household operations, others), so a leaf can
    use its own index for one and a parent for the other.
    """
    def first(chain, months):
        for c in chain:
            code = codes.get(norm(c.name))
            sid = f"CUUR0000{code}"
            if code and sid in idx and all(m in idx[sid] for m in months):
                return c, code
        raise RuntimeError(f"no index for {chain[0].name}")

    out = []
    for n in nodes:
        if n.kids:
            continue
        chain, cur = [], n
        while cur is not None:
            chain.append(cur)
            cur = nodes[cur.parent] if cur.parent is not None else None
        src, code = first(chain, YOY_MONTHS)
        wsrc, wcode = first(chain, ROLL_MONTHS)
        anc = [c.name for c in chain[1:]]
        group = ("Energy" if ENERGY_PARENTS & set(anc) else
                 "Food" if FOOD_PARENT in anc else "Core")
        out.append({"name": n.name, "code": code, "wcode": wcode,
                    "own_index": src is n, "index_from": src.name,
                    "weight_index_from": wsrc.name,
                    "major": anc[-2] if len(anc) > 1 else (anc[-1] if anc else n.name),
                    "parent": anc[0] if anc else "",
                    "group": group, "ri_dec_prior": n.weight})
    return out


def rolled(leaves, idx, month):
    """Relative importance at `month`: December weights x price relative, rescaled to 100."""
    raw = {l["name"]: l["ri_dec_prior"] * idx[f"CUUR0000{l['wcode']}"][month]
           / idx[f"CUUR0000{l['wcode']}"][DEC_PRIOR] for l in leaves}
    s = sum(raw.values())
    return {k: 100 * v / s for k, v in raw.items()}, s


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


def pct(a, b):
    return (a / b - 1) * 100


def chained(w_sep, rel_agg, ri_new, split, full_rel):
    """Contribution in percentage points; weights in percent of the aggregate."""
    return w_sep * (split - 1) + rel_agg * ri_new * (full_rel / split - 1)


def main():
    idx = series()
    codes = item_codes()
    nodes24, nodes25 = build_tree(2024), build_tree(2025)
    byname = {n.name: n for n in nodes24}
    leaves = leaves_with_index(nodes24, codes, idx)
    ri25 = {n.name: n.weight for n in nodes25 if not n.kids}
    if {l["name"] for l in leaves} != set(ri25):
        raise RuntimeError("2024 and 2025 leaf sets differ")

    # Check rolled weights against the August 2025 column BLS printed.
    w_aug, _ = rolled(leaves, idx, "2025-08")
    text, _ = printed_weights(RAW / "release_2025-09.htm", "Aug 2025")
    chk = check_printed(leaves, w_aug, text)
    diffs = [abs(a - b) for _, a, b in chk]
    w_sep, _ = rolled(leaves, idx, B)

    SA0, CORE = idx["CUUR0000SA0"], idx["CUUR0000SA0L1E"]
    all_yoy, core_yoy = pct(SA0[T], SA0[B]), pct(CORE[T], CORE[B])
    rel_all, rel_core = SA0[DEC_NEW] / SA0[B], CORE[DEC_NEW] / CORE[B]
    is_core = {l["name"]: l["group"] == "Core" for l in leaves}
    core_w = sum(w_sep[n] for n, c in is_core.items() if c)
    core_ri25 = sum(ri25[n] for n, c in is_core.items() if c)

    def contribs(names, s, sw):
        """Headline and core contribution of a set of leaves priced by s."""
        split, full = sw[DEC_NEW] / sw[B], s[T] / s[B]
        W = sum(w_sep[n] for n in names)
        R = sum(ri25[n] for n in names)
        h = chained(W, rel_all, R, split, full)
        if all(is_core[n] for n in names):
            c = chained(100 * W / core_w, rel_core, 100 * R / core_ri25, split, full)
        elif any(is_core[n] for n in names):
            raise RuntimeError(f"mixed core/non-core set: {names}")
        else:
            c = None
        return h, c

    items = {}
    for l in leaves:
        n = l["name"]
        s, sw = idx[f"CUUR0000{l['code']}"], idx[f"CUUR0000{l['wcode']}"]
        h, c = contribs([n], s, sw)
        chg = pct(s[T], s[B])
        items[n] = dict(l, ri_sep_prior=round(w_sep[n], 4), ri_dec_new=ri25[n],
                        yoy=chg, yoy_source="published" if l["own_index"] else "parent",
                        contrib=h, contrib_simple=w_sep[n] * chg / 100,
                        core_weight=100 * w_sep[n] / core_w if is_core[n] else None,
                        contrib_core=c)

    def leaves_under(node):
        return [node.name] if not node.kids else [
            x for k in node.kids for x in leaves_under(nodes24[k])]

    # Fill unpublished leaves from their parent, deepest parent first.
    fills = []
    parents = {l["index_from"] for l in leaves if not l["own_index"]}
    for P in sorted(parents, key=lambda p: -byname[p].level):
        under = leaves_under(byname[P])
        fill = [n for n in under if items[n]["index_from"] == P and not items[n]["own_index"]]
        rest = [n for n in under if n not in fill]
        code = codes[norm(P)]
        s = idx[f"CUUR0000{code}"]
        if DEC_NEW not in s:
            raise RuntimeError(f"{P} lacks {DEC_NEW}")
        hP, cP = contribs(under, s, s)
        h_res = hP - sum(items[n]["contrib"] for n in rest)
        c_res = (cP - sum(items[n]["contrib_core"] for n in rest)) if cP is not None else None
        Wf = sum(w_sep[n] for n in fill)
        Wh = sum(abs(items[n]["contrib"]) for n in fill)
        for n in fill:
            share = w_sep[n] / Wf if Wf else 1 / len(fill)
            it = items[n]
            it["contrib"] = h_res * share
            if c_res is not None:
                it["contrib_core"] = c_res * share
            # Implied 12-month change, for color only: contribution / weight.
            it["yoy"] = h_res / Wf * 100 if Wf > 0.001 else pct(s[T], s[B])
            it["yoy_source"] = "filled from " + P
        fills.append({"parent": P, "items": fill, "weight": round(Wf, 4),
                      "contrib": round(h_res, 5),
                      "implied_yoy": round(h_res / Wf * 100, 3) if Wf > 0.001 else None})

    rows = list(items.values())
    head_sum = sum(i["contrib"] for i in rows)
    core_sum = sum(i["contrib_core"] for i in rows if i["contrib_core"] is not None)
    simple_sum = sum(i["contrib_simple"] for i in rows)

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
            "food_share": round(sum(w_sep[l["name"]] for l in leaves if l["group"] == "Food"), 4),
            "energy_share": round(sum(w_sep[l["name"]] for l in leaves if l["group"] == "Energy"), 4),
            "filled_share": round(sum(w_sep[l["name"]] for l in leaves if not l["own_index"]), 4),
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
                "weight_index_from", "major", "parent", "group", "ri_dec_prior",
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
