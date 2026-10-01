"""KrishiChain Agent — Bharat Agentic 2026
Photo + Question + Voice ➔ Multimodal Diagnosis ➔ Agronomy KB ➔ Real Mandi Optimization ➔ Regional Audio Advisory
"""
import os
import json
import pathlib
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Streamlit secrets fallback for cloud deployment
try:
    if hasattr(st, "secrets"):
        for secret_key in ["GEMINI_API_KEY", "GEMINI_MODEL", "DATA_GOV_API_KEY", "DEMO_MODE"]:
            if secret_key in st.secrets and not os.getenv(secret_key):
                os.environ[secret_key] = str(st.secrets[secret_key])
except Exception:
    pass

from agent.orchestrator import run_agent, MODEL
from agent import guardrails
from voice import transcribe, tts

st.set_page_config(page_title="KrishiChain Bharat", page_icon="🌾", layout="wide")

DEMO_CACHE_DIR = pathlib.Path("demo_cache")
IS_DEMO_MODE_DEFAULT = os.getenv("DEMO_MODE", "0") == "1"

# ----------------- SIDEBAR -----------------
st.sidebar.title("⚙️ KrishiChain Settings")
key = st.sidebar.text_input("Gemini API key (optional if set in .env / secrets)", type="password")
language = st.sidebar.selectbox("Advisory Language", ["English", "Hindi (हिंदी)", "Tamil (தமிழ்)", "Marathi (मराठी)", "Telugu (తెలుగు)", "Punjabi (ਪੰਜਾਬੀ)"])

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Demo Scenarios")
demo_mode_active = st.sidebar.checkbox("Replay Recorded Runs (Offline Safe)", value=IS_DEMO_MODE_DEFAULT)

selected_demo = None
if demo_mode_active:
    st.sidebar.caption("Select a verified run to replay without live network calls:")
    d_col1, d_col2, d_col3 = st.sidebar.columns(3)
    if d_col1.button("EN 🍅", help="Tomato Early Blight (English)"):
        selected_demo = "tomato_early_blight_en"
    if d_col2.button("HI 🇮🇳", help="Tomato Leaf Curl (Hindi)"):
        selected_demo = "tomato_leaf_curl_hi"
    if d_col3.button("TA 🌿", help="Tomato Early Blight (Tamil)"):
        selected_demo = "tomato_tamil_run"

st.sidebar.markdown("---")
st.sidebar.caption(f"Model: `{MODEL}`")
st.sidebar.caption("Price engine: 🟢 Live Mandi API / 🔵 Frozen Real / 🟡 Seed")

# ----------------- MAIN UI -----------------
st.title("🌾 KrishiChain Agent")
st.markdown("##### **Autonomous Bharat Agri-Advisory**: Leaf Photo + Regional Voice ➔ Pathologist Diagnosis ➔ Real Mandi Net-Rupee Optimizer")

if demo_mode_active:
    st.info("🔹 **DEMO MODE ACTIVE**: Replaying stored benchmark runs. Works seamlessly with network off.")

# If user clicked demo button in sidebar
if selected_demo and (DEMO_CACHE_DIR / f"{selected_demo}.json").exists():
    cached = json.loads((DEMO_CACHE_DIR / f"{selected_demo}.json").read_text(encoding="utf-8"))
    st.session_state["crop"] = cached["crop"]
    st.session_state["district"] = cached["district"]
    st.session_state["qty"] = float(cached["quantity_quintals"])
    st.session_state["query"] = cached["query"]
    st.session_state["demo_result"] = cached

