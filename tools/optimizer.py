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


def trend_pct(history: list, trend_span_days: int = None) -> float:
    if not history or not isinstance(history, (list, tuple)) or len(history) < 2 or history[0] == 0:
        return None
    if trend_span_days is not None and trend_span_days < 2:
        return None
    return round((history[-1] - history[0]) / history[0] * 100, 1)


def timing_advice(severity: float, best_trend_pct: float, trend_span_days: int = None) -> dict:
    if severity >= 0.6:
        return {"action": "sell_now", "reason": f"Infection severity {severity:.0%} is high; harvest marketable produce now rather than wait."}
    if best_trend_pct is not None and (trend_span_days is None or trend_span_days >= 2) and severity < 0.3 and best_trend_pct >= 5:
        span_str = f"{trend_span_days}" if trend_span_days is not None else "multi-day"
        return {"action": "treat_and_hold_short", "reason": f"Low severity and prices up {best_trend_pct}% over {span_str} days; treat now and sell within 3-5 days if produce stays sound."}
    if best_trend_pct is None or (trend_span_days is not None and trend_span_days < 2):
        return {"action": "sell_at_best_market", "reason": "No multi-day price trend history available; sell at the best net-return market and treat remaining crop."}
    return {"action": "sell_at_best_market", "reason": "Moderate/unclear signals; sell at the best net-return market and treat remaining crop."}
