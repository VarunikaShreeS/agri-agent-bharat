"""Tool 3a: Mandi prices provider chain.
Chain: Mandi Price API (live) -> data.gov.in (live, optional) -> frozen real snapshot -> seed snapshot.
All providers normalize to the schema:
{market, district, state, lat, lon, modal_price, history_7d, source, as_of}
Sources: "live_mandi_api", "live_agmarknet", "frozen_real", "seeded_snapshot".
"""
import os
import json
import time
import pathlib
from typing import Optional, List, Dict, Any
import requests

DATA_DIR = pathlib.Path(__file__).parent.parent / "data"

# Load district coordinates
_COORDS_FILE = DATA_DIR / "district_coords.json"
_COORDS: Dict[str, Dict[str, Dict[str, float]]] = {}
if _COORDS_FILE.exists():
    _COORDS = json.loads(_COORDS_FILE.read_text(encoding="utf-8"))

_LAST_PROVIDER_LOG: List[Dict[str, Any]] = []


def get_district_coord(state: str, district: str) -> Optional[Dict[str, float]]:
    """Look up approximate centroid for a district within a state or across states."""
    st_map = _COORDS.get(state, {})
    if district in st_map:
        return st_map[district]
    # Case-insensitive / partial match in state
    for d_name, coord in st_map.items():
        if d_name.lower() == district.lower() or d_name.lower() in district.lower() or district.lower() in d_name.lower():
            return coord
    # Search all states if state didn't match
    for st_name, districts in _COORDS.items():
        if not isinstance(districts, dict):
            continue
        for d_name, coord in districts.items():
            if d_name.lower() == district.lower() or d_name.lower() in district.lower():
                return coord
    return None


class MandiApiAdapter:
    """Adapter for Mandi Price API (https://mandi-api.onrender.com/v1)."""
    NAME = "live_mandi_api"
    URL = "https://mandi-api.onrender.com/v1/prices"

    @classmethod
    def fetch_rows(cls, crop: str, state: str = "Maharashtra", timeout: float = 8.0) -> List[Dict[str, Any]]:
        # Attempt request with 1 retry
        for attempt in range(2):
            try:
                resp = requests.get(cls.URL, params={"state": state, "commodity": crop.title()}, timeout=timeout)
                if resp.status_code == 200:
                    data = resp.json().get("data", [])
                    rows = []
                    for r in data:
                        dist = (r.get("district") or "").strip()
                        m_name = (r.get("market") or "").strip()
                        modal = r.get("modal_price")
                        arrival = r.get("arrival_date", time.strftime("%Y-%m-%d"))
                        if not dist or not m_name or modal is None:
                            continue
                        coord = get_district_coord(state, dist)
                        if not coord:
                            # Skip unplaceable rows rather than guessing
                            continue
                        rows.append({
                            "market": m_name,
                            "district": dist,
                            "state": state,
                            "lat": coord["lat"],
                            "lon": coord["lon"],
                            "modal_price": float(modal),
                            "history_7d": None,  # Mandi API prices endpoint does not provide individual market history
                            "source": cls.NAME,
                            "as_of": arrival
                        })
                    if rows:
                        return rows
                elif resp.status_code in (502, 503, 504, 429) and attempt == 0:
                    time.sleep(1.0)
                    continue
            except Exception:
                if attempt == 0:
                    time.sleep(1.0)
                    continue
                raise
        raise RuntimeError(f"Mandi API failed or returned empty records for {crop} in {state}")


