"""Read a BLS relative importance XLSX into a validated item tree.

Adapted from CPI/src/cpi_diesel/parse.py (stdlib only: zipfile + ElementTree).
The expenditure tree runs from the "All items" root under "Expenditure category"
to the "Special aggregate indexes" header; the special aggregates overlap the
tree and are dropped so nothing is double counted.
"""
from __future__ import annotations

import zipfile
import xml.etree.ElementTree as ET

from common import RAW

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
SHEET = "xl/worksheets/sheet1.xml"
START_SECTION = "Expenditure category"
ROOT_ITEM = "All items"
STOP_SECTION = "Special aggregate indexes"
TOLERANCE = 0.05

# Rows BLS published at the wrong indent level, found by asserting that every
# parent equals the sum of its children. Keyed by weight-file year.
# name -> corrected level. Each fix carries the whole subtree with it.
INDENT_FIXES = {
    2024: {"Alcoholic beverages": 2,
           "Information technology, hardware and services": 4},
    2025: {"Alcoholic beverages": 2,
           "Information technology, hardware and services": 4},
}


class Node:
    __slots__ = ("idx", "level", "name", "weight", "parent", "kids")

    def __init__(self, idx, level, name, weight):
        self.idx, self.level, self.name, self.weight = idx, level, name, weight
        self.parent = None
        self.kids = []

    def __repr__(self):
        return f"<L{self.level} {self.name!r} {self.weight}>"


def _cells(path):
    with zipfile.ZipFile(path) as z:
        strings = ["".join(t.text or "" for t in si.iter(NS + "t"))
                   for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(NS + "si")]
        sheet = ET.fromstring(z.read(SHEET))
    rows = []
    for row in sheet.iter(NS + "row"):
        rec = {}
        for cell in row.iter(NS + "c"):
            col = "".join(ch for ch in (cell.get("r") or "") if ch.isalpha())
            v = cell.find(NS + "v")
            if v is None or v.text is None:
                continue
            rec[col] = strings[int(v.text)] if cell.get("t") == "s" else v.text
        rows.append(rec)
    return rows


def _expenditure_rows(rows):
    start = stop = None
    for i, rec in enumerate(rows):
        name = (rec.get("B") or "").strip()
        if name == START_SECTION and start is None:
            for j in range(i + 1, len(rows)):
                if (rows[j].get("B") or "").strip() == ROOT_ITEM:
                    start = j + 1
                    break
        elif name == STOP_SECTION and start is not None:
            stop = i
            break
    if start is None or stop is None:
        raise ValueError("expenditure section not found; table layout changed")
    return [r for r in rows[start:stop] if "A" in r and "B" in r and "C" in r]


def build_tree(year):
    raw = _expenditure_rows(_cells(RAW / f"relative_importance_{year}.xlsx"))
    rows = [[int(float(r["A"])), r["B"].strip(), float(r["C"])] for r in raw]
    fixes = INDENT_FIXES.get(year, {})
    for i, row in enumerate(rows):
        target = fixes.get(row[1])
        if target is None or row[0] == target:
            continue
        delta, original = target - row[0], row[0]
        row[0] = target
        for f in rows[i + 1:]:
            if f[0] <= original:
                break
            f[0] += delta
    nodes, stack = [], []
    for idx, (level, name, w) in enumerate(rows):
        while stack and nodes[stack[-1]].level >= level:
            stack.pop()
        n = Node(idx, level, name, w)
        if stack:
            n.parent = stack[-1]
            nodes[stack[-1]].kids.append(idx)
        nodes.append(n)
        stack.append(idx)
    broken = []
    for n in nodes:
        if n.kids:
            s = sum(nodes[k].weight for k in n.kids)
            if abs(s - n.weight) > TOLERANCE:
                broken.append((n.name, n.weight, round(s, 3)))
    if broken:
        raise ValueError(f"{year}: parent/child mismatches: {broken}")
    leaves = sum(n.weight for n in nodes if not n.kids)
    if abs(leaves - 100) > TOLERANCE:
        raise ValueError(f"{year}: leaves sum to {leaves}")
    return nodes


def ancestors(nodes, node):
    out = []
    while node.parent is not None:
        node = nodes[node.parent]
        out.append(node.name)
    return out


if __name__ == "__main__":
    for y in (2024, 2025):
        try:
            t = build_tree(y)
            print(y, len(t), "nodes,", sum(1 for n in t if not n.kids), "leaves")
        except ValueError as e:
            print(e)
