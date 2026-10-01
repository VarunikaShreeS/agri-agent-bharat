"""Tool 3b: Distance + transport cost model (deterministic)."""
from math import radians, sin, cos, asin, sqrt

ROAD_FACTOR = 1.3            # ASSUMPTION - not sourced (ratio)
FREIGHT_PER_QTL_KM = 2.0     # ASSUMPTION - not sourced (INR/qtl-km)
LOADING_PER_QTL = 15.0       # ASSUMPTION - not sourced (INR/qtl)
COMMISSION_PCT = 2.0         # ASSUMPTION - not sourced (%)
SPOILAGE_PCT_PER_100KM = {"tomato": 2.5, "onion": 0.5}  # ASSUMPTION - not sourced (%/100km)
MAX_PRICE_DATE_GAP_DAYS = 1  # ASSUMPTION - not sourced (days)


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = radians(lat1), radians(lat2)
    dphi, dl = p2 - p1, radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * 6371.0 * asin(sqrt(a))


def road_km(lat1, lon1, lat2, lon2) -> float:
    return round(haversine_km(lat1, lon1, lat2, lon2) * ROAD_FACTOR, 1)
