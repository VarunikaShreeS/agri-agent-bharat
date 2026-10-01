"""Deterministic net-profit calculation. The LLM never computes money."""
from . import logistics as L


def net_realization(crop: str, price_qtl: float, qty_qtl: float, km: float) -> dict:
    gross = price_qtl * qty_qtl
    freight = L.FREIGHT_PER_QTL_KM * km * qty_qtl
    commission = gross * L.COMMISSION_PCT / 100
    loading = L.LOADING_PER_QTL * qty_qtl
    spoil_rate = L.SPOILAGE_PCT_PER_100KM.get(crop.lower(), 1.0)
    spoilage = gross * (spoil_rate / 100) * (km / 100)
    net = gross - freight - commission - loading - spoilage
    r = lambda x: round(x, 0)
    return {"gross": r(gross), "freight": r(freight), "commission": r(commission),
            "loading": r(loading), "spoilage_loss": r(spoilage), "net": r(net)}


def trend_pct(history: list) -> float:
    if len(history) < 2 or history[0] == 0:
        return 0.0
    return round((history[-1] - history[0]) / history[0] * 100, 1)


def timing_advice(severity: float, best_trend_pct: float) -> dict:
    if severity >= 0.6:
        return {"action": "sell_now", "reason": f"Infection severity {severity:.0%} is high; harvest marketable produce now rather than wait."}
    if severity < 0.3 and best_trend_pct >= 5:
        return {"action": "treat_and_hold_short", "reason": f"Low severity and prices up {best_trend_pct}% over 7 days; treat now and sell within 3-5 days if produce stays sound."}
    return {"action": "sell_at_best_market", "reason": "Moderate/unclear signals; sell at the best net-return market and treat remaining crop."}
