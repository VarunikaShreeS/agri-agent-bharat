"""Smoke test for Gemini API connectivity, function-calling, and multimodal structured output."""
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not api_key:
    print("ERROR: GEMINI_API_KEY not set in .env")
    sys.exit(1)

client = genai.Client(api_key=api_key)

print(f"Testing Gemini SDK (google-genai) with model: {model}...")

# Test 1: Text-only generation
print("\n[1/3] Testing text-only generate_content...")
try:
    resp1 = client.models.generate_content(
        model=model,
        contents="Reply with exactly 'KrishiChain Online' and nothing else."
    )
    print("  Output:", resp1.text.strip())
    assert "KrishiChain" in resp1.text or len(resp1.text) > 0, "No text returned"
    print("  PASS Test 1 (text-only)")
except Exception as e:
    print(f"  FAIL Test 1: {e}")
    sys.exit(1)

# Test 2: Function calling with a dummy tool
print("\n[2/3] Testing automatic function calling...")
tool_called = False

def get_mandi_distance(mandi_name: str) -> dict:
    """Get the distance to a mandi in kilometers."""
    global tool_called
    tool_called = True
    return {"mandi": mandi_name, "distance_km": 42.5}

try:
    resp2 = client.models.generate_content(
        model=model,
        contents="What is the distance to Pimpalgaon mandi?",
        config=types.GenerateContentConfig(
            tools=[get_mandi_distance],
            temperature=0.1,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(maximum_remote_calls=3)
        )
    )
    print(f"  Tool called: {tool_called}")
    print("  Output:", resp2.text.strip()[:100], "...")
    assert tool_called, "Function calling tool was not executed"
    print("  PASS Test 2 (function calling)")
except Exception as e:
    print(f"  FAIL Test 2: {e}")
    sys.exit(1)

# Test 3: Multimodal image + structured output (response_schema)
print("\n[3/3] Testing multimodal image + response_schema...")
class LeafDiagnosis(BaseModel):
    crop: str
    disease: str
    severity: float
    confidence: float
    visible_symptoms: str

sample_img = os.path.join("tests", "samples", "tomato_early_blight.jpg")
if not os.path.exists(sample_img):
    print(f"  FAIL Test 3: Sample image {sample_img} not found")
    sys.exit(1)

with open(sample_img, "rb") as f:
    img_data = f.read()

try:
    resp3 = client.models.generate_content(
        model=model,
        contents=[
            types.Part.from_bytes(data=img_data, mime_type="image/jpeg"),
            "Diagnose this tomato leaf. Return valid JSON matching schema."
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LeafDiagnosis,
            temperature=0.1
        )
    )
    # Check parsing
    raw_text = resp3.text.strip()
    # Handle possible markdown fences if any
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    parsed = getattr(resp3, "parsed", None) or LeafDiagnosis.model_validate_json(raw_text)
    print(f"  Parsed Diagnosis: disease='{parsed.disease}', severity={parsed.severity}, confidence={parsed.confidence}")
    print(f"  Symptoms: {parsed.visible_symptoms}")
    print("  PASS Test 3 (image + schema)")
except Exception as e:
    print(f"  FAIL Test 3: {e}")
    sys.exit(1)

print("\nALL 3 GEMINI SMOKE TESTS PASSED!")