class DataGovAdapter:
    """Adapter for data.gov.in Agmarknet API (requires DATA_GOV_API_KEY)."""
    NAME = "live_agmarknet"
    URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

    @classmethod
    def fetch_rows(cls, crop: str, timeout: float = 8.0) -> List[Dict[str, Any]]:
        api_key = os.getenv("DATA_GOV_API_KEY")
        if not api_key:
            raise ValueError("DATA_GOV_API_KEY not configured")
        
        for attempt in range(2):
            try:
                resp = requests.get(cls.URL, params={"api-key": api_key, "format": "json", "limit": 200,
                                                     "filters[commodity]": crop.title()}, timeout=timeout)
                if resp.status_code == 200:
                    records = resp.json().get("records", [])
                    rows = []
                    for r in records:
                        st = r.get("state", "Maharashtra")
                        dist = r.get("district", "")
                        m_name = r.get("market", "")
                        modal = r.get("modal_price")
                        arrival = r.get("arrival_date", time.strftime("%Y-%m-%d"))
                        if not dist or not m_name or not modal:
                            continue
                        coord = get_district_coord(st, dist)
                        if not coord:
                            continue
                        rows.append({
                            "market": m_name,
                            "district": dist,
                            "state": st,
                            "lat": coord["lat"],
                            "lon": coord["lon"],
                            "modal_price": float(modal),
                            "history_7d": None,
                            "source": cls.NAME,
                            "as_of": arrival
                        })
                    if rows:
                        return rows
                elif attempt == 0:
                    time.sleep(1.0)
                    continue
            except Exception:
                if attempt == 0:
                    time.sleep(1.0)
                    continue
                raise
        raise RuntimeError(f"data.gov.in returned no records for {crop}")


class FrozenRealAdapter:
    """Adapter for frozen real snapshot data (data/mandi_snapshot_frozen.json)."""
    NAME = "frozen_real"
    FILE = DATA_DIR / "mandi_snapshot_frozen.json"

    @classmethod
    def fetch_rows(cls, crop: str) -> List[Dict[str, Any]]:
        if not cls.FILE.exists():
            raise FileNotFoundError(f"{cls.FILE} not found")
        data = json.loads(cls.FILE.read_text(encoding="utf-8"))
        as_of = data.get("as_of", "2026-09-24")
        rows = []
        for m in data.get("markets", []):
            prices = m.get("prices", {})
            hist = prices.get(crop.title()) or prices.get(crop)
            if hist:
                modal = hist[-1] if isinstance(hist, list) else hist
                history_7d = hist if (isinstance(hist, list) and len(hist) > 1) else None
                rows.append({
                    "market": m["market"],
                    "district": m["district"],
                    "state": m["state"],
                    "lat": m["lat"],
                    "lon": m["lon"],
                    "modal_price": float(modal),
                    "history_7d": history_7d,
                    "source": cls.NAME,
                    "as_of": m.get("arrival_dates", {}).get(crop.title(), as_of)
                })
        if not rows:
            raise ValueError(f"No frozen real data for crop {crop}")
        return rows


class SeededSnapshotAdapter:
    """Adapter for illustrative seeded snapshot (data/mandi_snapshot_seed.json or data/mandi_snapshot.json)."""
    NAME = "seeded_snapshot"

    @classmethod
    def fetch_rows(cls, crop: str) -> List[Dict[str, Any]]:
        seed_file = DATA_DIR / "mandi_snapshot_seed.json"
        if not seed_file.exists():
            seed_file = DATA_DIR / "mandi_snapshot.json"
        if not seed_file.exists():
            raise FileNotFoundError("No seed snapshot file found")
        data = json.loads(seed_file.read_text(encoding="utf-8"))
        as_of = data.get("as_of", "2026-10-01")
        rows = []
        for m in data.get("markets", []):
            prices = m.get("prices", {})
            hist = prices.get(crop.title()) or prices.get(crop)
            if hist:
                modal = hist[-1] if isinstance(hist, list) else hist
                history_7d = hist if isinstance(hist, list) else [modal]
                rows.append({
                    "market": m["market"],
                    "district": m["district"],
                    "state": m["state"],
                    "lat": m["lat"],
                    "lon": m["lon"],
                    "modal_price": float(modal),
                    "history_7d": history_7d,
                    "source": cls.NAME,
                    "as_of": as_of
                })
        if not rows:
            raise ValueError(f"No seed data for crop {crop}")
        return rows


