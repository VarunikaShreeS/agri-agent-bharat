"""Tool 3a: Mandi prices. Live data.gov.in (Agmarknet) if DATA_GOV_API_KEY is set, else seeded snapshot.
Every row carries `source` and `as_of` so the UI can show Live vs Cached honestly."""
import json
import os
from pathlib import Path

_SNAP = json.loads((Path(__file__).parent.parent / "data" / "mandi_snapshot.json").read_text(encoding="utf-8"))
# Agmarknet "current daily price" resource on data.gov.in (verify ID on the portal if the call fails)
_LIVE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"


def _snapshot_rows(crop: str) -> list:
    rows = []
    for m in _SNAP["markets"]:
        hist = m["prices"].get(crop.title())
        if hist:
            rows.append({"market": m["market"], "district": m["district"], "state": m["state"],
                         "lat": m["lat"], "lon": m["lon"], "modal_price": hist[-1], "history_7d": hist,
                         "source": "seeded_snapshot", "as_of": _SNAP["as_of"]})
    return rows


def _live_overlay(crop: str, rows: list) -> list:
    """Overlay live modal prices on snapshot rows (keeps coords/history). Falls back silently on any failure."""
    key = os.getenv("DATA_GOV_API_KEY")
    if not key:
        return rows
    try:
        import requests
        resp = requests.get(_LIVE_URL, params={"api-key": key, "format": "json", "limit": 500,
                                               "filters[commodity]": crop.title()}, timeout=8)
        resp.raise_for_status()
        live = {(r["state"].lower(), r["district"].lower()): r for r in resp.json().get("records", [])}
        for row in rows:
            rec = live.get((row["state"].lower(), row["district"].lower()))
            if rec and rec.get("modal_price"):
                row["modal_price"] = float(rec["modal_price"])
                row["source"], row["as_of"] = "live_agmarknet", rec.get("arrival_date", "today")
        return rows
    except Exception:
        return rows


def get_market_rows(crop: str) -> list:
    return _live_overlay(crop, _snapshot_rows(crop))


def resolve_home(text: str):
    """Match a free-text 'District, State' to a known market row (by district name)."""
    t = text.lower()
    for m in _SNAP["markets"]:
        if m["district"].lower() in t or m["market"].lower().split()[0] in t:
            return m
    return None


def known_districts() -> list:
    return sorted({m["district"] for m in _SNAP["markets"]})
