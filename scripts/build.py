"""Build dist/index.html from src/template.html and data/processed/contrib.json.

Injects the payload at the single /*DATA*/{} placeholder, parse-checks the
script, then runs the page in headless Chrome, full and embedded, failing on
any JavaScript error. The payload is keyed by month so more months can be added
later and animated; only the release month is filled now.
"""
from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import tempfile
from datetime import date

from common import DIST, PROCESSED, ROOT, SHORT

SRC = ROOT / "src"
AXIS = {"min": -2, "max": 10, "step": 2, "target": 2}   # fixed so later months fit without rescaling
STEPS = [0.5, 1, 2, 3, 5, 10]                            # color bins on |12-month change|, fixed


def label(ym):
    y, m = map(int, ym.split("-"))
    return date(y, m, 1).strftime("%B %Y")


def encode(months, order, title, notes=None):
    """Compact payload: the item list once, then per month one row per item,
    [12-month change, headline contribution, core contribution, headline
    weight, core weight, index source (-1 = own index, else parents[k])].
    Items with no weight, or too little weight for a 12-month change (under
    0.001% of the CPI), are left out of the drawing; they never add up to more
    than 0.0002 points in a month."""
    names = []
    for t in order:
        for i in months[t]["items"]:
            if i["name"] not in names:
                names.append(i["name"])
    parents, out = [], {}
    for t in order:
        M = months[t]
        by = {i["name"]: i for i in M["items"]}
        rows, sums = [], {"headline": 0.0, "core": 0.0}
        for n in names:
            i = by.get(n)
            if i is None or i["zero_weight"] or i["yoy"] is None:
                rows.append(None)
                continue
            frm = -1
            if not i["own_index"]:
                if i["index_from"] not in parents:
                    parents.append(i["index_from"])
                frm = parents.index(i["index_from"])
            cc = None if i["contrib_core"] is None else round(i["contrib_core"], 5)
            rows.append([round(i["yoy"], 3), round(i["contrib"], 5), cc,
                         round(i["ri_sep_prior"], 4),
                         None if i["core_weight"] is None else round(i["core_weight"], 4), frm])
            sums["headline"] += i["contrib"]
            sums["core"] += i["contrib_core"] or 0.0
        for k in sums:
            gap = abs(sums[k] - M["published"][k])
            assert gap < 0.005, f"{t} {k}: drawn items sum {sums[k]} vs published {M['published'][k]}"
        out[t] = {"label": label(t), "baseLabel": label(M["base"]), "note": (notes or {}).get(t, ""),
                  "pub": [round(M["published"]["headline"], 4), round(M["published"]["core"], 4)],
                  "sum": [round(sums["headline"], 4), round(sums["core"], 4)], "r": rows}
    item_meta = []
    for n in names:
        i = next(x for t in order for x in months[t]["items"] if x["name"] == n)
        item_meta.append([SHORT.get(n, n), n, i["group"], i["major"]])
    return {
        "title": title,
        "source": ("Source: BLS Consumer Price Index (CPI-U, U.S. city average, not seasonally adjusted) and "
                   "relative importance tables. Contributions computed by Data 4 The People."),
        "axis": AXIS, "color": {"steps": STEPS},
        "highlight": ["Health insurance", "Prescription drugs"],
        "items": item_meta, "parents": parents, "order": order, "months": out,
    }


def write_page(payload, filename, description):
    data = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    (PROCESSED / filename.replace(".html", "_data.json")).write_text(data)

    t = (SRC / "template.html").read_text()
    assert t.count("/*DATA*/{}") == 1
    t = t.replace("/*DATA*/{}", data)

    jsc = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc"
    if os.path.exists(jsc):
        i = t.index("<script>") + 8
        js = t[i:t.index("</script>", i)]
        with tempfile.TemporaryDirectory() as tmp:
            open(f"{tmp}/page.js", "w").write(js)
            open(f"{tmp}/chk.js", "w").write(
                'try{ new Function(read("%s/page.js")); print("ok") }catch(e){ print("PARSE ERROR: "+e) }' % tmp)
            out = subprocess.run([jsc, f"{tmp}/chk.js"], capture_output=True, text=True).stdout.strip()
        assert out == "ok", out

    head_end = t.index("</style>") + len("</style>")
    full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<meta name="description" content="{description}">\n'
            + t[:head_end].replace('<meta charset="utf-8">\n', "") + "\n</head>\n<body>\n" + t[head_end:] + "\n</body>\n</html>\n")
    DIST.mkdir(exist_ok=True)
    (DIST / filename).write_text(full)

    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(chrome):
        with tempfile.TemporaryDirectory() as tmp:
            probe = full.replace("<script>", '<script>window.onerror=(m,u,l,c)=>{document.body.setAttribute("data-err",m+" @"+l+":"+c)};', 1)
            open(f"{tmp}/probe.html", "w").write(probe)
            for mode in ("", "#embed=1"):
                dom = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--window-size=1100,800",
                                      "--virtual-time-budget=3000", "--dump-dom", f"file://{tmp}/probe.html{mode}"],
                                     capture_output=True, text=True, timeout=120).stdout
                err = re.search(r'data-err="([^"]*)"', dom)
                assert dom and not err, f"page JavaScript error{' (embed)' if mode else ''}: {err.group(1) if err else 'no output'}"
                assert 'data-ready="1"' in dom, "page script did not finish"
                n = dom.count('class="tile"')
                last = payload["months"][payload["order"][-1]]["r"]
                assert n >= sum(1 for r in last if r) - 5, f"only {n} tiles drawn"
        print(f"dist/{filename}: runs in Chrome, full and embedded, without errors")


def main():
    d = json.loads((PROCESSED / "contrib.json").read_text())
    month = d["month"]
    write_page(encode({month: d}, [month], f"What pushed prices up in {label(month)}"), "index.html",
               f"Which items pushed U.S. consumer prices up and down in the 12 months to {label(month)}, "
               "drawn as a hot air balloon. Built by Data 4 The People.")
    m = json.loads((PROCESSED / "monthly.json").read_text())
    assert m["order"][-1] == month
    a, b = label(m["order"][0]), label(m["order"][-1])
    notes = {}
    for row in csv.DictReader(open(PROCESSED / "monthly_summary.csv")):
        if row["note"] and row["status"] != "missing":
            notes[row["month"]] = row["note"]
    payload = encode(m["months"], m["order"], "The CPI Hot Air Balloon", notes)
    payload["missing"] = m["missing"]
    write_page(payload, "over-time.html",
               f"Which items pushed U.S. consumer prices up and down in every month from {a} to {b}, "
               "drawn as a hot air balloon that rises and falls with inflation. Built by Data 4 The People.")


if __name__ == "__main__":
    main()
