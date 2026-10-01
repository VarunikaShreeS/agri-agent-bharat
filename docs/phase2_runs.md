# KrishiChain Phase 2 Verification Runs — Real Mandi Data & Expanded KB

**Model:** `gemini-2.5-flash`

**Mandi Provider Chain:** Mandi Price API (Live) ➔ data.gov.in (Optional) ➔ Frozen Real Snapshot ➔ Seed Fallback

## Case A: Tomato with Early Blight Photo (English) - Live/Frozen Provider Chain

- **Inputs:** Crop: `Tomato`, District: `Nashik, Maharashtra`, Qty: `20.0 qtl`, Language: `English`
- **Image:** `tests/samples/tomato_early_blight.jpg`
- **Diagnosis Result:** `{"image_available": true, "crop": "Tomato", "disease": "early_blight", "severity": 0.15, "confidence": 0.95, "visible_symptoms": "Multiple dark brown lesions with concentric rings (bullseye pattern) and yellow halos are visible on the tomato leaves.", "low_confidence": false}`
- **Plan Result:** `{"ok": true, "crop": "Tomato", "quantity_quintals": 20, "home": "Nashik, Maharashtra", "best": {"market": "APMC Panvel", "district": "Raigad", "state": "Maharashtra", "distance_km": 229.7, "price_per_quintal": 3500.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-22", "gross": 70000.0, "freight": 9188.0, "commission": 1400.0, "loading": 300.0, "spoilage_loss": 4020.0, "net": 55092.0}, "local_baseline": {"market": "APMC Ghoti", "district": "Nashik", "state": "Maharashtra", "distance_km": 0.0, "price_per_quintal": 2100.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-24", "gross": 42000.0, "freight": 0.0, "commission": 840.0, "loading": 300.0, "spoilage_loss": 0.0, "net": 40860.0}, "top_options": [{"market": "APMC Panvel", "district": "Raigad", "state": "Maharashtra", "distance_km": 229.7, "price_per_quintal": 3500.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-22", "gross": 70000.0, "freight": 9188.0, "commission": 1400.0, "loading": 300.0, "spoilage_loss": 4020.0, "net": 55092.0}, {"market": "APMC Panvel", "district": "Raigad", "state": "Maharashtra", "distance_km": 229.7, "price_per_quintal": 2750.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-24", "gross": 55000.0, "freight": 9188.0, "commission": 1100.0, "loading": 300.0, "spoilage_loss": 3158.0, "net": 41254.0}, {"market": "APMC Panvel", "district": "Raigad", "state": "Maharashtra", "distance_km": 229.7, "price_per_quintal": 2750.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-20", "gross": 55000.0, "freight": 9188.0, "commission": 1100.0, "loading": 300.0, "spoilage_loss": 3158.0, "net": 41254.0}], "uplift_inr_vs_local": 14232.0, "uplift_pct_vs_local": 34.8, "timing": {"action": "sell_at_best_market", "reason": "No 7-day price trend history available; sell at the best net-return market and treat remaining crop."}, "assumptions": {"road_factor": 1.3, "freight_rs_per_qtl_km": 2.0, "commission_pct": 2.0}, "data_source": "live_mandi_api", "data_as_of": "2026-09-22", "provider_log": [{"provider": "live_mandi_api", "status": "success", "count": 169}]}`
- **Errors:** `[]`

### Tool Trace

