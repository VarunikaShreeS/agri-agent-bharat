"""Tool 3c: combines mandi rows + logistics + optimizer into a ranked sell plan."""
import datetime
from typing import Dict, Any, List
from . import mandi, logistics, optimizer

MAX_RADIUS_KM = 350  # realistic for smallholder transport


def classify(uplift_pct: float, uplift_inr: float, uplift_inr_freight_x125: float) -> str:
    """Pure classification of sell recommendation based on net financial returns and logistics risk."""
    if uplift_inr <= 0:
        return "sell_local"
    if uplift_pct >= 5.0 and uplift_inr_freight_x125 > 0:
        return "travel"
    return "marginal"


def _parse_date(d_val: Any) -> datetime.date:
    try:
        return datetime.date.fromisoformat(str(d_val).strip()[:10])
    except Exception:
        return datetime.date(1970, 1, 1)


def compute_sensitivity(crop: str, qty: float, best: Dict[str, Any], local: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compute exact sensitivity runs through optimizer.net_realization across freight and price shifts."""
    orig_freight = logistics.FREIGHT_PER_QTL_KM
    sens = []

    # 1. freight_x0.75
    try:
        logistics.FREIGHT_PER_QTL_KM = orig_freight * 0.75
        b_net = optimizer.net_realization(crop, best["price_per_quintal"], qty, best["distance_km"])["net"]
        l_net = optimizer.net_realization(crop, local["price_per_quintal"], qty, local["distance_km"])["net"]
        sens.append({"label": "freight_x0.75", "uplift_inr": b_net - l_net})
    finally:
        logistics.FREIGHT_PER_QTL_KM = orig_freight

    # 2. freight_x1.0 (base)
    sens.append({"label": "freight_x1.0", "uplift_inr": best["net"] - local["net"]})

    # 3. freight_x1.25
    try:
        logistics.FREIGHT_PER_QTL_KM = orig_freight * 1.25
        b_net = optimizer.net_realization(crop, best["price_per_quintal"], qty, best["distance_km"])["net"]
        l_net = optimizer.net_realization(crop, local["price_per_quintal"], qty, local["distance_km"])["net"]
        sens.append({"label": "freight_x1.25", "uplift_inr": b_net - l_net})
    finally:
        logistics.FREIGHT_PER_QTL_KM = orig_freight

    # 4. remote_price_x0.9
    b_net = optimizer.net_realization(crop, best["price_per_quintal"] * 0.9, qty, best["distance_km"])["net"]
    l_net = optimizer.net_realization(crop, local["price_per_quintal"], qty, local["distance_km"])["net"]
    sens.append({"label": "remote_price_x0.9", "uplift_inr": b_net - l_net})

    # 5. grade_discount_5pct_both
    b_net = optimizer.net_realization(crop, best["price_per_quintal"] * 0.95, qty, best["distance_km"])["net"]
    l_net = optimizer.net_realization(crop, local["price_per_quintal"] * 0.95, qty, local["distance_km"])["net"]
    sens.append({"label": "grade_discount_5pct_both", "uplift_inr": b_net - l_net})

    # 6. grade_discount_10pct_both
    b_net = optimizer.net_realization(crop, best["price_per_quintal"] * 0.90, qty, best["distance_km"])["net"]
    l_net = optimizer.net_realization(crop, local["price_per_quintal"] * 0.90, qty, local["distance_km"])["net"]
    sens.append({"label": "grade_discount_10pct_both", "uplift_inr": b_net - l_net})

    return sens


def build_sell_plan(crop: str, quantity_quintals: float, home_district: str, severity: float) -> dict:
    home = mandi.resolve_home(home_district)
    if not home:
        return {"ok": False, "error": f"Could not locate '{home_district}'.", "known_districts": mandi.known_districts()}
    rows = mandi.get_market_rows(crop, home_state=home.get("state", "Maharashtra"))
    if not rows:
        return {"ok": False, "error": f"No price data for crop '{crop}'.", "provider_log": mandi.get_last_provider_log()}

    all_options = []
    for r in rows:
        km = 0.0 if (r["district"].lower() == home["district"].lower() and r["state"].lower() == home["state"].lower()) else \
            logistics.road_km(home["lat"], home["lon"], r["lat"], r["lon"])
        if km > MAX_RADIUS_KM:
            continue
        money = optimizer.net_realization(crop, r["modal_price"], quantity_quintals, km)
        p_date = r.get("price_date") or r.get("as_of")
        tier = r.get("data_tier") or r.get("source", "")
        span_days = r.get("trend_span_days")
        all_options.append({
            "market": r["market"], "district": r["district"], "state": r["state"],
            "distance_km": km, "price_per_quintal": r["modal_price"],
            "trend_pct": optimizer.trend_pct(r.get("history_7d"), span_days),
            "trend_span_days": span_days,
            "source": tier, "data_tier": tier,
            "as_of": p_date, "price_date": p_date,
            "is_synthetic": r.get("is_synthetic", False),
            **money
        })

    if not all_options:
        return {"ok": False, "error": "No markets within range.", "provider_log": mandi.get_last_provider_log()}

    # Local baseline is the closest market
    local = min(all_options, key=lambda o: o["distance_km"])
    local_p_date = local["price_date"]
    local_dt = _parse_date(local_p_date) if local_p_date else None

    # Exclude stale markets
    valid_options = []
    excluded_stale = []
    for opt in all_options:
        opt_p_date = opt["price_date"]
        # Case A: Both dates are None (synthetic data) -> skip date comparison, keep valid
        if local_p_date is None and opt_p_date is None:
            valid_options.append(opt)
        # Case B: Incomparable dates (one is None and the other is real)
        elif (local_p_date is None and opt_p_date is not None) or (local_p_date is not None and opt_p_date is None):
            excluded_stale.append({"market": opt["market"], "price_date": opt_p_date, "reason": "no_comparable_date"})
        # Case C: Real dates -> check date gap
        else:
            opt_dt = _parse_date(opt_p_date)
            gap_days = abs((opt_dt - local_dt).days)
            if gap_days <= logistics.MAX_PRICE_DATE_GAP_DAYS:
                valid_options.append(opt)
            else:
                excluded_stale.append({"market": opt["market"], "price_date": opt_p_date, "reason": f"gap_{gap_days}d_exceeds_max"})

    # Rank options
    valid_options.sort(key=lambda o: o["net"], reverse=True)
    remote_options = [o for o in valid_options if o["distance_km"] > 0]
    best = max(remote_options, key=lambda o: o["net"]) if remote_options else local

    uplift = best["net"] - local["net"]
    uplift_pct = round(uplift / local["net"] * 100, 2) if local["net"] else 0.0

    # Sensitivity calculation
    sensitivity = compute_sensitivity(crop, quantity_quintals, best, local)
    freight_x125_uplift = next((s["uplift_inr"] for s in sensitivity if s["label"] == "freight_x1.25"), uplift)

    recommendation = classify(uplift_pct, uplift, freight_x125_uplift)

    # Break even freight per qtl-km
    if best["distance_km"] > 0 and (quantity_quintals * best["distance_km"]) > 0:
        break_even_freight = logistics.FREIGHT_PER_QTL_KM + (uplift / (quantity_quintals * best["distance_km"]))
    else:
        break_even_freight = None

    is_synthetic = any(opt.get("is_synthetic", False) for opt in valid_options)

    return {
        "ok": True,
        "crop": crop,
        "quantity_quintals": quantity_quintals,
        "home": f'{home["district"]}, {home["state"]}',
        "best": best,
        "local_baseline": local,
        "top_options": valid_options[:3],
        "excluded_stale": excluded_stale,
        "uplift_inr_vs_local": uplift,
        "uplift_pct_vs_local": uplift_pct,
        "recommendation": recommendation,
        "break_even_freight_inr_per_qtl_km": break_even_freight,
        "sensitivity": sensitivity,
        "timing": optimizer.timing_advice(severity, best.get("trend_pct"), best.get("trend_span_days")),
        "is_synthetic": is_synthetic,
        "assumptions": {
            "severity": severity,
            "severity_in_net": False,
            "road_factor": logistics.ROAD_FACTOR,
            "freight_rs_per_qtl_km": logistics.FREIGHT_PER_QTL_KM,
            "commission_pct": logistics.COMMISSION_PCT,
            "loading_rs_per_qtl": logistics.LOADING_PER_QTL,
            "spoilage_pct_per_100km": logistics.SPOILAGE_PCT_PER_100KM.get(crop.lower(), 1.0)
        },
        "data_source": best["source"],
        "data_tier": best["data_tier"],
        "data_as_of": best["as_of"],
        "price_date": best["price_date"],
        "provider_log": mandi.get_last_provider_log()
    }
