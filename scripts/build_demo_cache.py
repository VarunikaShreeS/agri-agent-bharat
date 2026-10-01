"""Builds demo_cache/ with 3 pre-recorded runs (EN, HI, TA) for offline DEMO_MODE=1 operation."""
import os
import sys
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from agent.orchestrator import run_agent
from voice.tts import generate_speech, build_spoken_summary

CACHE_DIR = pathlib.Path("demo_cache")
CACHE_DIR.mkdir(exist_ok=True)

RUNS = [
    {
        "id": "tomato_early_blight_en",
        "title": "Tomato Early Blight (English)",
        "crop": "Tomato",
        "district": "Nashik, Maharashtra",
        "quantity_quintals": 20.0,
        "query": "Leaves have dark concentric rings and yellow halos. What should I spray and where should I sell?",
        "language": "English",
        "image_file": "tests/samples/tomato_early_blight.jpg"
    },
    {
        "id": "tomato_leaf_curl_hi",
        "title": "Tomato Leaf Curl (Hindi)",
        "crop": "Tomato",
        "district": "Nashik, Maharashtra",
        "quantity_quintals": 20.0,
        "query": "पत्तियां ऊपर की तरफ मुड़ रही हैं और पीली पड़ रही हैं। क्या उपाय करें और टमाटर कहाँ बेचें?",
        "language": "Hindi",
        "image_file": "tests/samples/tomato_leaf_curl.jpg"
    },
    {
        "id": "tomato_tamil_run",
        "title": "Tomato Early Blight (Tamil)",
        "crop": "Tomato",
        "district": "Salem, Tamil Nadu",
        "quantity_quintals": 20.0,
        "query": "தக்காளி இலைகளில் கரும்புள்ளிகள் மற்றும் வளையங்கள் உள்ளன. மருந்து மற்றும் விற்பனை சந்தை தேவை.",
        "language": "Tamil",
        "image_file": "tests/samples/tomato_early_blight.jpg"
    }
]

def main():
    audio_only = "--audio-only" in sys.argv
    if audio_only:
        print("Regenerating spoken summaries and audio only (no Gemini calls)...")
        for r in RUNS:
            json_path = CACHE_DIR / f"{r['id']}.json"
            if not json_path.exists():
                print(f"  Warning: {json_path} not found, skipping.")
                continue
            data = json.loads(json_path.read_text(encoding="utf-8"))
            print(f"\nProcessing {data.get('title', r['id'])} (Audio Only)...")
            
            spoken_sum = build_spoken_summary(data.get("diagnosis", {}), data.get("plan", {}), language=data.get("language", "English"))
            audio_bytes = generate_speech(spoken_sum, language_label=data.get("language", "English"))
            
            audio_filename = data.get("audio_file", f"{r['id']}.mp3")
            audio_path = CACHE_DIR / audio_filename
            if audio_bytes:
                audio_path.write_bytes(audio_bytes)
                print(f"  Saved audio to {audio_path} ({len(audio_bytes)} bytes)")
            
            data["spoken_summary"] = spoken_sum
            json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  Updated run data in {json_path}")
        print("\nAll demo cache audio and spoken summaries updated successfully!")
        return

    print("Building demo cache for offline DEMO_MODE=1...")
    for r in RUNS:
        print(f"\nProcessing {r['title']}...")
        img_bytes = None
        if r["image_file"] and os.path.exists(r["image_file"]):
            with open(r["image_file"], "rb") as f:
                img_bytes = f.read()

        res = run_agent(
            crop=r["crop"],
            district=r["district"],
            quantity_quintals=r["quantity_quintals"],
            query=r["query"],
            language=r["language"],
            image_bytes=img_bytes,
            image_mime="image/jpeg"
        )

        spoken_sum = build_spoken_summary(res.diagnosis, res.plan, language=r["language"])
        audio_bytes = generate_speech(spoken_sum, language_label=r["language"])

        audio_filename = f"{r['id']}.mp3"
        audio_path = CACHE_DIR / audio_filename
        if audio_bytes:
            audio_path.write_bytes(audio_bytes)
            print(f"  Saved audio to {audio_path} ({len(audio_bytes)} bytes)")

        cache_data = {
            "id": r["id"],
            "title": r["title"],
            "crop": r["crop"],
            "district": r["district"],
            "quantity_quintals": r["quantity_quintals"],
            "query": r["query"],
            "language": r["language"],
            "answer": res.answer,
            "spoken_summary": spoken_sum,
            "audio_file": audio_filename,
            "diagnosis": res.diagnosis,
            "plan": res.plan,
            "trace": res.trace,
            "model": res.model,
            "errors": res.errors
        }

        json_path = CACHE_DIR / f"{r['id']}.json"
        json_path.write_text(json.dumps(cache_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  Saved run data to {json_path}")

    print("\nAll 3 demo cache items generated successfully!")

if __name__ == "__main__":
    main()