| Step | Tool | Latency (s) | Status | Arguments | Result Preview |
|---|---|---|---|---|---|
| 1 | `analyze_leaf_image` | 5.57 | `ok` | `{'crop': 'Tomato'}` | {"image_available": true, "crop": "Tomato", "disease": "early_blight", "severity": 0.15, "confidence": 0.95, "visible_symptoms": "Multiple dark brown lesions with concentric rings (bullseye pattern) and yellow halos are visible on the tomato leaves.", "low_confidence": false} |
| 2 | `lookup_remedy` | 0.0 | `ok` | `{'crop': 'Tomato', 'disease': 'early_bllight'}` | {"found": false, "error": "Disease 'early_bllight' not in KB for Tomato", "valid_diseases": ["bacterial_spot", "early_blight", "fusarium_wilt", "late_blight", "leaf_curl_virus", "powdery_mildew"], "hint": "Pick the closest valid disease from symptoms, or advise consulting the local KVK."} |
| 3 | `lookup_remedy` | 0.0 | `ok` | `{'crop': 'Tomato', 'disease': 'early_blight'}` | {"found": true, "crop": "tomato", "disease_key": "early_blight", "name": "Early blight (Alternaria solani)", "symptoms": "Dark brown concentric-ring spots ('target board') on older leaves, yellowing around spots.", "organic": ["Remove and destroy affected lower leaves", "Spray Trichoderma viride 5 g/L or neem oil 3 ml/L + sticky spreader", "Copper oxychloride 3 g/L (also accepted in organic-leaning plans)"], "chemical": [{"active": "Mancozeb 75% WP", "dose": "2.5 g per litre water", "interval_days": 10}, {"active": "Chlorothalonil 75% WP", "dose": "2 g per litre water", "interval_days": 10}],  |
| 4 | `compute_sell_plan` | 1.8 | `ok` | `{'crop': 'Tomato', 'quantity_quintals': 20, 'home_district': 'Nashik', 'severity': 0.15}` | {"ok": true, "crop": "Tomato", "quantity_quintals": 20, "home": "Nashik, Maharashtra", "best": {"market": "APMC Panvel", "district": "Raigad", "state": "Maharashtra", "distance_km": 229.7, "price_per_quintal": 3500.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-22", "gross": 70000.0, "freight": 9188.0, "commission": 1400.0, "loading": 300.0, "spoilage_loss": 4020.0, "net": 55092.0}, "local_baseline": {"market": "APMC Ghoti", "district": "Nashik", "state": "Maharashtra", "distance_km": 0.0, "price_per_quintal": 2100.0, "trend_7d_pct": null, "source": "live_mandi_api", "a |

### Advisory Text

```text
Hello! Don't worry, we can help you with your tomato crop.

### Diagnosis
Your tomato leaves show symptoms of **Early Blight (Alternaria solani)**, with dark brown spots that have concentric rings (like a bullseye pattern) and yellow halos. The severity is currently low, at about 15%.

### Treatment
Here are the recommended treatments, with organic options first:

**Organic Options:**
*   **Remove affected leaves:** Carefully remove and destroy any lower leaves that show symptoms to prevent the disease from spreading.
*   **Organic Sprays:**
    *   Spray with **Trichoderma viride** at a dose of 5 grams per litre of water.
    *   Alternatively, use **neem oil** at 3 ml per litre of water, mixed with a sticky spreader.
    *   **Copper oxychloride** at 3 grams per litre of water is also an option that is accepted in many organic farming plans.

**Chemical Options:**
*   **Mancozeb 75% WP:** Mix 2.5 grams per litre of water.
*   **Chlorothalonil 75% WP:** Mix 2 grams per litre of water.
*   For both chemical options, spray every 10 days.
*   **Pre-Harvest Interval (PHI):** If you use these chemical sprays, you must wait at least **7 days** after the last spray before harvesting your tomatoes.
*   **Safety:** Always follow the label instructions for the correct dose, wear protective gear, and confirm with your local Krishi Vigyan Kendra (KVK) for specific advice in your area.

### Where to sell
Based on current market data, selling your tomatoes at **APMC Panvel in Raigad, Maharashtra** could give you the best returns.

*   **Best Market:** APMC Panvel, Raigad, Maharashtra.
*   **Net Earnings:** You could earn approximately **₹55,092** for your 20 quintals of tomatoes.
*   **Uplift vs. Local Mandi:** This is an increase of **₹14,232** (or 34.8%) compared to selling at your local APMC Ghoti mandi in Nashik.
*   **Price Information:** The price per quintal at APMC Panvel is ₹3500 (data as of 2026-09-22, from live mandi API). The price at your local APMC Ghoti is ₹2100 per quintal (data as of 2026-09-24, from live mandi API).

### Next 3 days
Since there is no 7-day price trend history available, it is advised to sell your crop at the market that offers the best net return (APMC Panvel) and continue treating the remaining crop to manage the disease.
```

---

## Case B: Tomato without Photo - Text Symptoms Only (English) - Live/Frozen Provider Chain

- **Inputs:** Crop: `Tomato`, District: `Nashik, Maharashtra`, Qty: `20.0 qtl`, Language: `English`
- **Image:** `None`
- **Diagnosis Result:** `null`
- **Plan Result:** `{"ok": true, "crop": "Tomato", "quantity_quintals": 20, "home": "Nashik, Maharashtra", "best": {"market": "APMC Panvel", "district": "Raigad", "state": "Maharashtra", "distance_km": 229.7, "price_per_quintal": 3500.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-22", "gross": 70000.0, "freight": 9188.0, "commission": 1400.0, "loading": 300.0, "spoilage_loss": 4020.0, "net": 55092.0}, "local_baseline": {"market": "APMC Ghoti", "district": "Nashik", "state": "Maharashtra", "distance_km": 0.0, "price_per_quintal": 2100.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-24", "gross": 42000.0, "freight": 0.0, "commission": 840.0, "loading": 300.0, "spoilage_loss": 0.0, "net": 40860.0}, "top_options": [{"market": "APMC Panvel", "district": "Raigad", "state": "Maharashtra", "distance_km": 229.7, "price_per_quintal": 3500.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-22", "gross": 70000.0, "freight": 9188.0, "commission": 1400.0, "loading": 300.0, "spoilage_loss": 4020.0, "net": 55092.0}, {"market": "APMC Panvel", "district": "Raigad", "state": "Maharashtra", "distance_km": 229.7, "price_per_quintal": 2750.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-24", "gross": 55000.0, "freight": 9188.0, "commission": 1100.0, "loading": 300.0, "spoilage_loss": 3158.0, "net": 41254.0}, {"market": "APMC Panvel", "district": "Raigad", "state": "Maharashtra", "distance_km": 229.7, "price_per_quintal": 2750.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-20", "gross": 55000.0, "freight": 9188.0, "commission": 1100.0, "loading": 300.0, "spoilage_loss": 3158.0, "net": 41254.0}], "uplift_inr_vs_local": 14232.0, "uplift_pct_vs_local": 34.8, "timing": {"action": "sell_at_best_market", "reason": "No 7-day price trend history available; sell at the best net-return market and treat remaining crop."}, "assumptions": {"road_factor": 1.3, "freight_rs_per_qtl_km": 2.0, "commission_pct": 2.0}, "data_source": "live_mandi_api", "data_as_of": "2026-09-22", "provider_log": [{"provider": "live_mandi_api", "status": "success", "count": 169}]}`
- **Errors:** `[]`

### Tool Trace

| Step | Tool | Latency (s) | Status | Arguments | Result Preview |
|---|---|---|---|---|---|
| 1 | `lookup_remedy` | 0.0 | `ok` | `{'crop': 'Tomato', 'disease': 'Early Blight'}` | {"found": true, "crop": "tomato", "disease_key": "early_blight", "name": "Early blight (Alternaria solani)", "symptoms": "Dark brown concentric-ring spots ('target board') on older leaves, yellowing around spots.", "organic": ["Remove and destroy affected lower leaves", "Spray Trichoderma viride 5 g/L or neem oil 3 ml/L + sticky spreader", "Copper oxychloride 3 g/L (also accepted in organic-leaning plans)"], "chemical": [{"active": "Mancozeb 75% WP", "dose": "2.5 g per litre water", "interval_days": 10}, {"active": "Chlorothalonil 75% WP", "dose": "2 g per litre water", "interval_days": 10}],  |
| 2 | `compute_sell_plan` | 1.29 | `ok` | `{'crop': 'Tomato', 'quantity_quintals': 20, 'home_district': 'Nashik', 'severity': 0.3}` | {"ok": true, "crop": "Tomato", "quantity_quintals": 20, "home": "Nashik, Maharashtra", "best": {"market": "APMC Panvel", "district": "Raigad", "state": "Maharashtra", "distance_km": 229.7, "price_per_quintal": 3500.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-22", "gross": 70000.0, "freight": 9188.0, "commission": 1400.0, "loading": 300.0, "spoilage_loss": 4020.0, "net": 55092.0}, "local_baseline": {"market": "APMC Ghoti", "district": "Nashik", "state": "Maharashtra", "distance_km": 0.0, "price_per_quintal": 2100.0, "trend_7d_pct": null, "source": "live_mandi_api", "a |

### Advisory Text

```text
Hello! Don't worry, we can help you with your tomato crop.

### Diagnosis
Based on the dark rings on the lower leaves and yellowing you described, your tomato plants are likely suffering from **Early Blight (Alternaria solani)**.

### Treatment
Here are the treatment options, starting with organic methods:

**Organic Options:**
*   **Remove affected leaves:** Carefully remove and destroy any lower leaves showing symptoms to prevent the disease from spreading.
*   **Organic Spray:** You can spray **Trichoderma viride** at 5 grams per liter of water, or **neem oil** at 3 ml per liter of water mixed with a sticky spreader.
*   **Copper Oxychloride:** **Copper oxychloride** at 3 grams per liter of water is also an option that is accepted in many organic-leaning farming plans.

**Chemical Options:**
*   **Mancozeb 75% WP:** Use 2.5 grams per liter of water.
*   **Chlorothalonil 75% WP:** Use 2 grams per liter of water.

For both chemical options, spray every 10 days.

**Important:** For all treatments, the **pre-harvest interval (PHI)** is 7 days. This means you should not harvest your tomatoes for at least 7 days after spraying. Always follow the label dose, wear protective gear, and confirm with your local Krishi Vigyan Kendra (KVK) for best practices in your area.

**Cultural Practices:**
*   Avoid overhead irrigation to keep leaves dry.
*   Stake your plants to improve airflow.
*   Next season, rotate your crops away from other plants in the solanaceous family (like potatoes, peppers, eggplant) to reduce disease recurrence.

### Where to Sell
Based on current market data as of 2026-09-22 (live_mandi_api), the best option for selling your 20 quintals of tomatoes is **APMC Panvel in Raigad district, Maharashtra**.

*   **Net Rupees:** You could earn approximately **₹55,092** after accounting for transport, commission, and spoilage.
*   **Uplift vs. Local Mandi:** This is an estimated **₹14,232 more** (a 34.8% increase) compared to selling at your local APMC Ghoti in Nashik, where the net return is estimated at ₹40,860 (data as of 2026-09-24).
*   **Price per Quintal:** The price at APMC Panvel is ₹3500 per quintal, compared to ₹2100 per quintal at your local mandi.

### Next 3 Days
Since there is no 7-day price trend history available, it is advised to **sell your tomatoes at the best market (APMC Panvel)** and focus on treating the remaining crop to prevent further loss.
```

---

## Case E: Tomato with Leaf Curl Photo (Hindi) - Live/Frozen Provider Chain

- **Inputs:** Crop: `Tomato`, District: `Nashik, Maharashtra`, Qty: `20.0 qtl`, Language: `Hindi`
- **Image:** `tests/samples/tomato_leaf_curl.jpg`
- **Diagnosis Result:** `{"image_available": true, "crop": "Tomato", "disease": "leaf_curl_virus", "severity": 0.8, "confidence": 0.9, "visible_symptoms": "Leaves exhibit severe interveinal chlorosis, appearing yellow with darker green veins, and are significantly curled and distorted.", "low_confidence": false}`
- **Plan Result:** `{"ok": true, "crop": "Tomato", "quantity_quintals": 20, "home": "Nashik, Maharashtra", "best": {"market": "APMC Panvel", "district": "Raigad", "state": "Maharashtra", "distance_km": 229.7, "price_per_quintal": 3500.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-22", "gross": 70000.0, "freight": 9188.0, "commission": 1400.0, "loading": 300.0, "spoilage_loss": 4020.0, "net": 55092.0}, "local_baseline": {"market": "APMC Ghoti", "district": "Nashik", "state": "Maharashtra", "distance_km": 0.0, "price_per_quintal": 2100.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-24", "gross": 42000.0, "freight": 0.0, "commission": 840.0, "loading": 300.0, "spoilage_loss": 0.0, "net": 40860.0}, "top_options": [{"market": "APMC Panvel", "district": "Raigad", "state": "Maharashtra", "distance_km": 229.7, "price_per_quintal": 3500.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-22", "gross": 70000.0, "freight": 9188.0, "commission": 1400.0, "loading": 300.0, "spoilage_loss": 4020.0, "net": 55092.0}, {"market": "APMC Panvel", "district": "Raigad", "state": "Maharashtra", "distance_km": 229.7, "price_per_quintal": 2750.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-24", "gross": 55000.0, "freight": 9188.0, "commission": 1100.0, "loading": 300.0, "spoilage_loss": 3158.0, "net": 41254.0}, {"market": "APMC Panvel", "district": "Raigad", "state": "Maharashtra", "distance_km": 229.7, "price_per_quintal": 2750.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-20", "gross": 55000.0, "freight": 9188.0, "commission": 1100.0, "loading": 300.0, "spoilage_loss": 3158.0, "net": 41254.0}], "uplift_inr_vs_local": 14232.0, "uplift_pct_vs_local": 34.8, "timing": {"action": "sell_now", "reason": "Infection severity 80% is high; harvest marketable produce now rather than wait."}, "assumptions": {"road_factor": 1.3, "freight_rs_per_qtl_km": 2.0, "commission_pct": 2.0}, "data_source": "live_mandi_api", "data_as_of": "2026-09-22", "provider_log": [{"provider": "live_mandi_api", "status": "success", "count": 169}]}`
- **Errors:** `[]`

### Tool Trace

| Step | Tool | Latency (s) | Status | Arguments | Result Preview |
|---|---|---|---|---|---|
| 1 | `analyze_leaf_image` | 9.93 | `ok` | `{'crop': 'Tomato'}` | {"image_available": true, "crop": "Tomato", "disease": "leaf_curl_virus", "severity": 0.8, "confidence": 0.9, "visible_symptoms": "Leaves exhibit severe interveinal chlorosis, appearing yellow with darker green veins, and are significantly curled and distorted.", "low_confidence": false} |
| 2 | `lookup_remedy` | 0.0 | `ok` | `{'crop': 'Tomato', 'disease': 'leaf_curl_virus'}` | {"found": true, "crop": "tomato", "disease_key": "leaf_curl_virus", "name": "Tomato leaf curl virus (whitefly-transmitted)", "symptoms": "Upward curling and crinkling of leaves, yellowing, stunted plants; whiteflies under leaves.", "organic": ["Yellow sticky traps (about 10 per 1000 sq m)", "Neem oil 3-5 ml/L or neem seed kernel extract 5% against whitefly", "Uproot and destroy severely infected plants"], "chemical": [{"active": "Imidacloprid 17.8% SL (vector control only; virus itself cannot be cured)", "dose": "0.3 ml per litre water", "interval_days": 14}], "cultural": ["Border crop of maiz |
| 3 | `compute_sell_plan` | 1.36 | `ok` | `{'crop': 'Tomato', 'quantity_quintals': 20, 'home_district': 'Nashik', 'severity': 0.8}` | {"ok": true, "crop": "Tomato", "quantity_quintals": 20, "home": "Nashik, Maharashtra", "best": {"market": "APMC Panvel", "district": "Raigad", "state": "Maharashtra", "distance_km": 229.7, "price_per_quintal": 3500.0, "trend_7d_pct": null, "source": "live_mandi_api", "as_of": "2026-09-22", "gross": 70000.0, "freight": 9188.0, "commission": 1400.0, "loading": 300.0, "spoilage_loss": 4020.0, "net": 55092.0}, "local_baseline": {"market": "APMC Ghoti", "district": "Nashik", "state": "Maharashtra", "distance_km": 0.0, "price_per_quintal": 2100.0, "trend_7d_pct": null, "source": "live_mandi_api", "a |

### Advisory Text

```text
नमस्ते किसान भाई,

आपकी टमाटर की फसल के लिए यहाँ विस्तृत सलाह दी गई है:

### निदान
आपकी पत्तियों की तस्वीर और आपके बताए गए लक्षणों (पत्तियां ऊपर की तरफ मुड़ रही हैं और पीली पड़ रही हैं) के आधार पर, आपकी टमाटर की फसल में **टमाटर लीफ कर्ल वायरस (Tomato Leaf Curl Virus)** का संक्रमण है। इसकी गंभीरता 80% है। इस वायरस को सफेद मक्खी फैलाती है।

### उपचार
यह वायरस सफेद मक्खी द्वारा फैलता है, इसलिए उपचार का लक्ष्य सफेद मक्खी को नियंत्रित करना है।

**जैविक विकल्प:**
*   **पीले चिपचिपे जाल:** प्रति 1000 वर्ग मीटर में लगभग 10 पीले चिपचिपे जाल लगाएं ताकि सफेद मक्खियों को पकड़ा जा सके।
*   **नीम का तेल:** सफेद मक्खी के नियंत्रण के लिए 3-5 मिलीलीटर नीम का तेल प्रति लीटर पानी में मिलाकर या 5% नीम बीज गिरी का अर्क (Neem Seed Kernel Extract) का छिड़काव करें।
*   **संक्रमित पौधों को हटाना:** जो पौधे गंभीर रूप से संक्रमित हैं, उन्हें उखाड़ कर नष्ट कर दें।

**रासायनिक विकल्प:**
*   **इमिडाक्लोप्रिड 17.8% SL:** सफेद मक्खी के नियंत्रण के लिए 0.3 मिलीलीटर प्रति लीटर पानी में मिलाकर छिड़काव करें। यह केवल सफेद मक्खी को नियंत्रित करेगा; वायरस का कोई सीधा इलाज नहीं है।
*   **छिड़काव अंतराल:** 14 दिन।
*   **फसल कटाई से पहले का अंतराल (PHI):** 7 दिन। इसका मतलब है कि छिड़काव के 7 दिनों के भीतर फसल की कटाई न करें।

**अन्य उपाय:**
*   **बॉर्डर फसल:** खेत के चारों ओर मक्का या ज्वार की फसल लगाएं ताकि सफेद मक्खी के लिए एक बाधा बन सके।
*   **खरपतवार नियंत्रण:** उन खरपतवारों को नियंत्रित करें जो सफेद मक्खी को आश्रय देते हैं।
*   **अगले मौसम के लिए:** अगले मौसम में वायरस प्रतिरोधी किस्मों का उपयोग करें।
*   **सुरक्षा:** लेबल पर दिए गए निर्देशों का पालन करें, सुरक्षात्मक गियर पहनें और स्थानीय कृषि विज्ञान केंद्र (KVK) से पुष्टि करें।

### टमाटर कहाँ बेचें
आपकी 20 क्विंटल टमाटर की फसल बेचने के लिए सबसे अच्छा विकल्प **APMC पनवेल, रायगढ़ जिला, महाराष्ट्र** है।

*   **शुद्ध आय:** आपको लगभग **₹55,092** मिलेंगे।
*   **स्थानीय मंडी से अधिक लाभ:** यह आपकी स्थानीय मंडी (APMC घोटी, नासिक) की तुलना में **₹14,232** (या 34.8%) अधिक है।
*   **कीमत का स्रोत:** यह कीमत **लाइव मंडी एपीआई (live_mandi_api)** से 2026-09-22 तक के आंकड़ों पर आधारित है।
*   **स्थानीय मंडी (APMC घोटी, नासिक):** स्थानीय मंडी में आपको लगभग ₹40,860 की शुद्ध आय होगी (लाइव मंडी एपीआई से 2026-09-24 तक के आंकड़ों पर आधारित)।

### अगले 3 दिन
चूंकि संक्रमण की गंभीरता 80% है, इसलिए सलाह दी जाती है कि आप अपनी फसल को **अभी बेच दें**। इससे आप और अधिक नुकसान से बच सकते हैं। जो टमाटर बेचने योग्य हैं, उन्हें तुरंत काट लें।

शुभकामनाएं!
```

---
