"""Chained item contributions to 12-month CPI inflation, for any month.

For a target month T in year Y, with base B one year earlier:

    c = w_B x (I_Dec/I_B - 1) + (All_Dec/All_B) x RI_Dec x (I_T/I_Dec - 1)

where Dec is December of year Y-1 (the January weight reset), w_B is the
December Y-2 relative importance rolled forward to B, and RI_Dec is the
December Y-1 relative importance. Core uses the same formula with core-only
weights and the core index. When T is a December, B is the December the
weights are set at, so the first term is zero. See DATASETS.md.

Leaves without a published index are filled from the part of their nearest
published parent that the parent's other leaves do not explain, one term at a
time, deepest parent first.
"""
from __future__ import annotations

import json

from common import RAW
from fetch import item_codes, norm
from weights import canonical_tree

ENERGY_PARENTS = {"Household energy", "Motor fuel"}
FOOD_PARENT = "Food"


def series():
    return json.loads((RAW / "indexes.json").read_text())


def months_for(t: str):
    """(T, B, DEC_PRIOR, DEC_NEW) for a target month 'YYYY-MM'."""
    y, m = int(t[:4]), int(t[5:])
    return t, f"{y-1}-{m:02d}", f"{y-2}-12", f"{y-1}-12"


def pct(a, b):
    return (a / b - 1) * 100


class Inputs:
    """Everything read from disk once and shared across months."""

    def __init__(self):
        self.idx = series()
        self.codes = item_codes()
        self._trees = {}

    def tree(self, year):
        if year not in self._trees:
            self._trees[year] = canonical_tree(year)
        return self._trees[year]


def leaves_with_index(nodes, codes, idx, jobs):
    """Every leaf with the series used for each job.

    Each job needs certain months. A leaf uses its own index for a job when
    that index has those months, otherwise its nearest published parent's.
    """
    def first(chain, months):
        for c in chain:
            code = codes.get(norm(c.name))
            sid = f"CUUR0000{code}"
            if code and sid in idx and all(m in idx[sid] for m in months):
                return c, code
        raise RuntimeError(f"no index for {chain[0].name} over {months}")

    out = []
    for n in nodes:
        if n.kids:
            continue
        chain, cur = [], n
        while cur is not None:
            chain.append(cur)
            cur = nodes[cur.parent] if cur.parent is not None else None
        row = {"name": n.name}
        for job, months in jobs.items():
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


def rolled(leaves, idx, month, dec_prior, job="wcode"):
    """BLS relative importance at `month`: the December weight times the item's
    price relative, divided by the all-items relative. Not rescaled to 100."""
    A = idx["CUUR0000SA0"]
    all_rel = A[month] / A[dec_prior]
    return {l["name"]: l["ri_dec_prior"] * idx[f"CUUR0000{l[job]}"][month]
            / idx[f"CUUR0000{l[job]}"][dec_prior] / all_rel for l in leaves}, all_rel


