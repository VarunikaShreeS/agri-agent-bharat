"""Golden test suite for sell plan consistency, sensitivity, classification, and honest date handling."""
import sys
import os
import pathlib
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from tools import planner, logistics, optimizer, mandi


class TestSellPlanGolden(unittest.TestCase):
    def setUp(self):
        # Patch MandiApiAdapter to ensure offline deterministic tests against frozen_real snapshot
        self._patcher = patch.object(mandi.MandiApiAdapter, "fetch_rows", side_effect=RuntimeError("Offline test"))
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_g1_golden_tomato_nashik(self):
        """G1: Tomato, 20q, Nashik, severity 0.2 produces exact verified baseline figures."""
        with patch.object(mandi.MandiApiAdapter, "fetch_rows", side_effect=RuntimeError("Offline test")):
            plan = planner.build_sell_plan("Tomato", 20.0, "Nashik, Maharashtra", 0.2)
            self.assertTrue(plan["ok"])
            self.assertEqual(plan["local_baseline"]["net"], 40860.0)
            self.assertEqual(plan["best"]["net"], 41254.0)
            self.assertEqual(plan["uplift_inr_vs_local"], 394.0)
            self.assertEqual(round(plan["uplift_pct_vs_local"], 2), 0.96)
            self.assertEqual(plan["recommendation"], "marginal")

    def test_g2_freight_patch_sell_local(self):
        """G2: Higher freight rate flips recommendation to sell_local with negative uplift."""
        with patch.object(mandi.MandiApiAdapter, "fetch_rows", side_effect=RuntimeError("Offline test")):
            with patch.object(logistics, "FREIGHT_PER_QTL_KM", 2.5):
                plan = planner.build_sell_plan("Tomato", 20.0, "Nashik, Maharashtra", 0.2)
                self.assertTrue(plan["ok"])
                self.assertTrue(plan["uplift_inr_vs_local"] < 0)
                self.assertEqual(plan["uplift_inr_vs_local"], -1903.0)
                self.assertEqual(plan["recommendation"], "sell_local")

    def test_g3_break_even_freight(self):
        """G3: Break-even freight per qtl-km matches formula 2.0 + 394 / (20 * 229.7)."""
        with patch.object(mandi.MandiApiAdapter, "fetch_rows", side_effect=RuntimeError("Offline test")):
            plan = planner.build_sell_plan("Tomato", 20.0, "Nashik, Maharashtra", 0.2)
            self.assertTrue(plan["ok"])
            be = plan["break_even_freight_inr_per_qtl_km"]
            expected = 2.0 + 394.0 / (20.0 * 229.7)
            self.assertIsNotNone(be)
            self.assertAlmostEqual(be, expected, delta=0.001)

    def test_g4_synthetic_travel_recommendation(self):
        """G4: Remote market 40 km away with +30% price yields 'travel' recommendation."""
        mock_rows = [
            {"market": "Local Nashik", "district": "Nashik", "state": "Maharashtra", "lat": 19.9975, "lon": 73.7898,
             "modal_price": 2000.0, "history_7d": None, "source": "frozen_real", "as_of": "2026-09-24", "price_date": "2026-09-24"},
            {"market": "Remote High", "district": "Thane", "state": "Maharashtra", "lat": 20.25, "lon": 73.95,
             "modal_price": 2600.0, "history_7d": None, "source": "frozen_real", "as_of": "2026-09-24", "price_date": "2026-09-24"}
        ]
        with patch.object(mandi, "get_market_rows", return_value=mock_rows):
            with patch.object(logistics, "road_km", side_effect=lambda lat1, lon1, lat2, lon2: 40.0):
                plan = planner.build_sell_plan("Tomato", 20.0, "Nashik, Maharashtra", 0.2)
                self.assertTrue(plan["ok"])
                self.assertEqual(plan["best"]["market"], "Remote High")
                self.assertEqual(plan["recommendation"], "travel")
                self.assertTrue(plan["uplift_pct_vs_local"] >= 5.0)

    def test_g5_net_reconciliation(self):
        """G5: For every plan, best.net == gross - sum(cost components) exactly."""
        with patch.object(mandi.MandiApiAdapter, "fetch_rows", side_effect=RuntimeError("Offline test")):
            plan = planner.build_sell_plan("Tomato", 20.0, "Nashik, Maharashtra", 0.2)
            best = plan["best"]
            costs = best["freight"] + best["commission"] + best["loading"] + best["spoilage_loss"]
            self.assertEqual(best["net"], best["gross"] - costs)

    def test_g6_severity_net_invariance(self):
        """G6: Severity values 0.0, 0.2, 0.3 yield identical financial nets, and severity_in_net is False."""
        with patch.object(mandi.MandiApiAdapter, "fetch_rows", side_effect=RuntimeError("Offline test")):
            p0 = planner.build_sell_plan("Tomato", 20.0, "Nashik, Maharashtra", 0.0)
            p2 = planner.build_sell_plan("Tomato", 20.0, "Nashik, Maharashtra", 0.2)
            p3 = planner.build_sell_plan("Tomato", 20.0, "Nashik, Maharashtra", 0.3)
            self.assertEqual(p0["best"]["net"], p2["best"]["net"])
            self.assertEqual(p2["best"]["net"], p3["best"]["net"])
            self.assertEqual(p0["uplift_inr_vs_local"], p2["uplift_inr_vs_local"])
            self.assertEqual(p2["uplift_inr_vs_local"], p3["uplift_inr_vs_local"])
            self.assertFalse(p2["assumptions"]["severity_in_net"])

    def test_g7_stale_exclusion(self):
        """G7: Market with arrival date 3 days older than local is excluded from ranking to excluded_stale."""
        mock_rows = [
            {"market": "Local Nashik", "district": "Nashik", "state": "Maharashtra", "lat": 19.9975, "lon": 73.7898,
             "modal_price": 2000.0, "history_7d": None, "source": "frozen_real", "as_of": "2026-09-24", "price_date": "2026-09-24"},
            {"market": "Stale Panvel", "district": "Raigad", "state": "Maharashtra", "lat": 18.9894, "lon": 73.1175,
             "modal_price": 5000.0, "history_7d": None, "source": "frozen_real", "as_of": "2026-09-20", "price_date": "2026-09-20"}
        ]
        with patch.object(mandi, "get_market_rows", return_value=mock_rows):
            plan = planner.build_sell_plan("Tomato", 20.0, "Nashik, Maharashtra", 0.2)
            self.assertTrue(plan["ok"])
            ranked_markets = [opt["market"] for opt in plan["top_options"]]
            self.assertNotIn("Stale Panvel", ranked_markets)
            stale_markets = [s["market"] for s in plan["excluded_stale"]]
            self.assertIn("Stale Panvel", stale_markets)

    def test_g8_sensitivity_ordering(self):
        """G8: Sensitivity monotonic ordering checks across freight and remote price shifts."""
        with patch.object(mandi.MandiApiAdapter, "fetch_rows", side_effect=RuntimeError("Offline test")):
            plan = planner.build_sell_plan("Tomato", 20.0, "Nashik, Maharashtra", 0.2)
            sens_map = {s["label"]: s["uplift_inr"] for s in plan["sensitivity"]}
            # freight_x1.25 < freight_x1.0 < freight_x0.75
            self.assertTrue(sens_map["freight_x1.25"] < sens_map["freight_x1.0"] < sens_map["freight_x0.75"])
            # remote_price_x0.9 < freight_x1.0
            self.assertTrue(sens_map["remote_price_x0.9"] < sens_map["freight_x1.0"])
            # grade_discount_5pct_both < base
            self.assertTrue(sens_map["grade_discount_5pct_both"] < sens_map["freight_x1.0"])

    def test_g9_classify_boundary_table(self):
        """G9: Table-driven boundary tests for classify pure function."""
        # Boundaries: pct 4.99 vs 5.0, inr 0, freight_x1.25 uplift <= 0
        cases = [
            # uplift_pct, uplift_inr, freight_x125_uplift, expected
            (4.99, 100.0, 50.0, "marginal"),
            (5.0, 100.0, 50.0, "travel"),
            (6.5, 200.0, 10.0, "travel"),
            (10.0, 500.0, -10.0, "marginal"),   # freight_x1.25 <= 0 downgrades travel to marginal
            (10.0, 500.0, 0.0, "marginal"),     # freight_x1.25 == 0 downgrades travel to marginal
            (0.0, 0.0, -100.0, "sell_local"),   # inr <= 0
            (-1.5, -50.0, -150.0, "sell_local") # inr < 0
        ]
        for pct, inr, f125, exp in cases:
            with self.subTest(pct=pct, inr=inr, f125=f125):
                self.assertEqual(planner.classify(pct, inr, f125), exp)

    def test_g10_no_stale_34_8_in_tracked_text_files(self):
        """G10: Verify no '34.8' string exists in tracked text files."""
        repo_root = pathlib.Path(__file__).parent.parent
        tracked_dirs = [
            repo_root / "app.py",
            repo_root / "agent",
            repo_root / "tools",
            repo_root / "README.md",
            repo_root / "docs"
        ]
        hits = []
        scanned_files = []
        for item in tracked_dirs:
            if item.is_file():
                scanned_files.append(item)
                content = item.read_text(encoding="utf-8", errors="ignore")
                if "34.8" in content:
                    hits.append(str(item))
            elif item.is_dir():
                for f in item.rglob("*"):
                    if f.is_file() and not f.name.endswith(".pyc"):
                        scanned_files.append(f)
                        content = f.read_text(encoding="utf-8", errors="ignore")
                        if "34.8" in content:
                            hits.append(str(f))
        self.assertTrue(len(scanned_files) >= 10, f"Expected >=10 files scanned, got {len(scanned_files)}")
        self.assertEqual(hits, [], f"Found stale 34.8 in {hits}")

    def test_t1_to_iso_parsing(self):
        """T1: _to_iso correctly parses YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY and returns None for invalid."""
        valid_cases = [
            ("2026-09-24", "2026-09-24"),
            ("24/09/2026", "2026-09-24"),
            ("24-09-2026", "2026-09-24")
        ]
        for raw, exp in valid_cases:
            with self.subTest(raw=raw):
                self.assertEqual(mandi._to_iso(raw), exp)

        invalid_cases = ["garbage", "", None, 12345]
        for raw in invalid_cases:
            with self.subTest(raw=raw):
                self.assertIsNone(mandi._to_iso(raw))

    def test_t2_history_month_boundary_sorting(self):
        """T2: Dates across month boundary in DD/MM/YYYY format sort chronologically."""
        raw_dates = ["30/09/2026", "01/10/2026", "02/10/2026"]
        iso_dates = [mandi._to_iso(d) for d in raw_dates]
        sorted_iso = sorted(iso_dates)
        self.assertEqual(sorted_iso, ["2026-09-30", "2026-10-01", "2026-10-02"])
        # First vs last calculation
        prices = [1000.0, 1100.0, 1200.0]
        t_pct = optimizer.trend_pct(prices)
        self.assertEqual(t_pct, 20.0)

    def test_t3_trend_span_days_calendar(self):
        """T3: trend_span_days equals real calendar span; 2-day history gives span 1."""
        d1 = mandi._to_iso("30/09/2026")
        d2 = mandi._to_iso("01/10/2026")
        import datetime
        span = (datetime.date.fromisoformat(d2) - datetime.date.fromisoformat(d1)).days
        self.assertEqual(span, 1)

    def test_t4_timing_advice_dynamic_span_no_hardcoded_7_days(self):
        """T4: timing_advice contains the span number and not the hardcoded substring '7 days'."""
        adv1 = optimizer.timing_advice(severity=0.2, best_trend_pct=15.0, trend_span_days=3)
        self.assertIn("over 3 days", adv1["reason"])
        self.assertNotIn("7 days", adv1["reason"])

        adv2 = optimizer.timing_advice(severity=0.2, best_trend_pct=None)
        self.assertNotIn("7 days", adv2["reason"])

    def test_t5_seeded_plan_synthetic_flag_and_none_price_date(self):
        """T5: Seeded plan has is_synthetic=True, best.price_date=None, and no today's ISO date."""
        import datetime
        today_iso = datetime.date.today().isoformat()
        rows = mandi.SeededSnapshotAdapter.fetch_rows("Tomato")
        with patch.object(mandi, "get_market_rows", return_value=rows):
            plan = planner.build_sell_plan("Tomato", 20.0, "Nashik, Maharashtra", 0.2)
            self.assertTrue(plan["ok"])
            self.assertTrue(plan["is_synthetic"])
            self.assertIsNone(plan["best"]["price_date"])
            self.assertIsNone(plan["price_date"])
            # Ensure no today's date in price_date fields
            self.assertNotEqual(plan.get("price_date"), today_iso)
            self.assertNotEqual(plan["best"].get("price_date"), today_iso)

    def test_t6_real_frozen_plan_is_synthetic_false_g1_unchanged(self):
        """T6: Real frozen plan has is_synthetic=False and G1 verified numbers remain unchanged."""
        plan = planner.build_sell_plan("Tomato", 20.0, "Nashik, Maharashtra", 0.2)
        self.assertTrue(plan["ok"])
        self.assertFalse(plan["is_synthetic"])
        self.assertEqual(plan["local_baseline"]["net"], 40860.0)
        self.assertEqual(plan["best"]["net"], 41254.0)
        self.assertEqual(plan["uplift_inr_vs_local"], 394.0)
        self.assertEqual(round(plan["uplift_pct_vs_local"], 2), 0.96)
        self.assertEqual(plan["recommendation"], "marginal")

    def test_t7_app_source_contains_exact_synthetic_banner(self):
        """T7: app.py source code contains exact sample data warning banner string."""
        app_file = pathlib.Path(__file__).parent.parent / "app.py"
        content = app_file.read_text(encoding="utf-8")
        banner = "Sample data - not live market prices. Do not use for a real selling decision."
        self.assertIn(banner, content)

    def test_t8_no_trend_7d_pct_in_app_agent_tools(self):
        """T8: No un-aliased 'trend_7d_pct' left anywhere in app.py, agent/, tools/."""
        repo_root = pathlib.Path(__file__).parent.parent
        scan_targets = [
            repo_root / "app.py",
            repo_root / "agent",
            repo_root / "tools"
        ]
        hits = []
        for target in scan_targets:
            if target.is_file():
                content = target.read_text(encoding="utf-8", errors="ignore")
                if "trend_7d_pct" in content:
                    hits.append(str(target))
            elif target.is_dir():
                for f in target.rglob("*"):
                    if f.is_file() and not f.name.endswith(".pyc"):
                        content = f.read_text(encoding="utf-8", errors="ignore")
                        if "trend_7d_pct" in content:
                            hits.append(str(f))
        self.assertEqual(hits, [], f"Found residual trend_7d_pct in: {hits}")


if __name__ == "__main__":
    unittest.main()