# Input Form
with st.container():
    c1, c2, c3 = st.columns(3)
    crop = c1.selectbox("Crop", ["Tomato", "Onion"], index=0 if st.session_state.get("crop", "Tomato") == "Tomato" else 1)
    district = c2.text_input("District, State", st.session_state.get("district", "Nashik, Maharashtra"))
    qty = c3.number_input("Quantity to sell (quintals)", min_value=1.0, value=st.session_state.get("qty", 20.0), step=1.0)

    # Voice Input Section
    st.markdown("#### 🎙️ Voice Input or Describe Problem")
    v1, v2 = st.columns([1, 2])
    with v1:
        voice_audio = None
        if hasattr(st, "audio_input"):
            voice_audio = st.audio_input("Record voice query")
        audio_file = st.file_uploader("Or upload audio clip (WAV/MP3/M4A)", type=["wav", "mp3", "m4a", "ogg"])
    
    # Process voice if provided
    raw_audio_bytes = None
    if voice_audio:
        raw_audio_bytes = voice_audio.getvalue()
    elif audio_file:
        raw_audio_bytes = audio_file.getvalue()

    if raw_audio_bytes and "last_transcribed_audio" != hash(raw_audio_bytes):
        st.session_state["last_transcribed_audio"] = hash(raw_audio_bytes)
        with st.spinner("Transcribing audio in your language with Gemini..."):
            t_res = transcribe.transcribe_audio(raw_audio_bytes, language_hint=language, api_key=key or os.getenv("GEMINI_API_KEY"))
            if t_res["ok"]:
                st.session_state["query"] = t_res["text"]
                st.success(f"Transcribed: *\"{t_res['text']}\"*")
            else:
                st.warning(f"Voice note: {t_res['error']}. You can type the symptoms below.")

    with v2:
        query = st.text_area("Farmer's question / observed symptoms", st.session_state.get("query", "Leaves have dark concentric rings and yellow halos. Where should I sell?"))
        img = st.file_uploader("Upload leaf photo (optional for vision diagnosis)", type=["jpg", "jpeg", "png"])

    go = st.button("🚀 Run KrishiChain Agent", use_container_width=True, type="primary")

# Execute Agent or Load Demo
res_data = None
is_replay = False

if demo_mode_active and st.session_state.get("demo_result") and not go:
    res_data = st.session_state["demo_result"]
    is_replay = True

if go:
    if demo_mode_active and selected_demo and (DEMO_CACHE_DIR / f"{selected_demo}.json").exists():
        res_data = json.loads((DEMO_CACHE_DIR / f"{selected_demo}.json").read_text(encoding="utf-8"))
        is_replay = True
    else:
        api_key = key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("Please provide a Gemini API key in the sidebar or `.env` file (or enable Demo Mode).")
            st.stop()
        
        with st.spinner("🤖 KrishiChain Agent reasoning and executing tool pipeline…"):
            run_res = run_agent(
                crop=crop,
                district=district,
                quantity_quintals=qty,
                query=query,
                language=language,
                image_bytes=img.getvalue() if img else None,
                image_mime=img.type if img else "image/jpeg",
                api_key=api_key
            )
            # Generate spoken audio summary
            spoken_sum = tts.build_spoken_summary(run_res.diagnosis, run_res.plan, language=language)
            audio_bytes = tts.generate_speech(spoken_sum, language_label=language)
            
            res_data = {
                "answer": run_res.answer,
                "spoken_summary": spoken_sum,
                "audio_bytes": audio_bytes,
                "diagnosis": run_res.diagnosis,
                "plan": run_res.plan,
                "trace": run_res.trace,
                "model": run_res.model,
                "errors": run_res.errors
            }