def compute_month(inp: Inputs, t: str, extra_jobs=None):
    """Item contributions for target month t. Returns a dict with the items,
    the published rates and the sums; raises if a needed month is missing."""
    T, B, DEC_PRIOR, DEC_NEW = months_for(t)
    idx, codes = inp.idx, inp.codes
    SA0, CORE = idx["CUUR0000SA0"], idx["CUUR0000SA0L1E"]
    for m in (T, B, DEC_PRIOR, DEC_NEW):
        if m not in SA0 or m not in CORE:
            raise KeyError(f"{t}: all items or core index missing for {m}")

    nodes_p, nodes_n = inp.tree(int(DEC_PRIOR[:4])), inp.tree(int(DEC_NEW[:4]))
    byname = {n.name: n for n in nodes_p}
    jobs = {"code": (B, T),                # the 12-month change
            "wcode": (DEC_PRIOR, B),       # rolling the weight to the base month
            "scode": (B, DEC_NEW)}         # splitting the year at the January reweight
    jobs.update(extra_jobs or {})
    leaves = leaves_with_index(nodes_p, codes, idx, jobs)
    ri_new = {n.name: n.weight for n in nodes_n if not n.kids}
    ri_old = {l["name"]: l["ri_dec_prior"] for l in leaves}
    if set(ri_old) != set(ri_new):
        raise RuntimeError(f"{t}: leaf sets differ between weight years")
    zero = {n for n in ri_old if ri_old[n] == 0 and ri_new[n] == 0}

    w_b, all_rel_b = rolled(leaves, idx, B, DEC_PRIOR)
    all_yoy, core_yoy = pct(SA0[T], SA0[B]), pct(CORE[T], CORE[B])
    rel_all, rel_core = SA0[DEC_NEW] / SA0[B], CORE[DEC_NEW] / CORE[B]
    is_core = {l["name"]: l["group"] == "Core" for l in leaves}
    # Core's share of all items at the base month, rolled the way BLS rolls any aggregate.
    core_w = (sum(ri_old[n] for n, c in is_core.items() if c)
              * (CORE[B] / CORE[DEC_PRIOR]) / all_rel_b)
    core_ri_new = sum(ri_new[n] for n, c in is_core.items() if c)

    def terms(W, R, split, full, core):
        """The two pieces of the chained contribution, headline and (if core) core."""
        h = (W * (split - 1), rel_all * R * (full / split - 1))
        c = ((100 * W / core_w) * (split - 1),
             rel_core * (100 * R / core_ri_new) * (full / split - 1)) if core else None
        return h, c

    items = {}
    for l in leaves:
        n = l["name"]
        s, ss = idx[f"CUUR0000{l['code']}"], idx[f"CUUR0000{l['scode']}"]
        full, split = s[T] / s[B], ss[DEC_NEW] / ss[B]
        h, c = terms(w_b[n], ri_new[n], split, full, is_core[n])
        items[n] = dict(l, w=w_b[n], h=list(h), cc=list(c) if c else None,
                        yoy=pct(s[T], s[B]),
                        yoy_source="published" if l["own_index"] else "parent",
                        contrib_simple=w_b[n] * pct(s[T], s[B]) / 100)

    def leaves_under(node):
        return [node.name] if not node.kids else [
            x for k in node.kids for x in leaves_under(nodes_p[k])]

    # Fill unpublished leaves from their parent, deepest parent first. The
    # parent's own rolled weight and index give its contribution, one term at a
    # time; what the parent's other leaves do not explain goes to the filled
    # leaves, shared by their December weights.
    # A fill parent must have its own index at all four months. When the
    # nearest published parent lacks one (household operations is published
    # only some months), the fill moves up to the next parent that has them.
    need = (DEC_PRIOR, B, DEC_NEW, T)

    def has_all(name):
        code = codes.get(norm(name))
        s = idx.get(f"CUUR0000{code}", {}) if code else {}
        return all(m in s for m in need)

    fill_parent = {}
    for n, it in items.items():
        if it["own_index"]:
            continue
        P = byname[it["index_from"]]
        while not has_all(P.name):
            P = nodes_p[P.parent]
        fill_parent[n] = P.name

    # Core terms are the headline terms times fixed factors (the weight is
    # rescaled to core and the second term uses the core index), so the core
    # residual follows from the headline residual whenever the filled leaves
    # are all core. Their parent can hold non-core leaves, as Private
    # transportation does (motor fuel), because those leaves have their own
    # index and are subtracted out.
    k1, k2 = 100 / core_w, (rel_core / rel_all) * 100 / core_ri_new
    fills = []
    for P in sorted(set(fill_parent.values()), key=lambda p: (-byname[p].level, byname[p].idx)):
        under = leaves_under(byname[P])
        fill = [n for n in under if fill_parent.get(n) == P]
        rest = [n for n in under if n not in fill]
        s = idx[f"CUUR0000{codes[norm(P)]}"]
        core = is_core[fill[0]]
        if any(is_core[n] != core for n in fill):
            raise RuntimeError(f"{t}: filled leaves under {P} mix core and non-core")
        WP = sum(ri_old[n] for n in under) * (s[B] / s[DEC_PRIOR]) / all_rel_b
        RP = sum(ri_new[n] for n in under)
        hP, _ = terms(WP, RP, s[DEC_NEW] / s[B], s[T] / s[B], False)
        Wf = WP - sum(items[n]["w"] for n in rest)
        h_res = [hP[k] - sum(items[n]["h"][k] for n in rest) for k in (0, 1)]
        c_res = [h_res[0] * k1, h_res[1] * k2] if core else None
        f_old = sum(ri_old[n] for n in fill)
        f_new = sum(ri_new[n] for n in fill)
        for n in fill:
            a = ri_old[n] / f_old if f_old else 1 / len(fill)
            b = ri_new[n] / f_new if f_new else 1 / len(fill)
            it = items[n]
            it["w"] = Wf * a
            it["h"] = [h_res[0] * a, h_res[1] * b]
            if core:
                it["cc"] = [c_res[0] * a, c_res[1] * b]
            tot = sum(it["h"])
            it["yoy"] = (tot / it["w"] * 100) if it["w"] > 0.001 else None
            it["yoy_source"] = "filled from " + P
            it["index_from"] = P
        fills.append({"parent": P, "items": fill, "weight": round(Wf, 4),
                      "contrib": round(sum(h_res), 5),
                      "implied_yoy": round(sum(h_res) / Wf * 100, 3) if Wf > 0.001 else None})

    for n, it in items.items():
        if n in zero:                      # no weight in either year: nothing to show
            it["h"], it["yoy"] = [0.0, 0.0], None
            if it["cc"]:
                it["cc"] = [0.0, 0.0]
        it["zero_weight"] = n in zero
        it["ri_sep_prior"] = round(it["w"], 4)      # weight at the base month
        it["ri_dec_new"] = ri_new[n]
        it["contrib"] = sum(it["h"])
        it["contrib_core"] = sum(it["cc"]) if it["cc"] else None
        it["core_weight"] = 100 * it["w"] / core_w if is_core[n] else None
        it["_h"], it["_c"] = it.pop("h"), it.pop("cc")
        it.pop("w")

    rows = list(items.values())
    return {
        "month": T, "base": B, "dec_prior": DEC_PRIOR, "dec_new": DEC_NEW,
        "published": {"headline": all_yoy, "core": core_yoy},
        "sum": {"headline": sum(i["contrib"] for i in rows),
                "core": sum(i["contrib_core"] for i in rows if i["contrib_core"] is not None)},
        "sum_simple": sum(i["contrib_simple"] for i in rows),
        "core_w": core_w, "zero": sorted(zero), "fills": fills,
        "leaves": leaves, "items": rows,
    }
