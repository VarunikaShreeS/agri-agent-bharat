# KrishiChain Phase 1 Live Agent Verification Runs

**Model:** `gemini-2.5-flash`

## Case A: Tomato with Early Blight Photo (English)

- **Inputs:** Crop: `Tomato`, District: `Nashik, Maharashtra`, Qty: `20.0 qtl`, Language: `English`
- **Image:** `tests/samples/tomato_early_blight.jpg`
- **Diagnosis Result:** `{"image_available": true, "crop": "Tomato", "disease": "early_blight", "severity": 0.2, "confidence": 0.95, "visible_symptoms": "Multiple dark brown lesions with concentric rings and yellow halos are present on the tomato leaf.", "low_confidence": false}`
- **Plan Result:** `{"ok": true, "crop": "Tomato", "quantity_quintals": 20, "home": "Nashik, Maharashtra", "best": {"market": "Vashi (Navi Mumbai) APMC", "district": "Thane", "state": "Maharashtra", "distance_km": 171.2, "price_per_quintal": 2250, "trend_7d_pct": 15.4, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 45000, "freight": 6848.0, "commission": 900.0, "loading": 300.0, "spoilage_loss": 1926.0, "net": 35026.0}, "local_baseline": {"market": "Nashik APMC", "district": "Nashik", "state": "Maharashtra", "distance_km": 0.0, "price_per_quintal": 1640, "trend_7d_pct": 13.1, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 32800, "freight": 0.0, "commission": 656.0, "loading": 300.0, "spoilage_loss": 0.0, "net": 31844.0}, "top_options": [{"market": "Vashi (Navi Mumbai) APMC", "district": "Thane", "state": "Maharashtra", "distance_km": 171.2, "price_per_quintal": 2250, "trend_7d_pct": 15.4, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 45000, "freight": 6848.0, "commission": 900.0, "loading": 300.0, "spoilage_loss": 1926.0, "net": 35026.0}, {"market": "Nashik APMC", "district": "Nashik", "state": "Maharashtra", "distance_km": 0.0, "price_per_quintal": 1640, "trend_7d_pct": 13.1, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 32800, "freight": 0.0, "commission": 656.0, "loading": 300.0, "spoilage_loss": 0.0, "net": 31844.0}, {"market": "Pune APMC", "district": "Pune", "state": "Maharashtra", "distance_km": 213.7, "price_per_quintal": 1900, "trend_7d_pct": 8.6, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 38000, "freight": 8548.0, "commission": 760.0, "loading": 300.0, "spoilage_loss": 2030.0, "net": 26362.0}], "uplift_inr_vs_local": 3182.0, "uplift_pct_vs_local": 10.0, "timing": {"action": "treat_and_hold_short", "reason": "Low severity and prices up 15.4% over 7 days; treat now and sell within 3-5 days if produce stays sound."}, "assumptions": {"road_factor": 1.3, "freight_rs_per_qtl_km": 2.0, "commission_pct": 2.0}, "data_source": "seeded_snapshot", "data_as_of": "2026-10-01"}`
- **Errors:** `[]`

### Tool Trace

