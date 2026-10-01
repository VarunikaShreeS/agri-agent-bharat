# KrishiChain Bharat — 2:30 Minute Hackathon Video Script

**Theme:** "Real Profit Over Headline Prices — An Autonomous AI Plant Doctor & Mandi Logistics Agent for Bharat"  
**Target Duration:** 2 minutes 30 seconds

---

### [0:00 – 0:30] The Smallholder Farmer's Dilemma
- **Visual:** Farmer in Nashik looking at spotted tomato leaves and checking local mandi prices on a phone.
- **Narrator:** *"Every season, Indian smallholders face a double hazard: crop disease reduces marketable yield, and local mandis offer rock-bottom prices. A farmer might see a ₹2,750 headline price 200 km away in Panvel versus ₹2,100 locally in Nashik. But after diesel, loading, commission, and spoilage—will they actually make more money? Meet KrishiChain Bharat."*

---

### [0:30 – 1:00] Autonomous Perception & Diagnosis
- **Visual:** Screen recording of KrishiChain UI. Farmer uploads a leaf photo (`tomato_early_blight.jpg`) and speaks in Hindi: *"पत्तियों पर कत्थई धब्बे और पीले छल्ले हैं, क्या छिड़कें और कहाँ बेचें?"*
- **Narrator:** *"The farmer uploads a leaf photo and speaks in their regional language. KrishiChain's Gemini 2.5 vision pipeline diagnoses Early Blight (Alternaria solani) at 95% confidence with 15% severity, immediately retrieving TNAU-verified organic treatments before chemical options."*

---

### [1:00 – 1:30] Deterministic Mandi Economics & Tool Trace
- **Visual:** UI expands the Hero Metric Card and Agent Trace panel.
- **Narrator:** *"Unlike generic chatbots that hallucinate numbers, KrishiChain uses real tool calling. It calls our Mandi Price API across Maharashtra, computes 229 km road logistics, and calculates net realization: ₹55,000 gross minus ₹9,188 freight, ₹1,100 commission, ₹300 loading, and ₹3,158 spoilage—yielding ₹41,254 net, delivering a real +₹394 gain over local Ghoti mandi."*

---

### [1:30 – 2:00] The Guardrail & Regional Voice Output
- **Visual:** Show two key features:
  1. Testing a blurry photo (`blurry_or_nonleaf.jpg`) where the Low Confidence Guardrail triggers, blocking chemical advice and referring to KVK.
  2. Clicking the audio player to hear the 5-sentence spoken audio advisory in Hindi and Tamil.
- **Narrator:** *"Safety is built into code, not prompts. Low-confidence photos instantly block chemical prescriptions. And because literacy should never be a barrier, KrishiChain speaks the complete 5-sentence advisory back to the farmer in Hindi or Tamil."*

---

### [2:00 – 2:30] Demo Mode, Scalability & Conclusion
- **Visual:** Toggling DEMO MODE in the sidebar to show offline resiliency, and showing the clean architecture.
- **Narrator:** *"Built with Gemini 2.5 Flash, real Agmarknet data adapters, and offline fallback demo mode, KrishiChain empowers Bharat's 140 million farmers to protect their crops and maximize take-home earnings. KrishiChain: Real agronomy, real numbers, real impact."*
