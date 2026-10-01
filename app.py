import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
from agent.orchestrator import run_agent, MODEL  # noqa: E402

st.set_page_config(page_title="KrishiChain Agent", page_icon="🌾", layout="wide")

st.sidebar.title("⚙️ Settings")
key = st.sidebar.text_input("Gemini API key (optional if set in .env)", type="password")
language = st.sidebar.selectbox("Advisory language", ["English", "Hindi (हिंदी)", "Marathi (मराठी)", "Telugu (తెలుగు)", "Tamil (தமிழ்)", "Punjabi (ਪੰਜਾਬੀ)"])
st.sidebar.caption(f"Model: `{MODEL}`")
st.sidebar.caption("Live prices: " + ("on (data.gov.in key found)" if os.getenv("DATA_GOV_API_KEY") else "off — using seeded snapshot"))

st.title("🌾 KrishiChain Agent")
st.caption("Photo + question → diagnosis → treatment → best mandi by NET rupees, in your language.")

with st.form("f"):
    c1, c2, c3 = st.columns(3)
    crop = c1.selectbox("Crop", ["Tomato", "Onion"])
    district = c2.text_input("District, State", "Nashik, Maharashtra")
    qty = c3.number_input("Quantity to sell (quintals)", min_value=1.0, value=20.0, step=1.0)
    query = st.text_area("Describe the problem (any language)", "Leaves have dark rings and are turning yellow.")
    img = st.file_uploader("Leaf photo (recommended)", type=["jpg", "jpeg", "png"])
    go = st.form_submit_button("🚀 Run agent", use_container_width=True)

if go:
    api_key = key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Add a Gemini API key in the sidebar or .env")
        st.stop()
    with st.spinner("Agent is reasoning and calling tools…"):
        res = run_agent(crop=crop, district=district, quantity_quintals=qty, query=query, language=language,
                        image_bytes=img.getvalue() if img else None,
                        image_mime=img.type if img else "image/jpeg", api_key=api_key)

    if res.errors:
        st.error("Agent error: " + "; ".join(res.errors))

    m = st.columns(4)
    d, p = res.diagnosis, res.plan
    if d and d.get("image_available"):
        m[0].metric("Diagnosis", d["disease"].replace("_", " ").title())
        m[1].metric("Severity / Confidence", f'{d["severity"]:.0%} / {d["confidence"]:.0%}')
        if d.get("low_confidence"):
            st.warning("Low confidence — please upload a clearer close-up photo. The agent will not prescribe chemicals.")
    if p:
        m[2].metric("Best market (net)", p["best"]["market"], f'₹{p["best"]["net"]:,.0f}')
        m[3].metric("Gain vs local mandi", f'₹{p["uplift_inr_vs_local"]:,.0f}', f'{p["uplift_pct_vs_local"]}%')
        badge = "🟢 LIVE" if p["data_source"] == "live_agmarknet" else "🟡 CACHED / SEEDED SNAPSHOT"
        st.caption(f'Price data: {badge} · as of {p["data_as_of"]} · transport, commission & spoilage deducted')
        st.dataframe([{"Market": o["market"], "Distance km": o["distance_km"], "₹/qtl": o["price_per_quintal"],
                       "7d trend %": o["trend_7d_pct"], "Freight ₹": o["freight"], "Net ₹": o["net"]}
                      for o in p["top_options"]], use_container_width=True, hide_index=True)

    with st.expander(f"🔍 Agent trace — {len(res.trace)} real tool calls", expanded=True):
        for s in res.trace:
            icon = "✅" if s["status"] == "ok" else "⚠️"
            st.markdown(f'{icon} **Step {s["step"]}: `{s["tool"]}`** · {s["latency_s"]}s')
            st.code(f'args: {s["args"]}\nresult: {s["result_preview"]}', language="text")

    st.markdown("### 📋 Advisory")
    st.markdown(res.answer)
    st.download_button("📥 Download advisory", res.answer, file_name=f"KrishiChain_{crop}_{district}.md")
