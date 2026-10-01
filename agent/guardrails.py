"""Deterministic safety checks and numeric grounding verification that run in code, not in the LLM."""
import re
from typing import List, Dict, Any

CONFIDENCE_THRESHOLD = 0.6
SEVERE_THRESHOLD = 0.7


def check_diagnosis(d: dict) -> dict:
    if not d:
        return {"status": "ok", "action": "Proceed with symptoms-based advisory."}
    conf = float(d.get("confidence", 0))
    disease = d.get("disease", "unknown")
    if disease in ("unknown", None) or conf < CONFIDENCE_THRESHOLD or d.get("low_confidence"):
        return {
            "status": "low_confidence",
            "action": "Ask the farmer for a clearer, closer, well-lit photo of the affected leaf "
                      "(top and underside). Do NOT recommend chemical pesticides yet.",
        }
    if float(d.get("severity", 0)) >= SEVERE_THRESHOLD:
        return {
            "status": "severe",
            "action": "Recommend contacting the nearest Krishi Vigyan Kendra (KVK) or agriculture "
                      "officer in addition to the remedy.",
        }
    return {"status": "ok", "action": "Proceed. List organic options first."}


def extract_numbers_from_text(text: str) -> List[float]:
    """Extract integer and float numbers from free text while filtering common punctuation/dates."""
    if not text:
        return []
    # Replace dates like 2026-10-01 or 24/09/2026 so they don't count as price numbers
    t = re.sub(r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b", "", text)
    t = re.sub(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b", "", t)
    # Match standalone numbers and currency figures (e.g., ₹41,254, 229.7, 2.5)
    raw_nums = re.findall(r"₹?\s*(\d+(?:,\d{3})*(?:\.\d+)?)", t)
    cleaned = []
    for n in raw_nums:
        n_clean = n.replace(",", "")
        try:
            val = float(n_clean)
            cleaned.append(val)
        except ValueError:
            continue
    return cleaned


def collect_tool_numbers(data: Any) -> set:
    """Recursively collect all numeric values present in tool output payloads."""
    collected = set()
    if isinstance(data, (int, float)):
        collected.add(round(float(data), 1))
        collected.add(round(float(data), 0))
    elif isinstance(data, str):
        # Extract doses / numbers from text values (e.g. '2.5 g', '7 days', '₹3500')
        nums = extract_numbers_from_text(data)
        for n in nums:
            collected.add(round(n, 1))
            collected.add(round(n, 0))
    elif isinstance(data, dict):
        for v in data.values():
            collected.update(collect_tool_numbers(v))
    elif isinstance(data, (list, tuple, set)):
        for item in data:
            collected.update(collect_tool_numbers(item))
    return collected


def verify_numeric_grounding(answer: str, tool_outputs: List[Dict[str, Any]], allowed_inputs: List[float] = None) -> dict:
    """Verifies that key numeric figures (prices, net gains, distances, doses, intervals) in the LLM answer
    are grounded in tool returns or user inputs.
    Returns:
      {
        "verified": bool,
        "grounded_count": int,
        "unverified_figures": list,
        "warning": str | None
      }
    """
    if not answer:
        return {"verified": True, "grounded_count": 0, "unverified_figures": [], "warning": None}

    # Extract numbers in LLM answer
    answer_nums = extract_numbers_from_text(answer)
    
    # Collect all numbers from tool outputs
    valid_numbers = set()
    for tool_res in tool_outputs:
        valid_numbers.update(collect_tool_numbers(tool_res))

    # Add allowed input numbers (quantity, standard default numbers like 3 days, 100%, 7 days)
    if allowed_inputs:
        for inp in allowed_inputs:
            valid_numbers.add(round(float(inp), 1))
            valid_numbers.add(round(float(inp), 0))
    
    # Common conversational numbers to ignore
    ignorable = {0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 10.0, 14.0, 15.0, 20.0, 50.0, 100.0, 1000.0}
    valid_numbers.update(ignorable)

    unverified = []
    grounded_count = 0

    for num in answer_nums:
        r1 = round(num, 1)
        r0 = round(num, 0)
        # Check if number is grounded within 1% margin or exact
        if r1 in valid_numbers or r0 in valid_numbers or any(abs(num - v) < max(1.0, 0.01 * v) for v in valid_numbers if v > 0):
            grounded_count += 1
        else:
            if num > 10 and num not in unverified:
                unverified.append(num)

    verified = len(unverified) == 0
    warning = None if verified else f"Unverified figures in advisory: {unverified}"
    return {
        "verified": verified,
        "grounded_count": grounded_count,
        "unverified_figures": unverified,
        "warning": warning
    }