if res_data:
    st.markdown("---")
    if is_replay:
        st.caption("🟢 **DISPLAYING RECORDED BENCHMARK RUN (DEMO MODE)**")

    d = res_data.get("diagnosis")
    p = res_data.get("plan")

    # 1. HERO METRIC CARD
    if p and p.get("ok"):
        best = p["best"]
        local = p["local_baseline"]
        uplift = p["uplift_inr_vs_local"]
        uplift_pct = p["uplift_pct_vs_local"]
        src = p.get("data_source", "frozen_real")
        as_of = p.get("data_as_of", "recent")

        if src == "live_mandi_api":
            badge_str = f"🟢 LIVE (Mandi Price API, {as_of})"
        elif src == "live_agmarknet":
            badge_str = f"🟢 LIVE (data.gov.in, {as_of})"
        elif src == "frozen_real":
            badge_str = f"🔵 FROZEN REAL ({as_of})"
        else:
            badge_str = f"🟡 SEED ({as_of} illustrative)"

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(20, 83, 45, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%); 
                    border: 2px solid #22c55e; border-radius: 12px; padding: 18px 24px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span style="font-size: 0.85rem; text-transform: uppercase; color: #86efac; font-weight: 700; letter-spacing: 0.05em;">Recommended Market</span>
                    <h2 style="margin: 4px 0; color: #ffffff; font-size: 1.8rem;">Sell at {best['market']} ({best['district']})</h2>
                    <p style="margin: 0; color: #cbd5e1; font-size: 0.95rem;">
                        Net Realization: <b>₹{int(best['net']):,}</b> &nbsp;|&nbsp; Local Mandi ({local['market']}): <b>₹{int(local['net']):,}</b>
                    </p>
                </div>
                <div style="text-align: right; background: rgba(34, 197, 94, 0.15); padding: 10px 18px; border-radius: 10px; border: 1px solid rgba(34, 197, 94, 0.4);">
                    <div style="font-size: 0.8rem; color: #86efac; font-weight: 600;">NET GAIN VS LOCAL</div>
                    <div style="font-size: 1.9rem; font-weight: 800; color: #4ade80;">+₹{int(uplift):,} <span style="font-size: 1.1rem;">({uplift_pct}%)</span></div>
                    <div style="font-size: 0.75rem; color: #94a3b8;">{badge_str}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 2. METRIC TILES
    m1, m2, m3, m4 = st.columns(4)
    if d and d.get("image_available"):
        m1.metric("Diagnosis", d["disease"].replace("_", " ").title())
        m2.metric("Severity / Conf.", f"{d['severity']:.0%} / {d['confidence']:.0%}")
    else:
        m1.metric("Diagnosis Mode", "Text Symptoms")
        m2.metric("Visual Confidence", "N/A (No photo)")

    if p and p.get("ok"):
        m3.metric("Modal Price", f"₹{int(p['best']['price_per_quintal']):,}/qtl")
        m4.metric("Transport Dist.", f"{p['best']['distance_km']:.1f} km")

    # Guardrail check banner
    if d and d.get("low_confidence"):
        st.warning("⚠️ **Low Confidence Guardrail Fired**: Photo is unclear or non-leaf. Chemical remedies have been blocked. Please consult your local KVK.")

    # 3. SPOKEN AUDIO ADVISORY (TTS)
    st.markdown("### 🔊 Regional Audio Advisory")
    audio_data = res_data.get("audio_bytes")
    if not audio_data and res_data.get("audio_file"):
        audio_path = DEMO_CACHE_DIR / res_data["audio_file"]
        if audio_path.exists():
            audio_data = audio_path.read_bytes()

    if audio_data:
        st.audio(audio_data, format="audio/mp3")
        if res_data.get("spoken_summary"):
            st.caption(f"🎧 *Spoken Summary ({language}):* {res_data['spoken_summary']}")
    else:
        st.caption("ℹ️ Spoken audio not generated; see full written advisory below.")

    # 4. WRITTEN ADVISORY & GROUNDING VERIFICATION
    st.markdown("### 📋 Expert Advisory")
    st.markdown(res_data.get("answer", ""))

    # Grounding Verification
    tool_outputs = [s.get("result_preview") for s in res_data.get("trace", [])]
    if p:
        tool_outputs.append(p)
    if d:
        tool_outputs.append(d)
    
    g_res = guardrails.verify_numeric_grounding(res_data.get("answer", ""), tool_outputs, allowed_inputs=[qty])
    if g_res["verified"]:
        st.caption("🛡️ **Deterministic Grounding**: ✅ All prices, net earnings, doses, and distances match tool calculations.")
    else:
        st.caption(f"🛡️ **Grounding Notice**: ⚠️ {g_res['warning']}")

    # 5. HOW THIS WAS CALCULATED (COLLAPSIBLE)
    if p and p.get("ok"):
        with st.expander("📊 How Net Realization is Calculated (Cost Model)", expanded=False):
            st.markdown("""
            **Net Realization Formula**:
            $$\\text{Net Take-Home} = \\text{Gross Revenue} - \\text{Freight} - \\text{Commission (2\\%)} - \\text{Loading (₹15/qtl)} - \\text{Spoilage Loss}$$
            """)
            st.dataframe([
                {"Market": o["market"], "District": o["district"], "Distance (km)": f"{o['distance_km']:.1f}",
                 "Modal (₹/qtl)": f"₹{int(o['price_per_quintal']):,}", "Gross (₹)": f"₹{int(o['gross']):,}",
                 "Freight (₹)": f"₹{int(o['freight']):,}", "Commission (₹)": f"₹{int(o['commission']):,}",
                 "Spoilage (₹)": f"₹{int(o['spoilage_loss']):,}", "Net Realization (₹)": f"₹{int(o['net']):,}"}
                for o in p["top_options"]
            ], use_container_width=True, hide_index=True)

    # 6. AGENT FUNCTION-CALLING TRACE
    with st.expander(f"🔍 Agent Function-Calling Trace ({len(res_data.get('trace', []))} tool executions)", expanded=False):
        for s in res_data.get("trace", []):
            icon = "✅" if s.get("status") == "ok" else "⚠️"
            st.markdown(f"{icon} **Step {s.get('step')}: `{s.get('tool')}`** · {s.get('latency_s')}s")
            st.code(f"args: {s.get('args')}\nresult: {s.get('result_preview')}", language="text")

    st.download_button("📥 Download Written Advisory (.md)", res_data.get("answer", ""), file_name=f"KrishiChain_{crop}_{district}.md")
