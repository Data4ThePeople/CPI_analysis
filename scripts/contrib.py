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


# Each job needs certain months. A leaf uses its own index for a job when that
# index has those months, otherwise its nearest published parent's.
JOBS = {"code": (B, T),                  # the 12-month change
        "wcode": (DEC_PRIOR, B),         # rolling the weight to September 2025
        "scode": (B, DEC_NEW),           # splitting the year at the January reweight
        "acode": (DEC_PRIOR, "2025-08")} # the August 2025 weight check only


def leaves_with_index(nodes, codes, idx):
    """Every leaf with the series used for each job (see JOBS).

    BLS has paused or stopped some indexes (household operations, legal
    services, others), and some publish every other month, so a leaf can use
    its own index for one job and a parent's for another.
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
        row = {"name": n.name}
        for job, months in JOBS.items():
            src, code = first(chain, months)
            row[job] = code
            row[job + "_from"] = src.name
        anc = [c.name for c in chain[1:]]
        group = ("Energy" if ENERGY_PARENTS & set(anc) else
                 "Food" if FOOD_PARENT in anc else "Core")
        row.update({"own_index": row["code_from"] == n.name, "index_from": row["code_from"],
                    "major": anc[-2] if len(anc) > 1 else (anc[-1] if anc else n.name),
                    "parent": anc[0] if anc else "", "group": group, "ri_dec_prior": n.weight})
        out.append(row)
    return out


def rolled(leaves, idx, month, job="wcode"):
    """BLS relative importance at `month`: the December weight times the item's
    price relative, divided by the all-items relative. Not rescaled to 100."""
    A = idx["CUUR0000SA0"]
    all_rel = A[month] / A[DEC_PRIOR]
    return {l["name"]: l["ri_dec_prior"] * idx[f"CUUR0000{l[job]}"][month]
            / idx[f"CUUR0000{l[job]}"][DEC_PRIOR] / all_rel for l in leaves}, all_rel


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
    ri24 = {l["name"]: l["ri_dec_prior"] for l in leaves}
    if set(ri24) != set(ri25):
        raise RuntimeError("2024 and 2025 leaf sets differ")
    zero = {n for n in ri24 if ri24[n] == 0 and ri25[n] == 0}

    # Check rolled weights against the August 2025 column BLS printed.
    w_aug, _ = rolled(leaves, idx, "2025-08", "acode")
    text, _ = printed_weights(RAW / "release_2025-09.htm", "Aug 2025")
    chk = check_printed(leaves, w_aug, text)
    diffs = [abs(a - b) for _, a, b in chk]
    w_sep, all_rel_sep = rolled(leaves, idx, B)

    SA0, CORE = idx["CUUR0000SA0"], idx["CUUR0000SA0L1E"]
    all_yoy, core_yoy = pct(SA0[T], SA0[B]), pct(CORE[T], CORE[B])
    rel_all, rel_core = SA0[DEC_NEW] / SA0[B], CORE[DEC_NEW] / CORE[B]
    is_core = {l["name"]: l["group"] == "Core" for l in leaves}
    # Core's share of all items in September 2025, rolled the same way BLS rolls any aggregate.
    core_w = (sum(ri24[n] for n, c in is_core.items() if c)
              * (CORE[B] / CORE[DEC_PRIOR]) / all_rel_sep)
    core_ri25 = sum(ri25[n] for n, c in is_core.items() if c)

    def terms(W, R, split, full, core):
        """The two pieces of the chained contribution, headline and (if core) core."""
        h = (W * (split - 1), rel_all * R * (full / split - 1))
        c = ((100 * W / core_w) * (split - 1),
             rel_core * (100 * R / core_ri25) * (full / split - 1)) if core else None
        return h, c

    items = {}
    for l in leaves:
        n = l["name"]
        s, ss = idx[f"CUUR0000{l['code']}"], idx[f"CUUR0000{l['scode']}"]
        full, split = s[T] / s[B], ss[DEC_NEW] / ss[B]
        h, c = terms(w_sep[n], ri25[n], split, full, is_core[n])
        items[n] = dict(l, w=w_sep[n], h=list(h), cc=list(c) if c else None,
                        yoy=pct(s[T], s[B]), yoy_source="published" if l["own_index"] else "parent",
                        contrib_simple=w_sep[n] * pct(s[T], s[B]) / 100)

    def leaves_under(node):
        return [node.name] if not node.kids else [
            x for k in node.kids for x in leaves_under(nodes24[k])]

    # Fill unpublished leaves from their parent, deepest parent first. The
    # parent's own rolled weight and index give its contribution, one term at a
    # time; what the parent's other leaves do not explain goes to the filled
    # leaves, shared by their December weights.
    fills = []
    parents = {l["index_from"] for l in leaves if not l["own_index"]}
    for P in sorted(parents, key=lambda p: -byname[p].level):
        under = leaves_under(byname[P])
        fill = [n for n in under if items[n]["index_from"] == P and not items[n]["own_index"]]
        rest = [n for n in under if n not in fill]
        s = idx[f"CUUR0000{codes[norm(P)]}"]
        for m in (DEC_PRIOR, B, DEC_NEW, T):
            if m not in s:
                raise RuntimeError(f"{P} lacks {m}")
        core = is_core[under[0]]
        if any(is_core[n] != core for n in under):
            raise RuntimeError(f"mixed core/non-core under {P}")
        WP = sum(ri24[n] for n in under) * (s[B] / s[DEC_PRIOR]) / all_rel_sep
        RP = sum(ri25[n] for n in under)
        hP, cP = terms(WP, RP, s[DEC_NEW] / s[B], s[T] / s[B], core)
        Wf = WP - sum(items[n]["w"] for n in rest)
        h_res = [hP[k] - sum(items[n]["h"][k] for n in rest) for k in (0, 1)]
        c_res = [cP[k] - sum(items[n]["cc"][k] for n in rest) for k in (0, 1)] if core else None
        f24 = sum(ri24[n] for n in fill)
        f25 = sum(ri25[n] for n in fill)
        for n in fill:
            a = ri24[n] / f24 if f24 else 1 / len(fill)
            b = ri25[n] / f25 if f25 else 1 / len(fill)
            it = items[n]
            it["w"] = Wf * a
            it["h"] = [h_res[0] * a, h_res[1] * b]
            if core:
                it["cc"] = [c_res[0] * a, c_res[1] * b]
            tot = sum(it["h"])
            it["yoy"] = (tot / it["w"] * 100) if it["w"] > 0.001 else None
            it["yoy_source"] = "filled from " + P
        fills.append({"parent": P, "items": fill, "weight": round(Wf, 4),
                      "contrib": round(sum(h_res), 5),
                      "implied_yoy": round(sum(h_res) / Wf * 100, 3) if Wf > 0.001 else None})

    for n, it in items.items():
        if n in zero:                      # no weight in either year: nothing to show
            it["h"], it["yoy"] = [0.0, 0.0], None
            if it["cc"]:
                it["cc"] = [0.0, 0.0]
        it["zero_weight"] = n in zero
        it["ri_sep_prior"] = round(it["w"], 4)
        it["ri_dec_new"] = ri25[n]
        it["contrib"] = sum(it["h"])
        it["contrib_core"] = sum(it["cc"]) if it["cc"] else None
        it["core_weight"] = 100 * it["w"] / core_w if is_core[n] else None
        for k in ("w", "h", "cc"):
            it.pop(k)

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
