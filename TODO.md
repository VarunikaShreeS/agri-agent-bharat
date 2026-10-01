# KrishiChain Agent — Spec-Driven Build Plan (Bharat Agentic 2026)

**Domain:** AgriTech & Rural Bharat · **Deadline:** submission opens 8:00 PM, closes 9:00 PM, 1 Oct 2026 · **Midpoint check:** 4:00 PM
**Judging:** Agentic Capability · Bharat Impact · Technical Implementation · Innovation · User Experience · Scalability & Feasibility · Demo

## Working rules (the agent must follow these)
1. Work ONE phase at a time. Restate the phase spec, implement, run the acceptance checks, tick the boxes in this file, commit, then STOP and report for confirmation.
2. NEVER fake tool output, metrics, prices or audio. If data is seeded/cached, label it in the UI.
3. The LLM plans and explains; deterministic code computes money, distance, severity thresholds.
4. Every tool: typed signature, docstring, try/except, returns a dict; errors must be recoverable by the agent.
5. Scope cut-line: 2 crops (Tomato, Onion), 3 languages (English, Hindi, Tamil) deep; others best-effort.
6. Small commits with clear messages. Never commit `.env` or API keys.

## Success metrics to demonstrate (shown in demo + README)
- [ ] Real tool-call trace visible in UI (>= 3 distinct tools per run)
- [ ] Net-rupee uplift vs local mandi computed per run
- [ ] Low-confidence guardrail triggers on a bad photo
- [ ] Works end-to-end in English, Hindi, Tamil (text + audio)
- [ ] Offline tests pass; README has architecture diagram and honest limitations

---
## Phase 0 — Setup & merge (target: by 11:30)
**Spec:** Repo cloned, Phase 1 code merged, app boots.
- [x] Clone `https://github.com/VarunikaShreeS/agri-agent-bharat`, create branch `phase1-agent`
- [x] Merge Phase 1 files (agent/, tools/, data/, tests/, app.py, requirements.txt, .env.example, .gitignore); delete old `agent_engine.py`
- [x] Create venv, `pip install -r requirements.txt`, create `.env` from `.env.example`
- [x] **Accept:** `python tests/test_tools.py` prints 6 PASS; `streamlit run app.py` loads with no import errors

## Phase 1 — Core agent verification (target: by 1:00 PM)
**Spec:** Real Gemini function-calling loop works with image + text.
- [ ] Confirm a valid `GEMINI_MODEL` for the key; set in `.env`
- [ ] Run with a real tomato leaf photo: trace shows `analyze_leaf_image` → `lookup_remedy` → `compute_sell_plan`
- [ ] Run with NO image: agent infers disease from text and still produces a sell plan
- [ ] Run with bad/blurry/non-leaf image: guardrail fires, no chemical prescribed
- [ ] Run with unknown district: agent recovers using `known_districts`
- [ ] Fix any tool-schema or prompt issues found
- [ ] **Accept:** 5 runs above behave as described; screenshots saved in `docs/screens/`

## Phase 2 — Data realism (target: by 2:30 PM)
**Spec:** Replace guesswork with real, labeled data where possible.
- [ ] Register free data.gov.in key; set `DATA_GOV_API_KEY`; verify the Agmarknet resource ID and field names
- [ ] Live overlay works; UI badge shows 🟢 LIVE; falls back to 🟡 snapshot on failure (test by unsetting key)
- [ ] Extend `data/kb.json` to 5-6 diseases per crop with source citations (TNAU/ICAR); mark doses "verify with KVK"
- [ ] Add mandi coords for the districts of the demo scenario (include one Tamil Nadu demo path)
- [ ] **Accept:** one run shows live price source (or documented fallback); KB entries all carry a `source` field

## Phase 3 — Voice & multilingual (target: by 4:00 PM, MIDPOINT)
**Spec:** Farmer can speak or type in a regional language and hear the answer.
- [ ] Voice input: browser/mic audio → Gemini transcription → `query` text (English, Hindi, Tamil)
- [ ] TTS output of the advisory (e.g., gTTS or equivalent) for hi/ta/en; remove any placeholder audio
- [ ] Final advisory fully in selected language; numbers/units stay correct
- [ ] **Accept (midpoint demo):** photo + Tamil voice query → Tamil text + audio advisory with trace and net-rupee uplift

## Phase 4 — Robustness & guardrails (target: by 5:30 PM)
**Spec:** Demo cannot crash; unsafe advice is blocked.
- [ ] Timeouts + one retry on Gemini and mandi calls; friendly error messages
- [ ] Cached-demo mode (`DEMO_MODE=1`) that replays a stored successful run if the network/API fails
- [ ] Chemical safety: organic first, pre-harvest interval always shown, severity >= 0.7 adds "visit KVK"
- [ ] Add tests for guardrail thresholds and planner edge cases
- [ ] **Accept:** all tests pass; demo-mode works with network off

## Phase 5 — UX polish (target: by 6:30 PM)
**Spec:** A first-time judge understands value in 10 seconds.
- [ ] Clear hero metric card ("Sell at X: +₹Y vs local mandi")
- [ ] Mobile-friendly layout, large fonts, minimal inputs, sample-case button for the demo
- [ ] Trace panel readable (tool name, purpose, latency, status)
- [ ] **Accept:** run the full flow on a phone-sized browser window

## Phase 6 — Submission assets (target: by 8:00 PM)
**Spec:** Everything the email lists, ready to upload.
- [ ] README: problem, solution, architecture diagram, tech stack, setup, honest limitations, data sources
- [ ] Agent workflow/architecture diagram (PNG or Mermaid) in `docs/`
- [ ] 5-slide deck: Problem · Solution & Agent Flow · Architecture · Demo/Impact metrics · Scalability & Roadmap
- [ ] 2-3 minute demo video (use demo-mode-safe path), farmer-first story
- [ ] Working demo link (Streamlit Community Cloud or similar) + repo public, no secrets
- [ ] Submission fields: project name, team members, domain, problem statement, solution overview, workflow, tech stack, repo, demo, video, deck

## Phase 7 — Submit (8:00 – 9:00 PM)
- [ ] Dry-run the demo once more on the deployed link
- [ ] Submit through the official portal by 8:30 PM (buffer), save confirmation email
- [ ] Final tag: `git tag v1-submission`

## Scalability roadmap (for the deck, not for building today)
More crops/diseases via KB expansion · state-specific mandi coverage · FPO/buyer network integration · WhatsApp/IVR channel for feature phones · KVK expert-in-the-loop escalation · offline-first lite mode
