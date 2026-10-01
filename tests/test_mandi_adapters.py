"""Offline unit tests for mandi price adapters and provider chain using recorded fixtures."""
import sys
import json
import pathlib
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from tools import mandi, optimizer, planner


class TestMandiAdapters(unittest.TestCase):
    def setUp(self):
        self.fixtures_dir = pathlib.Path(__file__).parent / "fixtures"

    def test_mandi_api_adapter_fixture(self):
        """MandiApiAdapter correctly normalizes live API json with district coords."""
        fixture_file = self.fixtures_dir / "mandi_api_tomato.json"
        if not fixture_file.exists():
            self.skipTest("mandi_api_tomato.json fixture not present")
        
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = json.loads(fixture_file.read_text(encoding="utf-8"))

        with patch("requests.get", return_value=mock_resp):
            rows = mandi.MandiApiAdapter.fetch_rows("Tomato", state="Maharashtra")
            self.assertTrue(len(rows) > 0)
            sample = rows[0]
            self.assertEqual(sample["source"], "live_mandi_api")
            self.assertIn("modal_price", sample)
            self.assertIn("lat", sample)
            self.assertTrue(sample["history_7d"] is None or isinstance(sample["history_7d"], list))

    def test_data_gov_adapter_fixture(self):
        """DataGovAdapter parses data.gov.in records correctly."""
        fixture_file = self.fixtures_dir / "data_gov_response.json"
        if not fixture_file.exists():
            self.skipTest("data_gov_response.json fixture not present")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = json.loads(fixture_file.read_text(encoding="utf-8"))

        with patch.dict("os.environ", {"DATA_GOV_API_KEY": "test_mock_key"}):
            with patch("requests.get", return_value=mock_resp):
                rows = mandi.DataGovAdapter.fetch_rows("Tomato")
                self.assertTrue(len(rows) > 0)
                sample = rows[0]
                self.assertEqual(sample["source"], "live_agmarknet")
                self.assertIn("modal_price", sample)
                self.assertIn("lat", sample)
                self.assertIn("lon", sample)

    def test_frozen_real_adapter(self):
        """FrozenRealAdapter reads from data/mandi_snapshot_frozen.json."""
        rows = mandi.FrozenRealAdapter.fetch_rows("Tomato")
        self.assertTrue(len(rows) > 0)
        sample = rows[0]
        self.assertEqual(sample["source"], "frozen_real")
        self.assertIn("modal_price", sample)
        self.assertIn("lat", sample)
        self.assertIn("lon", sample)

    def test_seeded_snapshot_adapter(self):
        """SeededSnapshotAdapter reads from seed file and includes 7d history."""
        rows = mandi.SeededSnapshotAdapter.fetch_rows("Tomato")
        self.assertTrue(len(rows) > 0)
        sample = rows[0]
        self.assertEqual(sample["source"], "seeded_snapshot")
        self.assertIsNotNone(sample["history_7d"])
        self.assertIsInstance(sample["history_7d"], list)

    def test_optimizer_none_history_safety(self):
        """optimizer.trend_pct and timing_advice handle None history and trend safely."""
        self.assertIsNone(optimizer.trend_pct(None))
        self.assertIsNone(optimizer.trend_pct([]))
        self.assertIsNone(optimizer.trend_pct([100]))
        
        # Test timing advice with None trend
        t1 = optimizer.timing_advice(severity=0.2, best_trend_pct=None)
        self.assertEqual(t1["action"], "sell_at_best_market")
        self.assertIn("No 7-day price trend", t1["reason"])

        # High severity always sells now
        t2 = optimizer.timing_advice(severity=0.8, best_trend_pct=None)
        self.assertEqual(t2["action"], "sell_now")

    def test_provider_chain_fallback_logging(self):
        """When live API raises exception, provider chain falls back to frozen/seed and logs details."""
        with patch("tools.mandi.MandiApiAdapter.fetch_rows", side_effect=RuntimeError("Connection timeout")):
            rows = mandi.get_market_rows("Tomato", home_state="Maharashtra")
            self.assertTrue(len(rows) > 0)
            log = mandi.get_last_provider_log()
            self.assertTrue(len(log) >= 2)
            self.assertEqual(log[0]["provider"], "live_mandi_api")
            self.assertEqual(log[0]["status"], "failed")
            self.assertEqual(rows[0]["source"], "frozen_real")


if __name__ == "__main__":
    unittest.main()
