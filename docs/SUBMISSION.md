# Bharat Agentic 2026 Hackathon — Official Submission

### 1. Project Information
- **Project Name:** KrishiChain Bharat
- **Team Name / Members:** [Enter Team Members]
- **Domain:** AgriTech & Rural Bharat
- **Repository URL:** https://github.com/VarunikaShreeS/agri-agent-bharat
- **Live Demo URL:** [Streamlit Community Cloud Link Placeholder]
- **Demo Video URL:** [YouTube / Loom 2:30 min Video Link Placeholder]
- **Slide Deck URL:** [Google Slides / PDF Presentation Link Placeholder]

---

### 2. Problem Statement
Indian smallholder farmers lose up to 30% of their annual revenue due to delayed plant disease diagnosis and predatory market pricing. Existing digital tools suffer from three fatal flaws:
1. **Hallucinated figures**: Generic LLMs invent commodity prices, freight costs, and chemical dosages.
2. **Headline trap**: High mandi prices in distant cities often lead to net losses after transport and perishability spoilage are factored in.
3. **Language and literacy barriers**: Complex English text interfaces exclude rural farmers who need conversational regional voice guidance.

---

### 3. Solution Overview
**KrishiChain Bharat** is an autonomous multi-tool agent powered by Google Gemini 2.5 Flash and deterministic agronomic algorithms. A farmer simply uploads a leaf photo and speaks in their regional language (Hindi, Tamil, English). 

The agent autonomously orchestrates:
1. **Vision Pathologist Diagnosis**: Structured JSON disease identification with confidence and severity scoring.
2. **Curated Agronomy Knowledge**: TNAU/ICAR-verified organic remedies, chemical dosages, and Pre-Harvest Intervals (PHI).
3. **Mandi & Logistics Optimizer**: Queries live Agmarknet/Mandi REST APIs across Maharashtra & Tamil Nadu, computes multi-point road distances, and optimizes **Net Realization** (deducting freight, loading, APMC commission, and perishable spoilage).
4. **Safety Guardrails & Audio Advisory**: Blocks ungrounded chemical advice on blurry photos, verifies all figures against tool outputs, and speaks a concise 5-sentence advisory back in the farmer's native tongue.

---

### 4. Technical Architecture & Tech Stack
- **Core LLM & Perception**: Google Gemini 2.5 Flash (`google-genai 2.26.0`) with `AutomaticFunctionCallingConfig` and Pydantic schema constraints.
- **Backend & Tool Engine**: Python 3.13, Pydantic v2, Requests, Pillow, gTTS.
- **Data Infrastructure**: Multi-layer Mandi Provider Chain (Live Mandi Price API $\rightarrow$ data.gov.in $\rightarrow$ Frozen Real Snapshot $\rightarrow$ Seed Snapshot), 48 District Centroid Maps.
- **Frontend & UX**: Streamlit with custom Hero Metric Cards, interactive trace viewers, and voice input recorder.
- **Safety & Verification**: Deterministic guardrails for low confidence (<60%), severe condition escalation (>=70%), and regex-based numeric grounding verifier.
- **Offline Reliability**: `DEMO_MODE=1` recorded cache for zero-downtime offline demonstrations.

---

### 5. Measurable Bharat Impact & Feasibility
- **Economic Uplift**: Increases farmer take-home pay by identifying optimal regional mandis (+₹394 to +₹3,182 net profit per 20 quintals tomato run).
- **Food Loss Reduction**: Perishable spoilage modeling prevents farmers from dispatching over-ripe produce to distant markets.
- **Accessible AI**: Multi-dialect speech recognition and voice response in Hindi and Tamil democratizes AI for non-literate farmers.
