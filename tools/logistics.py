"""Tool 3b: Distance + transport cost model (deterministic)."""
from math import radians, sin, cos, asin, sqrt

ROAD_FACTOR = 1.3            # straight-line -> approx road distance
FREIGHT_PER_QTL_KM = 2.0     # Rs per quintal per km (configurable assumption)
LOADING_PER_QTL = 15.0       # Rs per quintal loading/unloading
COMMISSION_PCT = 2.0         # arhtiya/commission at mandi
SPOILAGE_PCT_PER_100KM = {"tomato": 2.5, "onion": 0.5}  # perishability


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = radians(lat1), radians(lat2)
    dphi, dl = p2 - p1, radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * 6371.0 * asin(sqrt(a))


def road_km(lat1, lon1, lat2, lon2) -> float:
    return round(haversine_km(lat1, lon1, lat2, lon2) * ROAD_FACTOR, 1)
