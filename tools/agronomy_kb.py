"""Tool 2: Agronomy knowledge base lookup (local curated JSON)."""
import json
from pathlib import Path

_KB = json.loads((Path(__file__).parent.parent / "data" / "kb.json").read_text(encoding="utf-8"))["crops"]


def supported_crops() -> list:
    return sorted(_KB)


def disease_keys(crop: str) -> list:
    return sorted(_KB.get(crop.strip().lower(), {}))


def lookup(crop: str, disease: str) -> dict:
    crop_k = crop.strip().lower()
    dis_k = disease.strip().lower().replace(" ", "_").replace("-", "_")
    if dis_k.startswith(f"{crop_k}_"):
        dis_k = dis_k[len(f"{crop_k}_"):]
    if dis_k == "leaf_curl":
        dis_k = "leaf_curl_virus"
    if crop_k not in _KB:
        return {"found": False, "error": f"Crop '{crop}' not in KB", "supported_crops": supported_crops()}
    entry = _KB[crop_k].get(dis_k)
    if not entry:
        return {"found": False, "error": f"Disease '{disease}' not in KB for {crop}",
                "valid_diseases": disease_keys(crop_k),
                "hint": "Pick the closest valid disease from symptoms, or advise consulting the local KVK."}
    return {"found": True, "crop": crop_k, "disease_key": dis_k, **entry,
            "safety": "Follow label dose; wear protective gear; observe pre-harvest interval; confirm with local KVK."}
