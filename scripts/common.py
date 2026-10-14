"""Paths, BLS download convention and the API fetcher shared by every script."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, os.path.expanduser("~/.claude/d4tp-process"))
from d4tp_env import load_env, get_key  # noqa: E402

load_env()

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
SLUG = "what-is-driving-cpi"
CHARTS = ROOT / "posts" / SLUG / "images"
DIST = ROOT / "dist"

# download.bls.gov rejects bare agents; BLS asks callers to identify themselves.
CONTACT = os.environ.get("D4TP_CONTACT_EMAIL", "")
USER_AGENT = f"Mozilla/5.0 CPI_analysis/1.0 ({CONTACT})"

RI_URL = "https://www.bls.gov/cpi/tables/relative-importance/{year}.xlsx"
CU_ITEM_URL = "https://download.bls.gov/pub/time.series/cu/cu.item"
API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# Plain-language names for long BLS item names, shared by the charts and the page.
SHORT = {
    "Owners' equivalent rent of primary residence": "Owners' equivalent rent",
    "Other lodging away from home including hotels and motels": "Hotels and motels",
    "Telephone hardware, calculators, and other consumer information items": "Phones and other info devices",
    "Club membership for shopping clubs, fraternal, or other organizations, or participant sports fees": "Club memberships and sports fees",
    "Unsampled owners' equivalent rent of secondary residences": "Owners' rent, second homes",
    "Full service meals and snacks": "Full-service restaurant meals",
    "Limited service meals and snacks": "Fast food and takeout",
    "Motor vehicle maintenance and servicing": "Car maintenance",
    "Other pork including roasts, steaks, and ribs": "Other pork",
    "Moving, storage, freight expense": "Moving and storage",
    "Utility (piped) gas service": "Natural gas service",
    "Gasoline (all types)": "Gasoline",
}

# The release month this analysis is about, and the history window.
TARGET = (2026, 9)
HIST_START = 2014


def download(url: str, dest: Path, force: bool = False) -> Path:
    if dest.exists() and not force:
        return dest
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    body = urllib.request.urlopen(req, timeout=120).read()
    if dest.suffix == ".xlsx" and not body.startswith(b"PK"):
        raise RuntimeError(f"{url} did not return an xlsx (got an HTML page?)")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(body)
    return dest


def bls_series(ids, start_year: int, end_year: int) -> dict:
    """{series_id: {(year, month): value}} for monthly NSA data, 50 ids per call.

    Missing values ("-", e.g. October 2025 during the funding lapse) are skipped.
    The API allows 20 years per request, which covers HIST_START..TARGET.
    """
    ids = list(dict.fromkeys(ids))
    out = {}
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        body = json.dumps({"seriesid": chunk, "startyear": str(start_year),
                           "endyear": str(end_year),
                           "registrationkey": get_key("BLS_API_KEY")}).encode()
        req = urllib.request.Request(API_URL, data=body, headers={
            "Content-type": "application/json", "User-Agent": USER_AGENT})
        r = json.load(urllib.request.urlopen(req, timeout=120))
        if r.get("status") != "REQUEST_SUCCEEDED":
            raise RuntimeError(f"BLS API: {r.get('status')} {r.get('message')}")
        for s in r["Results"]["series"]:
            vals = {}
            for x in s["data"]:
                if not x["period"].startswith("M") or x["period"] == "M13":
                    continue
                try:
                    v = float(x["value"])
                except ValueError:
                    continue
                key = (int(x["year"]), int(x["period"][1:]))
                if key in vals:
                    raise RuntimeError(f"duplicate {s['seriesID']} {key}")
                vals[key] = v
            out[s["seriesID"]] = vals
        time.sleep(0.5)
    return out
