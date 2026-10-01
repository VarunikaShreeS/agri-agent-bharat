"""Tool 3c: combines mandi rows + logistics + optimizer into a ranked sell plan."""
from . import mandi, logistics, optimizer

MAX_RADIUS_KM = 350  # realistic for smallholder transport


def build_sell_plan(crop: str, quantity_quintals: float, home_district: str, severity: float) -> dict:
    home = mandi.resolve_home(home_district)
    if not home:
        return {"ok": False, "error": f"Could not locate '{home_district}'.", "known_districts": mandi.known_districts()}
    rows = mandi.get_market_rows(crop)
    if not rows:
        return {"ok": False, "error": f"No price data for crop '{crop}'."}
    options = []
    for r in rows:
        km = 0.0 if (r["district"] == home["district"] and r["state"] == home["state"]) else \
            logistics.road_km(home["lat"], home["lon"], r["lat"], r["lon"])
        if km > MAX_RADIUS_KM:
            continue
        money = optimizer.net_realization(crop, r["modal_price"], quantity_quintals, km)
        options.append({"market": r["market"], "district": r["district"], "state": r["state"],
                        "distance_km": km, "price_per_quintal": r["modal_price"],
                        "trend_7d_pct": optimizer.trend_pct(r["history_7d"]),
                        "source": r["source"], "as_of": r["as_of"], **money})
    if not options:
        return {"ok": False, "error": "No markets within range."}
    options.sort(key=lambda o: o["net"], reverse=True)
    local = min(options, key=lambda o: o["distance_km"])
    best = options[0]
    uplift = best["net"] - local["net"]
    return {"ok": True, "crop": crop, "quantity_quintals": quantity_quintals,
            "home": f'{home["district"]}, {home["state"]}',
            "best": best, "local_baseline": local, "top_options": options[:3],
            "uplift_inr_vs_local": uplift,
            "uplift_pct_vs_local": round(uplift / local["net"] * 100, 1) if local["net"] else 0.0,
            "timing": optimizer.timing_advice(severity, best["trend_7d_pct"]),
            "assumptions": {"road_factor": logistics.ROAD_FACTOR, "freight_rs_per_qtl_km": logistics.FREIGHT_PER_QTL_KM,
                            "commission_pct": logistics.COMMISSION_PCT},
            "data_source": best["source"], "data_as_of": best["as_of"]}
