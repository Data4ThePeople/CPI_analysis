"""Download every raw input: weight files, item codes, release tables, indexes.

Indexes are fetched for every node in the expenditure tree that has a code, so a
leaf without its own index can fall back to its nearest published parent.
"""
from __future__ import annotations

import csv
import json

from common import (RAW, RI_URL, CU_ITEM_URL, HIST_START, TARGET,
                    bls_series, download)

AGGREGATES = {"SA0": "All items", "SA0L1E": "All items less food and energy"}
RELEASES = {"2025-09": "https://www.bls.gov/news.release/archives/cpi_10242025.htm",
            "2025-11": "https://www.bls.gov/news.release/archives/cpi_12182025.htm"}


def norm(name: str) -> str:
    return " ".join(name.replace(", and ", " and ").split()).lower()


def item_codes() -> dict:
    """{normalized name: code} from cu.item; duplicate names are a hard failure."""
    out = {}
    with open(RAW / "cu.item") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            k = norm(r["item_name"])
            if k in out:
                raise RuntimeError(f"duplicate item name in cu.item: {k}")
            out[k] = r["item_code"].strip()
    return out


def main():
    for y in (2024, 2025):
        download(RI_URL.format(year=y), RAW / f"relative_importance_{y}.xlsx")
    download(CU_ITEM_URL, RAW / "cu.item")
    for k, url in RELEASES.items():
        download(url, RAW / f"release_{k}.htm")

    from weights import build_tree
    codes = item_codes()
    names = {n.name for y in (2024, 2025) for n in build_tree(y)}
    wanted = {c: n for n in names if (c := codes.get(norm(n)))}
    ids = [f"CUUR0000{c}" for c in list(AGGREGATES) + sorted(wanted)]
    data = bls_series(ids, HIST_START, TARGET[0])
    out = {sid: {f"{y}-{m:02d}": v for (y, m), v in sorted(vals.items())}
           for sid, vals in data.items()}
    (RAW / "indexes.json").write_text(json.dumps(out, indent=0))
    empty = [s for s, v in out.items() if not v]
    print(f"{len(ids)} series requested, {len(out)} returned, {len(empty)} empty")
    if empty:
        print("empty:", empty)


if __name__ == "__main__":
    main()
