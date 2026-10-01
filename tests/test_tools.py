"""Offline tests: python tests/test_tools.py  (no API key / network needed)"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from tools import agronomy_kb, planner, optimizer, mandi
from agent.tracing import Trace


def test_kb():
    assert agronomy_kb.lookup("Tomato", "early_blight")["found"]
    bad = agronomy_kb.lookup("tomato", "nonsense")
    assert not bad["found"] and "valid_diseases" in bad


def test_optimizer_math():
    r = optimizer.net_realization("tomato", 2000, 10, 100)
    assert r["gross"] == 20000 and r["freight"] == 2000 and r["commission"] == 400 and r["loading"] == 150
    assert r["net"] == r["gross"] - r["freight"] - r["commission"] - r["loading"] - r["spoilage_loss"]


def test_plan_nashik_tomato():
    p = planner.build_sell_plan("Tomato", 20, "Nashik, Maharashtra", 0.4)
    assert p["ok"] and p["best"]["net"] >= p["local_baseline"]["net"]
    assert all(o["distance_km"] <= planner.MAX_RADIUS_KM for o in p["top_options"])
    assert p["data_source"] in ("live_mandi_api", "live_agmarknet", "frozen_real", "seeded_snapshot")


def test_plan_recovers_on_unknown_district():
    p = planner.build_sell_plan("Tomato", 10, "Atlantis", 0.2)
    assert not p["ok"] and p["known_districts"]


def test_timing_rules():
    assert optimizer.timing_advice(0.8, 10)["action"] == "sell_now"
    assert optimizer.timing_advice(0.1, 8)["action"] == "treat_and_hold_short"


def test_trace_captures_errors():
    t = Trace()
    def boom(x: int) -> dict:
        raise ValueError("bad")
    out = t.wrap(boom)(1)
    assert "error" in out and t.steps[0]["status"] == "error"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("PASS", name)
