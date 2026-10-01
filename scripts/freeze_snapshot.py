"""Freezes current real mandi data from Mandi Price API into data/mandi_snapshot_frozen.json."""
import os
import sys
import json
import time
import pathlib
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
            data = resp.json()
            return data.get("data", [])
        print(f"Error {resp.status_code}: {resp.text[:100]}")
        return []
    except Exception as e:
        print(f"Fetch failed: {e}")
        return []

def main():
    coords = get_coords_map()
    all_markets = {}
    fetch_date = time.strftime("%Y-%m-%d")
    latest_arrival = "2026-09-24"

    crops = ["Tomato", "Onion"]
    states = ["Maharashtra"]

    for st in states:
        st_coords = coords.get(st, {})
        for crop in crops:
            records = fetch_prices(st, crop)
            print(f"  Got {len(records)} records for {st} {crop}")
            for r in records:
                dist = (r.get("district") or "").strip()
                market_name = (r.get("market") or "").strip()
                modal = r.get("modal_price")
                arrival = r.get("arrival_date", fetch_date)
                if arrival > latest_arrival:
                    latest_arrival = arrival
                
                if not dist or not market_name or modal is None:
                    continue

                # Match coordinates by district
                c = st_coords.get(dist)
                if not c:
                    # Try fuzzy matching
                    for d_key, d_val in st_coords.items():
                        if d_key.lower() in dist.lower() or dist.lower() in d_key.lower():
                            c = d_val
                            break

                if not c:
                    # Skip unplaceable rows rather than guessing
                    continue

                key = (st, dist, market_name)
                if key not in all_markets:
                    all_markets[key] = {
                        "market": market_name,
                        "district": dist,
                        "state": st,
                        "lat": c["lat"],
                        "lon": c["lon"],
                        "prices": {},
                        "arrival_dates": {}
                    }
                all_markets[key]["prices"][crop] = [int(modal)]
                all_markets[key]["arrival_dates"][crop] = arrival

    # Also add seed Tamil Nadu markets if needed so TN coverage is maintained in frozen file
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
        "as_of": latest_arrival,
        "frozen_on": fetch_date,
        "disclaimer": "Real Agmarknet wholesale data frozen from Mandi Price API (https://mandi-api.onrender.com). Approximate district centroids used for distances.",
        "market_count": len(market_list),
        "markets": market_list
    }

    OUTPUT_PATH.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSuccessfully froze {len(market_list)} markets to {OUTPUT_PATH} (as of {latest_arrival})")

if __name__ == "__main__":
    main()
