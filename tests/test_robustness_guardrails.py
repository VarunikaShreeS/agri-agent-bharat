"""Unit tests for Phase 4: Robustness, Demo Mode, Safety Guardrails, and Numeric Grounding."""
import sys
import json
import pathlib
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from agent import guardrails


class TestRobustnessAndGuardrails(unittest.TestCase):
    def test_guardrail_low_confidence(self):
        """Low confidence (<0.6) triggers low_confidence status and blocks chemical recommendation."""
        res = guardrails.check_diagnosis({"confidence": 0.45, "disease": "early_blight", "severity": 0.2})
        self.assertEqual(res["status"], "low_confidence")
        self.assertIn("Do NOT recommend chemical pesticides", res["action"])

    def test_guardrail_severe_kvk_escalation(self):
        """High infection severity (>=0.7) triggers severe escalation to local KVK."""
        res = guardrails.check_diagnosis({"confidence": 0.90, "disease": "leaf_curl_virus", "severity": 0.85})
        self.assertEqual(res["status"], "severe")
        self.assertIn("Krishi Vigyan Kendra (KVK)", res["action"])

    def test_guardrail_ok_status(self):
        """Normal confidence and mild severity proceed with organic-first guidance."""
        res = guardrails.check_diagnosis({"confidence": 0.90, "disease": "early_blight", "severity": 0.25})
        self.assertEqual(res["status"], "ok")
        self.assertIn("organic options first", res["action"])

    def test_numeric_grounding_verifier_valid(self):
        """Advisory containing numbers strictly present in tool outputs passes grounding check."""
        answer = "Your 20 quintals can be sold at Vashi APMC for net ₹41,254, gaining ₹394 over local mandi. Distance is 229.7 km."
        tool_outputs = [
            {"market": "Vashi APMC", "net": 41254.0, "distance_km": 229.7, "modal_price": 2750.0},
            {"uplift_inr_vs_local": 394.0}
        ]
        res = guardrails.verify_numeric_grounding(answer, tool_outputs, allowed_inputs=[20.0])
        self.assertTrue(res["verified"])
        self.assertEqual(len(res["unverified_figures"]), 0)

    def test_numeric_grounding_verifier_flags_hallucination(self):
        """Advisory containing invented prices/numbers triggers unverified warning."""
        answer = "You will get ₹99,999 at Fantasy Market which is 850 km away with dose of 45.5 kg/L."
        tool_outputs = [
            {"market": "Vashi APMC", "net": 41254.0, "distance_km": 229.7, "modal_price": 2750.0}
        ]
        res = guardrails.verify_numeric_grounding(answer, tool_outputs, allowed_inputs=[20.0])
        self.assertFalse(res["verified"])
        self.assertTrue(99999.0 in res["unverified_figures"] or 850.0 in res["unverified_figures"])
        self.assertIsNotNone(res["warning"])

    def test_demo_cache_files_exist_and_valid(self):
        """Demo cache contains valid JSON and audio files for EN, HI, and TA."""
        cache_dir = pathlib.Path("demo_cache")
        self.assertTrue(cache_dir.exists())

        required_runs = ["tomato_early_blight_en", "tomato_leaf_curl_hi", "tomato_tamil_run"]
        for r_id in required_runs:
            json_file = cache_dir / f"{r_id}.json"
            mp3_file = cache_dir / f"{r_id}.mp3"
            self.assertTrue(json_file.exists(), f"Missing {json_file}")
            self.assertTrue(mp3_file.exists(), f"Missing {mp3_file}")
            data = json.loads(json_file.read_text(encoding="utf-8"))
            self.assertEqual(data["id"], r_id)
            self.assertIn("answer", data)
            self.assertIn("plan", data)


if __name__ == "__main__":
    unittest.main()