| Step | Tool | Latency (s) | Status | Arguments | Result Preview |
|---|---|---|---|---|---|
| 1 | `analyze_leaf_image` | 4.82 | `ok` | `{'crop': 'Tomato'}` | {"image_available": true, "crop": "Tomato", "disease": "early_blight", "severity": 0.2, "confidence": 0.95, "visible_symptoms": "Multiple dark brown lesions with concentric rings and yellow halos are present on the tomato leaf.", "low_confidence": false} |
| 2 | `lookup_remedy` | 0.0 | `ok` | `{'crop': 'Tomato', 'disease': 'early_blight'}` | {"found": true, "crop": "tomato", "disease_key": "early_blight", "name": "Early blight (Alternaria solani)", "symptoms": "Dark brown concentric-ring spots ('target board') on older leaves, yellowing around spots.", "organic": ["Remove and destroy affected lower leaves", "Spray Trichoderma viride 5 g/L or neem oil 3 ml/L + sticky spreader", "Copper oxychloride 3 g/L (also accepted in organic-leaning plans)"], "chemical": [{"active": "Mancozeb 75% WP", "dose": "2.5 g per litre water", "interval_days": 10}, {"active": "Chlorothalonil 75% WP", "dose": "2 g per litre water", "interval_days": 10}],  |
| 3 | `compute_sell_plan` | 0.0 | `ok` | `{'crop': 'Tomato', 'quantity_quintals': 20, 'home_district': 'Nashik', 'severity': 0.2}` | {"ok": true, "crop": "Tomato", "quantity_quintals": 20, "home": "Nashik, Maharashtra", "best": {"market": "Vashi (Navi Mumbai) APMC", "district": "Thane", "state": "Maharashtra", "distance_km": 171.2, "price_per_quintal": 2250, "trend_7d_pct": 15.4, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 45000, "freight": 6848.0, "commission": 900.0, "loading": 300.0, "spoilage_loss": 1926.0, "net": 35026.0}, "local_baseline": {"market": "Nashik APMC", "district": "Nashik", "state": "Maharashtra", "distance_km": 0.0, "price_per_quintal": 1640, "trend_7d_pct": 13.1, "source": "seeded_snaps |

### Advisory Text

```text
Hello there! Don't worry, we can help you with your tomato crop.

### Diagnosis
Based on the image you sent and your description of dark spots with yellow halos on the leaves, your tomato plants are showing signs of **Early Blight (Alternaria solani)**. The severity is currently low, at about 20%.

### Treatment

Here are some ways to treat Early Blight, with organic options listed first:

**Organic Options:**
*   **Remove affected leaves:** Carefully remove and destroy any lower leaves that are showing symptoms.
*   **Organic Sprays:** You can spray your plants with **Trichoderma viride** at a dose of 5 grams per litre of water, or **neem oil** at 3 ml per litre of water, along with a sticky spreader.
*   **Copper Oxychloride:** Another option, also accepted in organic-leaning plans, is to spray **Copper oxychloride** at 3 grams per litre of water.

**Chemical Options:**
*   **Mancozeb 75% WP:** Spray 2.5 grams per litre of water. Repeat every 10 days.
*   **Chlorothalonil 75% WP:** Spray 2 grams per litre of water. Repeat every 10 days.

**Important:** Always follow the label dose, wear protective gear, and confirm with your local Krishi Vigyan Kendra (KVK).
**Pre-Harvest Interval (PHI):** After spraying, you must wait **7 days** before harvesting your tomatoes.

### Where to Sell

We've looked at the best places to sell your 20 quintals of tomatoes. The prices are a **seeded snapshot as of 2026-10-01**.

*   **Best Market:** The best option for you is **Vashi (Navi Mumbai) APMC in Thane, Maharashtra**.
    *   **Net Earnings:** You could earn approximately **₹35026** after accounting for transport, commission, and spoilage.
    *   **Uplift vs. Local Mandi:** This is an uplift of **₹3182**, or 10% more, compared to selling at your local Nashik APMC.

### Next 3 Days

Given the low severity of the disease and that tomato prices have been trending up by 15.4% over the last 7 days, we recommend you **treat your crop now and plan to sell within the next 3-5 days** if your produce remains in good condition.

We hope this helps you get the best outcome for your crop!
```

---

## Case B: Tomato without Photo - Text Symptoms Only (English)

- **Inputs:** Crop: `Tomato`, District: `Nashik, Maharashtra`, Qty: `20.0 qtl`, Language: `English`
- **Image:** `None`
- **Diagnosis Result:** `null`
- **Plan Result:** `{"ok": true, "crop": "Tomato", "quantity_quintals": 20, "home": "Nashik, Maharashtra", "best": {"market": "Vashi (Navi Mumbai) APMC", "district": "Thane", "state": "Maharashtra", "distance_km": 171.2, "price_per_quintal": 2250, "trend_7d_pct": 15.4, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 45000, "freight": 6848.0, "commission": 900.0, "loading": 300.0, "spoilage_loss": 1926.0, "net": 35026.0}, "local_baseline": {"market": "Nashik APMC", "district": "Nashik", "state": "Maharashtra", "distance_km": 0.0, "price_per_quintal": 1640, "trend_7d_pct": 13.1, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 32800, "freight": 0.0, "commission": 656.0, "loading": 300.0, "spoilage_loss": 0.0, "net": 31844.0}, "top_options": [{"market": "Vashi (Navi Mumbai) APMC", "district": "Thane", "state": "Maharashtra", "distance_km": 171.2, "price_per_quintal": 2250, "trend_7d_pct": 15.4, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 45000, "freight": 6848.0, "commission": 900.0, "loading": 300.0, "spoilage_loss": 1926.0, "net": 35026.0}, {"market": "Nashik APMC", "district": "Nashik", "state": "Maharashtra", "distance_km": 0.0, "price_per_quintal": 1640, "trend_7d_pct": 13.1, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 32800, "freight": 0.0, "commission": 656.0, "loading": 300.0, "spoilage_loss": 0.0, "net": 31844.0}, {"market": "Pune APMC", "district": "Pune", "state": "Maharashtra", "distance_km": 213.7, "price_per_quintal": 1900, "trend_7d_pct": 8.6, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 38000, "freight": 8548.0, "commission": 760.0, "loading": 300.0, "spoilage_loss": 2030.0, "net": 26362.0}], "uplift_inr_vs_local": 3182.0, "uplift_pct_vs_local": 10.0, "timing": {"action": "sell_at_best_market", "reason": "Moderate/unclear signals; sell at the best net-return market and treat remaining crop."}, "assumptions": {"road_factor": 1.3, "freight_rs_per_qtl_km": 2.0, "commission_pct": 2.0}, "data_source": "seeded_snapshot", "data_as_of": "2026-10-01"}`
- **Errors:** `[]`

### Tool Trace

| Step | Tool | Latency (s) | Status | Arguments | Result Preview |
|---|---|---|---|---|---|
| 1 | `lookup_remedy` | 0.0 | `ok` | `{'crop': 'Tomato', 'disease': 'Early Blight'}` | {"found": true, "crop": "tomato", "disease_key": "early_blight", "name": "Early blight (Alternaria solani)", "symptoms": "Dark brown concentric-ring spots ('target board') on older leaves, yellowing around spots.", "organic": ["Remove and destroy affected lower leaves", "Spray Trichoderma viride 5 g/L or neem oil 3 ml/L + sticky spreader", "Copper oxychloride 3 g/L (also accepted in organic-leaning plans)"], "chemical": [{"active": "Mancozeb 75% WP", "dose": "2.5 g per litre water", "interval_days": 10}, {"active": "Chlorothalonil 75% WP", "dose": "2 g per litre water", "interval_days": 10}],  |
| 2 | `compute_sell_plan` | 0.0 | `ok` | `{'crop': 'Tomato', 'quantity_quintals': 20, 'home_district': 'Nashik, Maharashtra', 'severity': 0.3}` | {"ok": true, "crop": "Tomato", "quantity_quintals": 20, "home": "Nashik, Maharashtra", "best": {"market": "Vashi (Navi Mumbai) APMC", "district": "Thane", "state": "Maharashtra", "distance_km": 171.2, "price_per_quintal": 2250, "trend_7d_pct": 15.4, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 45000, "freight": 6848.0, "commission": 900.0, "loading": 300.0, "spoilage_loss": 1926.0, "net": 35026.0}, "local_baseline": {"market": "Nashik APMC", "district": "Nashik", "state": "Maharashtra", "distance_km": 0.0, "price_per_quintal": 1640, "trend_7d_pct": 13.1, "source": "seeded_snaps |

### Advisory Text

```text
Here is your KrishiChain advisory:

**Diagnosis**
Based on your description of "dark rings on lower leaves, yellowing" on your tomato plants, it sounds like your crop is affected by **Early Blight (Alternaria solani)**.

**Treatment**

Here are some ways to treat Early Blight, with organic options listed first:

*   **Organic Options:**
    *   Carefully remove and destroy any affected lower leaves to prevent the disease from spreading.
    *   Spray your plants with **Trichoderma viride** at a dose of 5 grams per liter of water, or use **neem oil** at 3 ml per liter of water mixed with a sticky spreader.
    *   You can also use **Copper oxychloride** at 3 grams per liter of water, which is often accepted in organic-leaning farming plans.
*   **Chemical Options:**
    *   You can spray with **Mancozeb 75% WP** at a dose of 2.5 grams per liter of water.
    *   Alternatively, use **Chlorothalonil 75% WP** at a dose of 2 grams per liter of water.
    *   For both chemical options, repeat the spray every 10 days.

**Important:** For all treatments, the **pre-harvest interval (PHI)** is 7 days. This means you should not harvest your tomatoes for at least 7 days after the last spray. Always follow the label instructions for doses, wear protective gear, and confirm with your local Krishi Vigyan Kendra (KVK) for specific advice in your area.

**Where to Sell**

Based on our analysis (data as of 2026-10-01, from a seeded snapshot), here is the best plan for selling your 20.0 quintals of tomatoes:

*   **Best Market:** The **Vashi (Navi Mumbai) APMC** in Thane district, Maharashtra, offers the best net return.
    *   **Net Rupees:** You could earn approximately **₹35,026**.
    *   This is an **uplift of ₹3,182 (10%)** compared to selling at your local Nashik APMC.
    *   The price per quintal at Vashi is ₹2,250.
    *   The distance to Vashi is about 171.2 km.
*   **Local Option:** If you prefer to sell locally, the Nashik APMC offers a net return of approximately ₹31,844 with a price of ₹1,640 per quintal.

**Next 3 Days**

Given the moderate signals, it is advisable to **sell your produce at the best net-return market (Vashi APMC)** while continuing to treat the remaining crop for Early Blight. Focus on applying the chosen treatment method (organic or chemical) as soon as possible to control the disease.
```

---

## Case C: Blurry / Non-leaf Photo - Guardrail Check (English)

- **Inputs:** Crop: `Tomato`, District: `Nashik, Maharashtra`, Qty: `20.0 qtl`, Language: `English`
- **Image:** `tests/samples/blurry_or_nonleaf.jpg`
- **Diagnosis Result:** `{"image_available": true, "crop": "Tomato", "disease": "unknown", "severity": 0.0, "confidence": 1.0, "visible_symptoms": "The image provided is of a blurry kitchen interior, not a tomato leaf, so no plant symptoms are visible.", "low_confidence": true, "guardrail": "Confidence too low. Do NOT prescribe a chemical. Ask the farmer for a clearer, close-up, well-lit photo of an affected leaf (top and underside) and suggest visiting the nearest KVK."}`
- **Plan Result:** `null`
- **Errors:** `[]`

### Tool Trace

| Step | Tool | Latency (s) | Status | Arguments | Result Preview |
|---|---|---|---|---|---|
| 1 | `analyze_leaf_image` | 3.69 | `ok` | `{'crop': 'Tomato'}` | {"image_available": true, "crop": "Tomato", "disease": "unknown", "severity": 0.0, "confidence": 1.0, "visible_symptoms": "The image provided is of a blurry kitchen interior, not a tomato leaf, so no plant symptoms are visible.", "low_confidence": true, "guardrail": "Confidence too low. Do NOT prescribe a chemical. Ask the farmer for a clearer, close-up, well-lit photo of an affected leaf (top and underside) and suggest visiting the nearest KVK."} |

### Advisory Text

```text
I am sorry, but the photo you uploaded appears to be of a kitchen interior and not a tomato leaf. I need a clear, close-up, well-lit photo of an affected leaf (both top and underside) to diagnose the disease accurately.

Please upload a better photo. In the meantime, I recommend you visit your nearest Krishi Vigyan Kendra (KVK) for an in-person diagnosis and advice.
```

---

## Case D: Unknown District 'Atlantis' - Recovery Check (English)

- **Inputs:** Crop: `Tomato`, District: `Atlantis`, Qty: `20.0 qtl`, Language: `English`
- **Image:** `None`
- **Diagnosis Result:** `null`
- **Plan Result:** `null`
- **Errors:** `[]`

### Tool Trace

| Step | Tool | Latency (s) | Status | Arguments | Result Preview |
|---|---|---|---|---|---|
| 1 | `lookup_remedy` | 0.0 | `ok` | `{'crop': 'Tomato', 'disease': 'Early Blight'}` | {"found": true, "crop": "tomato", "disease_key": "early_blight", "name": "Early blight (Alternaria solani)", "symptoms": "Dark brown concentric-ring spots ('target board') on older leaves, yellowing around spots.", "organic": ["Remove and destroy affected lower leaves", "Spray Trichoderma viride 5 g/L or neem oil 3 ml/L + sticky spreader", "Copper oxychloride 3 g/L (also accepted in organic-leaning plans)"], "chemical": [{"active": "Mancozeb 75% WP", "dose": "2.5 g per litre water", "interval_days": 10}, {"active": "Chlorothalonil 75% WP", "dose": "2 g per litre water", "interval_days": 10}],  |
| 2 | `compute_sell_plan` | 0.0 | `ok` | `{'crop': 'Tomato', 'quantity_quintals': 20, 'home_district': 'Atlantis', 'severity': 0.3}` | {"ok": false, "error": "Could not locate 'Atlantis'.", "known_districts": ["Ahmednagar", "Aurangabad", "Chennai", "Coimbatore", "Dhule", "Krishnagiri", "Nashik", "Pune", "Salem", "Thane", "Vellore"]} |

### Advisory Text

```text
It looks like your tomato plants might be suffering from **Early Blight (Alternaria solani)**, based on your description of dark rings and spots on the leaves.

Here's what you can do:

**Diagnosis**
Your tomato leaves show symptoms consistent with Early Blight, characterized by dark brown spots with concentric rings, often described as "target board" spots, primarily on older leaves. Yellowing may also occur around these spots.

**Treatment**

**Organic Options:**
*   **Remove affected leaves:** Carefully remove and destroy any lower leaves that show symptoms of the disease.
*   **Organic Spray:** You can spray with *Trichoderma viride* at 5 grams per liter of water, or use neem oil at 3 ml per liter of water, along with a sticky spreader.
*   **Copper Oxychloride:** Copper oxychloride at 3 grams per liter is also an option that is accepted in many organic-leaning farming practices.

**Chemical Options:**
*   **Mancozeb 75% WP:** Apply 2.5 grams per liter of water.
*   **Chlorothalonil 75% WP:** Apply 2 grams per liter of water.
*   **Spray Interval:** For both chemical options, spray every 10 days.
*   **Pre-Harvest Interval (PHI):** Please wait 7 days after spraying any of these treatments before harvesting your tomatoes.
*   **Safety:** Always follow the label instructions for dosage, wear protective gear, and observe the pre-harvest interval. It's always a good idea to confirm with your local Krishi Vigyan Kendra (KVK) for specific advice in your area.

**Cultural Practices:**
*   Avoid overhead irrigation to reduce leaf wetness.
*   Stake your plants to improve airflow around them.
*   Next season, rotate your crops and avoid planting tomatoes or other solanaceous crops (like potatoes, peppers, or eggplants) in the same spot.

**Where to sell**
I couldn't find information for the district "Atlantis". To help you find the best market for your 20 quintals of tomatoes, please provide a valid district from the following list: Ahmednagar, Aurangabad, Chennai, Coimbatore, Dhule, Krishnagiri, Nashik, Pune, Salem, Thane, Vellore.

**Next 3 days**
Focus on implementing the recommended treatments for Early Blight. If you choose to spray, ensure you have the necessary products and follow the instructions carefully. Also, please provide a valid district so I can help you with selling advice.
```

---

## Case E: Tomato with Leaf Curl Photo (Hindi)

- **Inputs:** Crop: `Tomato`, District: `Nashik, Maharashtra`, Qty: `20.0 qtl`, Language: `Hindi`
- **Image:** `tests/samples/tomato_leaf_curl.jpg`
- **Diagnosis Result:** `{"image_available": true, "crop": "Tomato", "disease": "leaf_curl_virus", "severity": 0.75, "confidence": 0.9, "visible_symptoms": "Leaves show severe yellowing with interveinal chlorosis, significant upward curling, and crinkling.", "low_confidence": false}`
- **Plan Result:** `{"ok": true, "crop": "Tomato", "quantity_quintals": 20, "home": "Nashik, Maharashtra", "best": {"market": "Vashi (Navi Mumbai) APMC", "district": "Thane", "state": "Maharashtra", "distance_km": 171.2, "price_per_quintal": 2250, "trend_7d_pct": 15.4, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 45000, "freight": 6848.0, "commission": 900.0, "loading": 300.0, "spoilage_loss": 1926.0, "net": 35026.0}, "local_baseline": {"market": "Nashik APMC", "district": "Nashik", "state": "Maharashtra", "distance_km": 0.0, "price_per_quintal": 1640, "trend_7d_pct": 13.1, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 32800, "freight": 0.0, "commission": 656.0, "loading": 300.0, "spoilage_loss": 0.0, "net": 31844.0}, "top_options": [{"market": "Vashi (Navi Mumbai) APMC", "district": "Thane", "state": "Maharashtra", "distance_km": 171.2, "price_per_quintal": 2250, "trend_7d_pct": 15.4, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 45000, "freight": 6848.0, "commission": 900.0, "loading": 300.0, "spoilage_loss": 1926.0, "net": 35026.0}, {"market": "Nashik APMC", "district": "Nashik", "state": "Maharashtra", "distance_km": 0.0, "price_per_quintal": 1640, "trend_7d_pct": 13.1, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 32800, "freight": 0.0, "commission": 656.0, "loading": 300.0, "spoilage_loss": 0.0, "net": 31844.0}, {"market": "Pune APMC", "district": "Pune", "state": "Maharashtra", "distance_km": 213.7, "price_per_quintal": 1900, "trend_7d_pct": 8.6, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 38000, "freight": 8548.0, "commission": 760.0, "loading": 300.0, "spoilage_loss": 2030.0, "net": 26362.0}], "uplift_inr_vs_local": 3182.0, "uplift_pct_vs_local": 10.0, "timing": {"action": "sell_now", "reason": "Infection severity 75% is high; harvest marketable produce now rather than wait."}, "assumptions": {"road_factor": 1.3, "freight_rs_per_qtl_km": 2.0, "commission_pct": 2.0}, "data_source": "seeded_snapshot", "data_as_of": "2026-10-01"}`
- **Errors:** `[]`

### Tool Trace

| Step | Tool | Latency (s) | Status | Arguments | Result Preview |
|---|---|---|---|---|---|
| 1 | `analyze_leaf_image` | 5.52 | `ok` | `{'crop': 'Tomato'}` | {"image_available": true, "crop": "Tomato", "disease": "leaf_curl_virus", "severity": 0.75, "confidence": 0.9, "visible_symptoms": "Leaves show severe yellowing with interveinal chlorosis, significant upward curling, and crinkling.", "low_confidence": false} |
| 2 | `lookup_remedy` | 0.0 | `ok` | `{'crop': 'Tomato', 'disease': 'leaf_curl_virus'}` | {"found": true, "crop": "tomato", "disease_key": "leaf_curl_virus", "name": "Tomato leaf curl virus (whitefly-transmitted)", "symptoms": "Upward curling and crinkling of leaves, yellowing, stunted plants; whiteflies under leaves.", "organic": ["Yellow sticky traps (about 10 per 1000 sq m)", "Neem oil 3-5 ml/L or neem seed kernel extract 5% against whitefly", "Uproot and destroy severely infected plants"], "chemical": [{"active": "Imidacloprid 17.8% SL (vector control only; virus itself cannot be cured)", "dose": "0.3 ml per litre water", "interval_days": 14}], "cultural": ["Border crop of maiz |
| 3 | `compute_sell_plan` | 0.0 | `ok` | `{'crop': 'Tomato', 'quantity_quintals': 20, 'home_district': 'Nashik', 'severity': 0.75}` | {"ok": true, "crop": "Tomato", "quantity_quintals": 20, "home": "Nashik, Maharashtra", "best": {"market": "Vashi (Navi Mumbai) APMC", "district": "Thane", "state": "Maharashtra", "distance_km": 171.2, "price_per_quintal": 2250, "trend_7d_pct": 15.4, "source": "seeded_snapshot", "as_of": "2026-10-01", "gross": 45000, "freight": 6848.0, "commission": 900.0, "loading": 300.0, "spoilage_loss": 1926.0, "net": 35026.0}, "local_baseline": {"market": "Nashik APMC", "district": "Nashik", "state": "Maharashtra", "distance_km": 0.0, "price_per_quintal": 1640, "trend_7d_pct": 13.1, "source": "seeded_snaps |

### Advisory Text

```text
नमस्ते किसान भाई,

आपकी फसल और पत्तियों की तस्वीर के आधार पर, यहाँ आपके लिए सलाह है:

**निदान**
आपकी टमाटर की पत्तियों में 'टोमैटो लीफ कर्ल वायरस' (Tomato leaf curl virus) का संक्रमण दिख रहा है। पत्तियों का ऊपर की ओर मुड़ना, सिकुड़ना और पीला पड़ना इसके मुख्य लक्षण हैं। यह वायरस सफेद मक्खी द्वारा फैलता है। संक्रमण की गंभीरता 75% है।

**उपचार**

यह वायरस सफेद मक्खी द्वारा फैलता है, इसलिए सफेद मक्खी को नियंत्रित करना महत्वपूर्ण है।

**जैविक उपाय:**
*   **पीले चिपचिपे जाल:** अपने खेत में प्रति 1000 वर्ग मीटर में लगभग 10 पीले चिपचिपे जाल लगाएं। ये सफेद मक्खियों को आकर्षित करके फंसाते हैं।
*   **नीम का तेल:** सफेद मक्खी के नियंत्रण के लिए 3-5 मिलीलीटर नीम का तेल प्रति लीटर पानी में मिलाकर या 5% नीम की खली का अर्क स्प्रे करें।
*   **संक्रमित पौधों को हटाना:** जो पौधे गंभीर रूप से संक्रमित हैं, उन्हें तुरंत उखाड़कर नष्ट कर दें ताकि संक्रमण अन्य पौधों में न फैले।

**सांस्कृतिक उपाय:**
*   **बॉर्डर फसल:** खेत के चारों ओर मक्का या ज्वार की फसल लगाएं। यह सफेद मक्खी के लिए एक बाधा का काम करेगी।
*   **खरपतवार नियंत्रण:** उन खरपतवारों को नियंत्रित करें जो सफेद मक्खी के लिए मेजबान का काम करते हैं।
*   **अगले मौसम के लिए:** अगले बुवाई के मौसम में वायरस-प्रतिरोधी किस्मों का उपयोग करें।

**रासायनिक उपाय (केवल वाहक नियंत्रण के लिए):**
*   **इमिडाक्लोप्रिड 17.8% SL:** सफेद मक्खी के नियंत्रण के लिए 0.3 मिलीलीटर प्रति लीटर पानी में मिलाकर स्प्रे करें। इसे हर 14 दिन में दोहराया जा सकता है।
*   **कटाई-पूर्व अंतराल (PHI):** रासायनिक छिड़काव के बाद कम से कम 7 दिनों तक टमाटर की कटाई न करें।
*   **सुरक्षा:** हमेशा लेबल पर दिए गए निर्देशों का पालन करें, सुरक्षात्मक गियर पहनें और स्थानीय कृषि विज्ञान केंद्र (KVK) से पुष्टि करें।

**टमाटर कहाँ बेचें**

आपकी 20 क्विंटल टमाटर की फसल के लिए, यहाँ सबसे अच्छे बिक्री विकल्प दिए गए हैं:

*   **सबसे अच्छा बाज़ार:** वाशी (नवी मुंबई) APMC, जिला ठाणे, महाराष्ट्र।
    *   **शुद्ध आय:** आपको लगभग 35,026 रुपये मिल सकते हैं।
    *   **स्थानीय मंडी से लाभ:** यह आपके स्थानीय नासिक APMC की तुलना में लगभग 3,182 रुपये (या 10%) अधिक है।
    *   **प्रति क्विंटल कीमत:** यहाँ आपको लगभग 2,250 रुपये प्रति क्विंटल मिल सकते हैं।
    *   **डेटा स्रोत:** यह जानकारी 2026-10-01 के सीडेड स्नैपशॉट पर आधारित है।

*   **स्थानीय बाज़ार (तुलना के लिए):** नासिक APMC, जिला नासिक।
    *   **शुद्ध आय:** यहाँ आपको लगभग 31,844 रुपये मिल सकते हैं।
    *   **प्रति क्विंटल कीमत:** यहाँ आपको लगभग 1,640 रुपये प्रति क्विंटल मिल सकते हैं।

**बेचने का सही समय:**
संक्रमण की गंभीरता 75% अधिक है, इसलिए सलाह दी जाती है कि आप अभी अपनी विपणन योग्य उपज की कटाई करें और बेच दें, बजाय इसके कि आप इंतजार करें।

**अगले 3 दिन**
1.  तुरंत पीले चिपचिपे जाल लगाएं और नीम के तेल का छिड़काव करें।
2.  गंभीर रूप से संक्रमित पौधों को उखाड़कर नष्ट कर दें।
3.  अपनी फसल को वाशी (नवी मुंबई) APMC, ठाणे में बेचने की योजना बनाएं ताकि आपको बेहतर दाम मिल सकें।
4.  यदि आवश्यक हो, तो सफेद मक्खी के नियंत्रण के लिए रासायनिक उपाय (इमिडाक्लोप्रिड) का उपयोग करें, और कटाई-पूर्व अंतराल का ध्यान रखें।

शुभकामनाएं!

```

---
