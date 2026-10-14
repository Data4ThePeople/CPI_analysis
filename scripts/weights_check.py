"""Check our weight roll-forward against every December BLS printed, 2015-2025.

Rolling December Y-1's relative importance forward to December Y (item
relative over all-items relative) should reproduce what BLS printed for
December Y on the same weight basis:
- in years without a weight update (2016, 2018, 2020), the regular December
  table;
- in update years, the "old weights" table, which BLS prints for December on
  the outgoing basis: PDFs in the 2010-2019 archive (2015, 2017, 2019) and web
  pages (2021-2025).
Leaves with their own index for both Decembers are compared. Writes
data/processed/weights_check.json.
"""
from __future__ import annotations

import html
import json
import re
import statistics

from chain import Inputs, leaves_with_index, rolled
from common import RAW, PROCESSED, download
from fetch import norm
from weights import build_tree, TXT_DIR

OLD_URL = "https://www.bls.gov/cpi/tables/relative-importance/old-weights-{year}.htm"
NO_UPDATE = {2016, 2018, 2020}


def pairs_htm(year):
    path = download(OLD_URL.format(year=year), RAW / "ri_archive" / f"old-weights-{year}.htm")
    t = path.read_text(errors="ignore")
    return [(html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip(), float(m.group(2)))
            for m in re.finditer(r"<th[^>]*>(.*?)</th>\s*<td[^>]*>(?:\s*<[^>]+>)*\s*([0-9.]+)",
                                 t, re.S)]


def pairs_pdf(year):
    from pypdf import PdfReader
    txt = "\n".join(p.extract_text() for p in
                    PdfReader(str(TXT_DIR / f"old-weights-{year}.pdf")).pages)
    out = []
    for line in txt.splitlines():
        m = re.match(r"^\s*(.*?)[\s.]*?([0-9]*\.[0-9]{3})\s+([0-9]*\.[0-9]{3})\s*$", line)
        if m:
            out.append((m.group(1).strip(" ."), float(m.group(2))))
    return out


def main():
    inp = Inputs()
    out = {}
    for y in range(2015, 2026):
        canon = inp.tree(y - 1)
        if y in NO_UPDATE:
            printed = {n.name: n.weight for n in inp.tree(y) if not n.kids}
            source = f"{y} December table (no weight update)"
        else:
            pr = pairs_htm(y) if y >= 2021 else pairs_pdf(y)
            # Old-weight tables use either year's item names; map both to canonical.
            namemap = {}
            for yy in (y - 1, y):
                namemap.update({norm(a.name): b.name for a, b in zip(build_tree(yy), inp.tree(yy))})
            printed = {}
            for n, v in pr:
                c = namemap.get(norm(n))
                if c and c not in printed:
                    printed[c] = v
            source = f"{y} December, old-weights table"
        dp, dn = f"{y-1}-12", f"{y}-12"
        lv = leaves_with_index(canon, inp.codes, inp.idx,
                               {"code": (dp, dn), "wcode": (dp, dn), "scode": (dp, dn)})
        w, _ = rolled(lv, inp.idx, dn, dp)
        d = sorted(((abs(w[l["name"]] - printed[l["name"]]), l["name"]) for l in lv
                    if l["own_index"] and l["name"] in printed), reverse=True)
        out[y] = {"source": source, "matched": len(d),
                  "mean_abs_diff": round(statistics.mean(x for x, _ in d), 5),
                  "max_abs_diff": round(d[0][0], 4), "worst": d[0][1]}
        print(y, out[y])
    (PROCESSED / "weights_check.json").write_text(json.dumps(out, indent=1))
    bad = [y for y, r in out.items() if r["max_abs_diff"] > 0.0015 or r["matched"] < 140]
    if bad:
        raise SystemExit(f"weight roll-forward check failed for {bad}")


if __name__ == "__main__":
    main()
