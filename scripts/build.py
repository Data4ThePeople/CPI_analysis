"""Build dist/index.html from src/template.html and data/processed/contrib.json.

Injects the payload at the single /*DATA*/{} placeholder, parse-checks the
script, then runs the page in headless Chrome, full and embedded, failing on
any JavaScript error. The payload is keyed by month so more months can be added
later and animated; only the release month is filled now.
"""
from __future__ import annotations

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


def view_items(items, core):
    out = []
    for i in items:
        c = i["contrib_core"] if core else i["contrib"]
        if c is None:
            continue
        out.append({"n": SHORT.get(i["name"], i["name"]), "f": i["name"], "g": i["group"],
                    "m": i["major"], "y": round(i["yoy"], 3), "c": round(c, 5),
                    "w": round(i["core_weight"] if core else i["ri_sep_prior"], 4),
                    "fill": not i["own_index"], "from": i["index_from"]})
    return out


def main():
    d = json.loads((PROCESSED / "contrib.json").read_text())
    month = d["month"]
    views = {}
    for key, core in (("headline", False), ("core", True)):
        items = view_items(d["items"], core)
        names = [i["f"] for i in items]
        assert len(names) == len(set(names)), "duplicate items"
        views[key] = {"published": d["published"][key], "sum": round(sum(i["c"] for i in items), 4),
                      "items": items}
        gap = abs(views[key]["sum"] - views[key]["published"])
        assert gap < 0.01, f"{key}: items sum {views[key]['sum']} vs published {views[key]['published']}"
    payload = {
        "title": f"What pushed prices up in {label(month)}",
        "source": ("Source: BLS Consumer Price Index (CPI-U, U.S. city average, not seasonally adjusted) and "
                   "relative importance tables. Contributions computed by Data 4 The People."),
        "axis": AXIS, "color": {"steps": STEPS},
        "highlight": ["Health insurance", "Prescription drugs"],
        "order": [month],
        "months": {month: {"label": label(month), "baseLabel": label(d["base"]), "views": views}},
    }
    data = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    (PROCESSED / "page_data.json").write_text(data)

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
            f'<meta name="description" content="Which items pushed U.S. consumer prices up and down in the 12 months to '
            f'{label(month)}, drawn as a hot air balloon. Built by Data 4 The People.">\n'
            + t[:head_end].replace('<meta charset="utf-8">\n', "") + "\n</head>\n<body>\n" + t[head_end:] + "\n</body>\n</html>\n")
    DIST.mkdir(exist_ok=True)
    (DIST / "index.html").write_text(full)

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
                assert n >= len(views["headline"]["items"]) - 5, f"only {n} tiles drawn"
        print("page and embed run in Chrome without errors")
    print("dist/index.html:", {k: (v["published"], v["sum"], len(v["items"])) for k, v in views.items()})


if __name__ == "__main__":
    main()