def get_market_rows(crop: str, home_state: str = "Maharashtra") -> List[Dict[str, Any]]:
    """Provider chain execution:
    1. live_mandi_api (Mandi Price API)
    2. live_agmarknet (data.gov.in)
    3. frozen_real (data/mandi_snapshot_frozen.json)
    4. seeded_snapshot (data/mandi_snapshot_seed.json)
    """
    global _LAST_PROVIDER_LOG
    _LAST_PROVIDER_LOG = []
    
    # Provider 1: Live Mandi Price API
    try:
        rows = MandiApiAdapter.fetch_rows(crop, state=home_state)
        _LAST_PROVIDER_LOG.append({"provider": MandiApiAdapter.NAME, "status": "success", "count": len(rows)})
        return rows
    except Exception as e:
        _LAST_PROVIDER_LOG.append({"provider": MandiApiAdapter.NAME, "status": "failed", "error": str(e)})

    # Provider 2: Live data.gov.in (if configured)
    if os.getenv("DATA_GOV_API_KEY"):
        try:
            rows = DataGovAdapter.fetch_rows(crop)
            _LAST_PROVIDER_LOG.append({"provider": DataGovAdapter.NAME, "status": "success", "count": len(rows)})
            return rows
        except Exception as e:
            _LAST_PROVIDER_LOG.append({"provider": DataGovAdapter.NAME, "status": "failed", "error": str(e)})
    else:
        _LAST_PROVIDER_LOG.append({"provider": DataGovAdapter.NAME, "status": "skipped", "reason": "No DATA_GOV_API_KEY"})

    # Provider 3: Frozen Real Snapshot
    try:
        rows = FrozenRealAdapter.fetch_rows(crop)
        _LAST_PROVIDER_LOG.append({"provider": FrozenRealAdapter.NAME, "status": "success", "count": len(rows)})
        return rows
    except Exception as e:
        _LAST_PROVIDER_LOG.append({"provider": FrozenRealAdapter.NAME, "status": "failed", "error": str(e)})

    # Provider 4: Seeded Snapshot Fallback
    try:
        rows = SeededSnapshotAdapter.fetch_rows(crop)
        _LAST_PROVIDER_LOG.append({"provider": SeededSnapshotAdapter.NAME, "status": "success", "count": len(rows)})
        return rows
    except Exception as e:
        _LAST_PROVIDER_LOG.append({"provider": SeededSnapshotAdapter.NAME, "status": "failed", "error": str(e)})
        return []


def get_last_provider_log() -> List[Dict[str, Any]]:
    return list(_LAST_PROVIDER_LOG)


def resolve_home(text: str) -> Optional[Dict[str, Any]]:
    """Match a free-text 'District, State' to a known district coordinate or market row."""
    t = text.lower()
    
    # Check district coords first
    for st_name, dists in _COORDS.items():
        if isinstance(dists, dict):
            for d_name, coord in dists.items():
                if d_name.lower() in t:
                    return {
                        "district": d_name,
                        "state": st_name,
                        "lat": coord["lat"],
                        "lon": coord["lon"]
                    }
    
    # Check frozen markets
    frozen_file = DATA_DIR / "mandi_snapshot_frozen.json"
    if frozen_file.exists():
        data = json.loads(frozen_file.read_text(encoding="utf-8"))
        for m in data.get("markets", []):
            if m["district"].lower() in t or m["market"].lower().split()[0] in t:
                return {"district": m["district"], "state": m["state"], "lat": m["lat"], "lon": m["lon"]}

    # Check seed markets
    seed_file = DATA_DIR / "mandi_snapshot_seed.json"
    if seed_file.exists():
        data = json.loads(seed_file.read_text(encoding="utf-8"))
        for m in data.get("markets", []):
            if m["district"].lower() in t or m["market"].lower().split()[0] in t:
                return {"district": m["district"], "state": m["state"], "lat": m["lat"], "lon": m["lon"]}

    return None


def known_districts() -> List[str]:
    """List all recognized districts across coordinates and snapshot files."""
    districts = set()
    for st_name, dists in _COORDS.items():
        if isinstance(dists, dict):
            districts.update(dists.keys())
    
    seed_file = DATA_DIR / "mandi_snapshot_seed.json"
    if seed_file.exists():
        data = json.loads(seed_file.read_text(encoding="utf-8"))
        for m in data.get("markets", []):
            districts.add(m["district"])

    return sorted(districts)
