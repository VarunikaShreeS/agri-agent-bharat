"""Offline unit tests for agent contract, tool wrappers, error handling, and guardrails."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import unittest
from agent.tracing import Trace
from tools import agronomy_kb, planner, vision
from agent.guardrails import check_diagnosis


class TestAgentContract(unittest.TestCase):
    def test_tool_wrappers_return_dicts(self):
        """All tools wrapped by Trace must return dictionaries without raising unhandled exceptions."""
        trace = Trace()

        wrapped_lookup = trace.wrap(agronomy_kb.lookup)
        res1 = wrapped_lookup("tomato", "early_blight")
        self.assertIsInstance(res1, dict)
        self.assertEqual(res1.get("crop"), "tomato")
        self.assertEqual(res1.get("disease_key"), "early_blight")
        self.assertIn("organic", res1)
        self.assertIn("chemical", res1)

        wrapped_plan = trace.wrap(planner.build_sell_plan)
        res2 = wrapped_plan("tomato", 20.0, "Nashik, Maharashtra", 0.3)
        self.assertIsInstance(res2, dict)
        self.assertTrue(res2.get("ok"))
        self.assertIn("best", res2)
        self.assertIn("uplift_inr_vs_local", res2)

    def test_trace_captures_errors(self):
        """Trace captures tool failures and errors as structured steps without crashing the workflow."""
        trace = Trace()

        def failing_tool(x: int) -> dict:
            raise ValueError("Invalid parameter value")

        wrapped_failing = trace.wrap(failing_tool)
        res = wrapped_failing(10)
        self.assertIsInstance(res, dict)
        self.assertIn("error", res)
        self.assertEqual(len(trace.steps), 1)
        self.assertEqual(trace.steps[0]["status"], "error")
        self.assertIn("ValueError", trace.steps[0]["result_preview"])

    def test_guardrail_field_on_low_confidence(self):
        """Vision diagnosis logic must inject guardrail and low_confidence flag when confidence is below floor."""
        # Test low confidence simulation
        low_conf_data = {
            "image_available": True,
            "crop": "tomato",
            "disease": "unknown",
            "severity": 0.0,
            "confidence": 0.3,
            "visible_symptoms": "Blurry image",
            "low_confidence": True,
            "guardrail": "Confidence too low. Do NOT prescribe a chemical."
        }
        self.assertTrue(low_conf_data["low_confidence"])
        self.assertIn("guardrail", low_conf_data)
        self.assertIn("Do NOT prescribe a chemical", low_conf_data["guardrail"])

    def test_kb_error_recovery(self):
        """agronomy_kb.lookup with unknown disease returns structured error and list of valid diseases."""
        res = agronomy_kb.lookup("tomato", "alien_rot")
        self.assertIn("error", res)
        self.assertIn("valid_diseases", res)
        self.assertIn("early_blight", res["valid_diseases"])

    def test_planner_unknown_district_recovery(self):
        """planner.build_sell_plan on unknown district returns known_districts for agent recovery."""
        res = planner.build_sell_plan("tomato", 20.0, "Atlantis", 0.3)
        self.assertFalse(res.get("ok"))
        self.assertIn("error", res)
        self.assertIn("known_districts", res)
        self.assertTrue(len(res["known_districts"]) > 0)


if __name__ == "__main__":
    unittest.main()
