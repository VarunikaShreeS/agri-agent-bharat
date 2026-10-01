"""Tool 1: Vision diagnosis via Gemini, returning validated structured JSON."""
from . import agronomy_kb

CONFIDENCE_FLOOR = 0.6


def diagnose(client, model: str, image_bytes: bytes, mime: str, crop: str) -> dict:
    from google.genai import types
    from agent.schemas import Diagnosis

    allowed = agronomy_kb.disease_keys(crop)
    prompt = (f"You are a plant pathologist. The crop is {crop}. Look at the leaf photo and choose `disease` "
              f"from exactly this list: {allowed}, or 'healthy', or 'unknown' if unsure. "
              "`severity` = fraction of visible leaf area affected (0.0-1.0). `confidence` = your honest 0.0-1.0 certainty. "
              "`visible_symptoms` = one short sentence describing what you actually see. Do not guess beyond the image.")
    resp = client.models.generate_content(
        model=model,
        contents=[types.Part.from_bytes(data=image_bytes, mime_type=mime), prompt],
        config=types.GenerateContentConfig(response_mime_type="application/json",
                                           response_schema=Diagnosis, temperature=0.1))
    raw_text = (resp.text or "").strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    d = getattr(resp, "parsed", None) or (Diagnosis.model_validate_json(raw_text) if raw_text else None)
    if not d:
        return {"image_available": True, "crop": crop, "disease": "unknown", "severity": 0.0, "confidence": 0.0,
                "visible_symptoms": "Could not parse model output", "low_confidence": True,
                "guardrail": "Confidence too low. Do NOT prescribe a chemical."}
    disease = d.disease.strip().lower().replace(" ", "_").replace("-", "_")
    if disease.startswith("tomato_"):
        disease = disease[len("tomato_"):]
    if disease.startswith("onion_"):
        disease = disease[len("onion_"):]
    if disease == "leaf_curl":
        disease = "leaf_curl_virus"
    if disease not in allowed and disease != "healthy":
        disease = "unknown"
    sev = min(max(float(d.severity), 0.0), 1.0)
    conf = min(max(float(d.confidence), 0.0), 1.0)
    low = conf < CONFIDENCE_FLOOR or disease == "unknown"
    out = {"image_available": True, "crop": crop, "disease": disease, "severity": sev, "confidence": conf,
           "visible_symptoms": d.visible_symptoms, "low_confidence": low}
    if low:
        out["guardrail"] = ("Confidence too low. Do NOT prescribe a chemical. Ask the farmer for a clearer, close-up, "
                            "well-lit photo of an affected leaf (top and underside) and suggest visiting the nearest KVK.")
    return out
