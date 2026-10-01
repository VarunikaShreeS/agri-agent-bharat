"""Probes real agricultural mandi data sources with latency, status, and sample payload schemas."""
import os
import sys
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

TIMEOUT = 8.0

def probe(name: str, url: str, headers: dict = None, params: dict = None, retry_cold_start: bool = True) -> dict:
    print(f"\n==========================================")
    print(f"Probing: {name}")
    print(f"URL: {url} | Params: {params}")
    headers = headers or {"Accept": "application/json", "User-Agent": "KrishiChain-Probe/1.0"}
    
    start = time.time()
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        latency = round(time.time() - start, 3)
        print(f"Status: {resp.status_code} | Latency: {latency}s")
        if resp.status_code == 200:
            try:
                data = resp.json()
                print(f"Response Type: {type(data).__name__}")
                if isinstance(data, dict):
                    print(f"Top-level keys: {list(data.keys())}")
                    # If success wrapper
                    items = data.get("data") or data.get("records") or data.get("results") or data
                    if isinstance(items, list) and len(items) > 0:
                        print(f"Item count: {len(items)}")
                        print(f"Sample item keys: {list(items[0].keys()) if isinstance(items[0], dict) else type(items[0])}")
                        print(f"Sample item preview: {json.dumps(items[0], default=str)[:300]}")
                    else:
                        print(f"Dict preview: {json.dumps(data, default=str)[:300]}")
                elif isinstance(data, list):
                    print(f"Item count: {len(data)}")
                    if len(data) > 0:
                        print(f"Sample item keys: {list(data[0].keys()) if isinstance(data[0], dict) else type(data[0])}")
                        print(f"Sample item preview: {json.dumps(data[0], default=str)[:300]}")
                return {"reachable": True, "status": resp.status_code, "latency_s": latency, "data": data}
            except Exception as e:
                print(f"Non-JSON response (length {len(resp.text)}): {resp.text[:200]}")
                return {"reachable": True, "status": resp.status_code, "latency_s": latency, "text_preview": resp.text[:200]}
        else:
            print(f"Non-200 Status: {resp.status_code} - {resp.text[:200]}")
            if retry_cold_start and resp.status_code in (502, 503, 504, 429):
                print("Retrying after 10s for cold start...")
                time.sleep(10)
                return probe(name, url, headers, params, retry_cold_start=False)
            return {"reachable": False, "status": resp.status_code, "latency_s": latency, "error": resp.text[:200]}
    except requests.exceptions.Timeout:
        latency = round(time.time() - start, 3)
        print(f"Timeout after {latency}s")
        if retry_cold_start:
            print("Retrying once with 15s timeout for cold start...")
            try:
                start2 = time.time()
                resp = requests.get(url, headers=headers, params=params, timeout=15.0)
                latency2 = round(time.time() - start2, 3)
                print(f"Retry Status: {resp.status_code} | Latency: {latency2}s")
                if resp.status_code == 200:
                    data = resp.json()
                    return {"reachable": True, "status": resp.status_code, "latency_s": latency2, "data": data}
            except Exception as e2:
                print(f"Retry failed: {e2}")
        return {"reachable": False, "status": "TIMEOUT", "latency_s": latency}
    except Exception as e:
        latency = round(time.time() - start, 3)
        print(f"Error ({type(e).__name__}): {e}")
        return {"reachable": False, "status": "ERROR", "error": str(e), "latency_s": latency}


def main():
    results = {}
    
    # a) GET /v1/states
    results["mandi_api_states"] = probe(
        "Mandi Price API - States",
        "https://mandi-api.onrender.com/v1/states"
    )
    
    # b) GET /v1/prices (Tomato and Onion for Maharashtra)
    results["mandi_api_tomato"] = probe(
        "Mandi Price API - Maharashtra Tomato",
        "https://mandi-api.onrender.com/v1/prices",
        params={"state": "Maharashtra", "commodity": "Tomato"}
    )
    results["mandi_api_onion"] = probe(
        "Mandi Price API - Maharashtra Onion",
        "https://mandi-api.onrender.com/v1/prices",
        params={"state": "Maharashtra", "commodity": "Onion"}
    )
    
    # c) GET /v1/prices/history
    results["mandi_api_history"] = probe(
        "Mandi Price API - History (Maharashtra Tomato)",
        "https://mandi-api.onrender.com/v1/prices/history",
        params={"state": "Maharashtra", "commodity": "Tomato"}
    )

    # d) data.gov.in Agmarknet resource
    data_gov_key = os.getenv("DATA_GOV_API_KEY")
    if data_gov_key:
        print("\nDATA_GOV_API_KEY is present, probing data.gov.in...")
        # Common agmarknet resource ID on data.gov.in: 9ef84268-d588-465a-a308-a864a43d0070
        results["data_gov_in"] = probe(
            "data.gov.in Agmarknet API",
            "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070",
            params={"api-key": data_gov_key, "format": "json", "limit": 5, "filters[state]": "Maharashtra"}
        )
    else:
        print("\n[d] DATA_GOV_API_KEY not set in .env; skipping data.gov.in probe.")
        results["data_gov_in"] = {"reachable": False, "status": "KEY_NOT_CONFIGURED", "note": "DATA_GOV_API_KEY is empty"}

    # e) CEDA Agmarknet
    results["ceda_probe"] = probe(
        "CEDA Agmarknet API / Website",
        "https://agmarknet.ceda.ashoka.edu.in",
        retry_cold_start=False
    )

    print("\n==========================================")
    print("PROBE SUMMARY TABLE:")
    print("==========================================")
    for k, v in results.items():
        status = v.get("status")
        lat = v.get("latency_s", "-")
        reachable = v.get("reachable", False)
        print(f"- {k:22}: Reachable={reachable:<5} | Status={str(status):<8} | Latency={lat}s")


if __name__ == "__main__":
    main()
