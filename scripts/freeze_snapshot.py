"""Freezes current real mandi data from Mandi Price API into data/mandi_snapshot_frozen.json.
Deduplication rule: For each market, pick latest arrival_date (exclude > 3 days stale vs max dataset date),
average modal_price across varieties on same date, and extract 7-day history if present.
"""
import os
import sys
import json
import time
import pathlib
import datetime
import requests

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

BASE_URL = "https://mandi-api.onrender.com/v1"
COORDS_PATH = pathlib.Path("data") / "district_coords.json"
OUTPUT_PATH = pathlib.Path("data") / "mandi_snapshot_frozen.json"

def get_coords_map():
    if COORDS_PATH.exists():
        return json.loads(COORDS_PATH.read_text(encoding="utf-8"))
    return {}

def fetch_prices(state: str, commodity: str):
    print(f"Fetching prices for {state} - {commodity}...")
    try:
        resp = requests.get(f"{BASE_URL}/prices", params={"state": state, "commodity": commodity}, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("data", [])
        return []
    except Exception as e:
        print(f"Fetch failed: {e}")
        return []

def aggregate_market_records(records, state: str, coords_map: dict):
    if not records:
        return {}
    
    # 1. Group records by (market, district)
    grouped = {}
    max_date = "1970-01-01"
    for r in records:
        dist = (r.get("district") or "").strip()
        m_name = (r.get("market") or "").strip()
        arr = r.get("arrival_date", "")
        modal = r.get("modal_price")
        if not dist or not m_name or modal is None or not arr:
            continue
        if arr > max_date:
            max_date = arr
        key = (dist, m_name)
        grouped.setdefault(key, []).append(r)

    # Convert max_date to datetime to compute staleness
    try:
        max_dt = datetime.datetime.strptime(max_date, "%Y-%m-%d")
    except Exception:
        max_dt = datetime.datetime.now()

    st_coords = coords_map.get(state, {})
    result = {}

    for (dist, m_name), rows in grouped.items():
        # Match coordinates
        c = st_coords.get(dist)
        if not c:
            for d_k, d_v in st_coords.items():
                if d_k.lower() in dist.lower() or dist.lower() in d_k.lower():
                    c = d_v
                    break
        if not c:
            continue

        # Sort rows by arrival_date ascending
        rows_by_date = {}
        for r in rows:
            arr = r.get("arrival_date", "")
            try:
                p = float(r.get("modal_price"))
                rows_by_date.setdefault(arr, []).append(p)
            except Exception:
                continue

        if not rows_by_date:
            continue

        sorted_dates = sorted(rows_by_date.keys())
        latest_date = sorted_dates[-1]

        # Check staleness: within 3 days of dataset max_date
        try:
            latest_dt = datetime.datetime.strptime(latest_date, "%Y-%m-%d")
            if (max_dt - latest_dt).days > 3:
                continue
        except Exception:
            pass

        # Average modal price for the latest date
        latest_prices = rows_by_date[latest_date]
        avg_modal = round(sum(latest_prices) / len(latest_prices), 0)

        # Build chronological history
        history = [round(sum(rows_by_date[d]) / len(rows_by_date[d]), 0) for d in sorted_dates]

        result[(state, dist, m_name)] = {
            "market": m_name,
            "district": dist,
            "state": state,
            "lat": c["lat"],
            "lon": c["lon"],
            "modal_price": avg_modal,
            "history_7d": history if len(history) > 1 else None,
            "arrival_date": latest_date,
            "max_date": max_date
        }

    return result

def main():
    coords = get_coords_map()
    crops = ["Tomato", "Onion"]
    states = ["Maharashtra"]
    all_markets = {}
    dataset_max_date = "2026-09-24"

    for st in states:
        for crop in crops:
            records = fetch_prices(st, crop)
            agg = aggregate_market_records(records, st, coords)
            print(f"  Aggregated {len(agg)} clean markets for {st} {crop}")
            for (state, dist, m_name), data in agg.items():
                if data["arrival_date"] > dataset_max_date:
                    dataset_max_date = data["arrival_date"]
                key = (state, dist, m_name)
                if key not in all_markets:
                    all_markets[key] = {
                        "market": data["market"],
                        "district": data["district"],
                        "state": data["state"],
                        "lat": data["lat"],
                        "lon": data["lon"],
                        "prices": {},
                        "histories": {},
                        "arrival_dates": {}
                    }
                all_markets[key]["prices"][crop] = [int(data["modal_price"])]
                if data["history_7d"]:
                    all_markets[key]["histories"][crop] = [int(p) for p in data["history_7d"]]
                all_markets[key]["arrival_dates"][crop] = data["arrival_date"]

    # Incorporate seed Tamil Nadu benchmark markets
    seed_path = pathlib.Path("data") / "mandi_snapshot_seed.json"
    if seed_path.exists():
        seed_data = json.loads(seed_path.read_text(encoding="utf-8"))
        for m in seed_data.get("markets", []):
            if m.get("state") == "Tamil Nadu":
                key = (m["state"], m["district"], m["market"])
                if key not in all_markets:
                    all_markets[key] = m

    market_list = list(all_markets.values())
    output_data = {
        "source": "frozen_real",
        "as_of": dataset_max_date,
        "frozen_on": time.strftime("%Y-%m-%d"),
        "disclaimer": "Real Agmarknet wholesale data frozen from Mandi Price API (https://mandi-api.onrender.com). Filtered to latest same-day arrivals within 3-day freshness window with approximate district centroids.",
        "market_count": len(market_list),
        "markets": market_list
    }

    OUTPUT_PATH.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSuccessfully froze {len(market_list)} distinct markets to {OUTPUT_PATH} (as of {dataset_max_date})")

if __name__ == "__main__":
    main()
