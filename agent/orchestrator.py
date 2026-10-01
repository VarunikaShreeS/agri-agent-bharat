"""KrishiChain orchestrator: Gemini function-calling loop over real tools, with trace + guardrails."""
import os
from dataclasses import dataclass, field

from google import genai
from google.genai import types

from tools import agronomy_kb, planner, vision
from .tracing import Trace

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")  # set GEMINI_MODEL to whatever your AI Studio key supports
MAX_TOOL_CALLS = 8

SYSTEM = """You are KrishiChain, an autonomous agent helping a smallholder farmer in India.
Work in this order, deciding tool use yourself:
1. If a leaf image is available call analyze_leaf_image first. If it returns low_confidence, STOP prescribing: ask for a better photo and refer to the nearest KVK.
2. Call lookup_remedy with the diagnosed disease (or infer the closest disease from the farmer's symptoms if there is no image). If it errors, use the valid_diseases it returns.
3. Call compute_sell_plan with the farmer's crop, quantity, district and the diagnosed severity (use 0.3 if unknown).
4. Write the final advisory.
Hard rules:
- NEVER invent prices, distances, costs or doses. Use only numbers returned by tools.
- Always show organic options before chemical ones and mention the pre-harvest interval.
- State whether prices are live or a cached/seeded snapshot (data_source, data_as_of).
- If a tool errors, adapt (try another input, explain the limitation) rather than fabricate.
- Final answer must be written ENTIRELY in the requested language, in simple, encouraging words, with sections:
  Diagnosis, Treatment (organic first), Where to sell (best market, net rupees, uplift vs local mandi, timing), Next 3 days.
"""


@dataclass
class AgentResult:
    answer: str
    trace: list
    diagnosis: dict = None
    plan: dict = None
    model: str = MODEL
    errors: list = field(default_factory=list)


def run_agent(*, crop, district, quantity_quintals, query, language, image_bytes=None, image_mime="image/jpeg", api_key=None):
    client = genai.Client(api_key=api_key or os.getenv("GEMINI_API_KEY"))
    trace = Trace()
    art = {"diagnosis": None, "plan": None}

    def analyze_leaf_image(crop: str) -> dict:
        """Diagnose the uploaded leaf photo. Returns disease, severity (0-1), confidence (0-1) and a low_confidence flag."""
        if not image_bytes:
            return {"image_available": False, "note": "No photo uploaded; rely on the farmer's text symptoms."}
        out = vision.diagnose(client, MODEL, image_bytes, image_mime, crop)
        art["diagnosis"] = out
        return out

    def lookup_remedy(crop: str, disease: str) -> dict:
        """Get organic and chemical treatment, doses, spray interval and pre-harvest interval for a crop disease."""
        return agronomy_kb.lookup(crop, disease)

    def compute_sell_plan(crop: str, quantity_quintals: float, home_district: str, severity: float) -> dict:
        """Rank nearby mandis by NET rupees after transport, commission and spoilage; compare with the local mandi; advise timing."""
        out = planner.build_sell_plan(crop, quantity_quintals, home_district, severity)
        if out.get("ok"):
            art["plan"] = out
        return out

    tools = [trace.wrap(f) for f in (analyze_leaf_image, lookup_remedy, compute_sell_plan)]
    user_msg = (f"Crop: {crop}\nDistrict/State: {district}\nQuantity to sell: {quantity_quintals} quintals\n"
                f"Farmer's words: {query}\nImage uploaded: {'yes' if image_bytes else 'no'}\nRespond in: {language}")
    errors = []
    try:
        resp = client.models.generate_content(
            model=MODEL, contents=user_msg,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM, tools=tools, temperature=0.2,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(maximum_remote_calls=MAX_TOOL_CALLS)))
        answer = resp.text or "The agent could not produce an advisory. Please retry or contact your nearest KVK."
    except Exception as e:
        errors.append(f"{type(e).__name__}: {e}")
        answer = "Sorry, the advisory service hit an error. Please try again, or contact your nearest Krishi Vigyan Kendra."
    return AgentResult(answer=answer, trace=trace.steps, diagnosis=art["diagnosis"], plan=art["plan"], errors=errors)
