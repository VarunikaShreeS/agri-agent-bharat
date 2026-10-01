"""Runs Phase 2 verification cases A, B, and E with the new provider chain and outputs docs/phase2_runs.md."""
import os
import sys
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from agent.orchestrator import run_agent

CASES = [
    {
        "id": "a",
        "title": "Case A: Tomato with Early Blight Photo (English) - Live/Frozen Provider Chain",
        "crop": "Tomato",
        "district": "Nashik, Maharashtra",
        "quantity_quintals": 20.0,
        "query": "Leaves have dark spots with yellow halos. What should I spray and where should I sell?",
        "language": "English",
        "image_file": "tests/samples/tomato_early_blight.jpg"
    },
    {
        "id": "b",
        "title": "Case B: Tomato without Photo - Text Symptoms Only (English) - Live/Frozen Provider Chain",
        "crop": "Tomato",
        "district": "Nashik, Maharashtra",
        "quantity_quintals": 20.0,
        "query": "dark rings on lower leaves, yellowing",
        "language": "English",
        "image_file": None
    },
    {
        "id": "e",
        "title": "Case E: Tomato with Leaf Curl Photo (Hindi) - Live/Frozen Provider Chain",
        "crop": "Tomato",
        "district": "Nashik, Maharashtra",
        "quantity_quintals": 20.0,
        "query": "पत्तियां ऊपर की तरफ मुड़ रही हैं और पीली पड़ रही हैं। क्या उपाय करें और टमाटर कहाँ बेचें?",
        "language": "Hindi",
        "image_file": "tests/samples/tomato_leaf_curl.jpg"
    }
]

os.makedirs("docs", exist_ok=True)
md_out = [
    "# KrishiChain Phase 2 Verification Runs — Real Mandi Data & Expanded KB\n",
    f"**Model:** `{os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')}`\n",
    "**Mandi Provider Chain:** Mandi Price API (Live) ➔ data.gov.in (Optional) ➔ Frozen Real Snapshot ➔ Seed Fallback\n"
]

print("==================================================")
print("STARTING PHASE 2 VERIFICATION RUNS (CASES A, B, E)")
print("==================================================\n")

for c in CASES:
    print(f"\n>>> Running {c['title']}...")
    img_bytes = None
    if c["image_file"] and os.path.exists(c["image_file"]):
        with open(c["image_file"], "rb") as f:
            img_bytes = f.read()

    res = run_agent(
        crop=c["crop"],
        district=c["district"],
        quantity_quintals=c["quantity_quintals"],
        query=c["query"],
        language=c["language"],
        image_bytes=img_bytes,
        image_mime="image/jpeg"
    )

    print(f"Result for {c['id']}:")
    print("Diagnosis:", res.diagnosis)
    print("Plan:", "OK" if (res.plan and res.plan.get("ok")) else (res.plan or "None"))
    if res.plan and "provider_log" in res.plan:
        print("Provider log:", res.plan["provider_log"])
    print("Errors:", res.errors)
    print(f"Trace ({len(res.trace)} steps):")
    for s in res.trace:
        print(f"  - Step {s['step']}: {s['tool']} ({s['latency_s']}s) [{s['status']}] -> {s['args']}")

    print("\n--- Advisory Preview ---")
    print(res.answer[:300] + "...\n")

    # Append to markdown report
    md_out.append(f"## {c['title']}\n")
    md_out.append(f"- **Inputs:** Crop: `{c['crop']}`, District: `{c['district']}`, Qty: `{c['quantity_quintals']} qtl`, Language: `{c['language']}`")
    md_out.append(f"- **Image:** `{c['image_file'] or 'None'}`")
    md_out.append(f"- **Diagnosis Result:** `{json.dumps(res.diagnosis)}`")
    md_out.append(f"- **Plan Result:** `{json.dumps(res.plan)}`")
    md_out.append(f"- **Errors:** `{res.errors}`\n")
    md_out.append("### Tool Trace\n")
    md_out.append("| Step | Tool | Latency (s) | Status | Arguments | Result Preview |")
    md_out.append("|---|---|---|---|---|---|")
    for s in res.trace:
        args_str = str(s['args']).replace("|", "\\|")
        res_str = str(s['result_preview']).replace("|", "\\|")
        md_out.append(f"| {s['step']} | `{s['tool']}` | {s['latency_s']} | `{s['status']}` | `{args_str}` | {res_str} |")
    md_out.append("\n### Advisory Text\n")
    md_out.append(f"```text\n{res.answer}\n```\n")
    md_out.append("---\n")

with open("docs/phase2_runs.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md_out))

print("\n==================================================")
print("PHASE 2 RUNS COMPLETED. Saved to docs/phase2_runs.md")
print("==================================================")
