"""Deterministic safety checks that run in code, not in the LLM."""
CONFIDENCE_THRESHOLD = 0.6
SEVERE = 0.7


def check_diagnosis(d: dict) -> dict:
    conf = float(d.get("confidence", 0))
    if d.get("disease_id") in ("unknown", None) or conf < CONFIDENCE_THRESHOLD:
        return {
            "status": "low_confidence",
            "action": "Ask the farmer for a clearer, closer, well-lit photo of the affected leaf "
                      "(top and underside). Do NOT recommend chemical pesticides yet.",
        }
    if float(d.get("severity", 0)) >= SEVERE:
        return {
            "status": "severe",
            "action": "Recommend contacting the nearest Krishi Vigyan Kendra (KVK) or agriculture "
                      "officer in addition to the remedy.",
        }
    return {"status": "ok", "action": "Proceed. List organic options first."}
