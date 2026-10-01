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

    def test_s1_marginal_summary_no_best_market_or_gain_en(self):
        """S1: Marginal plan spoken summary in EN contains no 'best market' or 'gain'."""
        from voice.tts import build_spoken_summary
        diagnosis = {"image_available": True, "disease": "early_blight", "severity": 0.2}
        plan = {
            "ok": True,
            "recommendation": "marginal",
            "best": {"market": "APMC Panvel", "net": 41254.0},
            "local_baseline": {"market": "APMC Ghoti", "net": 40860.0},
            "uplift_inr_vs_local": 394.0,
            "uplift_pct_vs_local": 0.96,
            "is_synthetic": False
        }
        summary = build_spoken_summary(diagnosis, plan, language="English")
        self.assertNotIn("best market", summary.lower())
        self.assertNotIn("gain", summary.lower())
        self.assertIn("roughly break-even", summary)
        self.assertIn("lower risk", summary)

    def test_s2_synthetic_plan_summary_disclaimer(self):
        """S2: Synthetic plan summary contains the disclaimer in EN, HI, and TA."""
        from voice.tts import build_spoken_summary
        diagnosis = {"image_available": True, "disease": "early_blight", "severity": 0.2}
        plan = {
            "ok": True,
            "recommendation": "travel",
            "best": {"market": "APMC Panvel", "net": 41254.0},
            "local_baseline": {"market": "APMC Ghoti", "net": 40860.0},
            "uplift_inr_vs_local": 394.0,
            "uplift_pct_vs_local": 0.96,
            "is_synthetic": True
        }
        en_sum = build_spoken_summary(diagnosis, plan, language="English")
        hi_sum = build_spoken_summary(diagnosis, plan, language="Hindi")
        ta_sum = build_spoken_summary(diagnosis, plan, language="Tamil")

        self.assertTrue(en_sum.startswith("This is sample data, not live prices."))
        self.assertTrue(hi_sum.startswith("यह केवल नमूना डेटा है, वास्तविक दरें नहीं।"))
        self.assertTrue(ta_sum.startswith("இது மாதிரி தரவு மட்டுமே, நேரடி விலை அல்ல."))

    def test_s3_numeric_grounding_in_spoken_summaries(self):
        """S3: Every number in each demo cache summary is grounded in the plan/diagnosis."""
        import re
        cache_dir = pathlib.Path("demo_cache")
        required_runs = ["tomato_early_blight_en", "tomato_leaf_curl_hi", "tomato_tamil_run"]
        for r_id in required_runs:
            json_file = cache_dir / f"{r_id}.json"
            data = json.loads(json_file.read_text(encoding="utf-8"))
            summary = data["spoken_summary"]
            # Extract numbers from summary
            raw_nums = re.findall(r"[\d,]+(?:\.\d+)?", summary)
            nums = [float(n.replace(",", "")) for n in raw_nums if n.replace(",", "")]
            
            # Grounding sources: plan, diagnosis, standard timing horizon (3 days)
            plan = data.get("plan", {})
            diag = data.get("diagnosis", {})
            
            allowed_nums = {3.0}  # standard 3-day action window
            if diag:
                allowed_nums.add(round(float(diag.get("severity", 0) * 100), 1))
                allowed_nums.add(float(diag.get("severity", 0)))
            if plan:
                allowed_nums.add(float(plan.get("uplift_inr_vs_local", 0)))
                allowed_nums.add(round(float(plan.get("uplift_pct_vs_local", 0)), 2))
                allowed_nums.add(float(plan.get("quantity_quintals", 0)))
                if "best" in plan:
                    allowed_nums.add(float(plan["best"].get("net", 0)))
                    allowed_nums.add(float(plan["best"].get("price_per_quintal", 0)))
                if "local_baseline" in plan:
                    allowed_nums.add(float(plan["local_baseline"].get("net", 0)))
                    allowed_nums.add(float(plan["local_baseline"].get("price_per_quintal", 0)))
            
            for n in nums:
                self.assertTrue(
                    any(abs(n - a) < 0.01 for a in allowed_nums),
                    f"Number {n} in summary '{summary}' of {r_id} not grounded in plan {allowed_nums}"
                )

    def test_marginal_demo_cache_advisory_text_policy(self):
        """For every demo cache file with recommendation == 'marginal', the full 'answer' text must match marginal policy."""
        cache_dir = pathlib.Path("demo_cache")
        for f in cache_dir.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            rec = data.get("plan", {}).get("recommendation")
            if rec == "marginal":
                answer = data.get("answer", "")
                lang = data.get("language", "")
                if "english" in lang.lower():
                    self.assertNotIn("best market", answer.lower(), f"Found 'best market' in {f.name}")
                    self.assertNotIn("sell at the best net-return market", answer.lower(), f"Found 'sell at the best net-return market' in {f.name}")
                    self.assertIn("break-even", answer.lower(), f"Expected break-even in {f.name}")
                    self.assertIn("lower risk", answer.lower(), f"Expected lower risk in {f.name}")
                elif "hindi" in lang.lower():
                    self.assertNotIn("सर्वोत्तम मंडी", answer, f"Found 'सर्वोत्तम मंडी' in {f.name}")
                    self.assertNotIn("सबसे अच्छा विकल्प", answer, f"Found 'सबसे अच्छा विकल्प' in {f.name}")
                    self.assertNotIn("अधिक लाभ", answer, f"Found 'अधिक लाभ' in {f.name}")
                    self.assertIn("बराबर", answer, f"Expected बराबर in {f.name}")
                    self.assertIn("कम जोखिम", answer, f"Expected कम जोखिम in {f.name}")


if __name__ == "__main__":
    unittest.main()
