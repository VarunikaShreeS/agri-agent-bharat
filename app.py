import os
import streamlit as st
from agent_engine import run_agri_agent

st.set_page_config(page_title="KrishiChain Agent - Bharat Agentic 2026", layout="centered")

# Sidebar for API Key input so it never fails
st.sidebar.title("🔑 Configuration")
api_key_input = st.sidebar.text_input("Enter OpenAI API Key", type="password", placeholder="sk-...")

st.title("🌾 KrishiChain Agent")
st.subheader("Autonomous Crop Health & Market Linkage Engine for Bharat")
st.markdown("---")

with st.form("farmer_form"):
    col1, col2 = st.columns(2)
    with col1:
        crop_name = st.text_input("Crop Name", "Tomato")
    with col2:
        location = st.text_input("District / Location", "Nashik, Maharashtra")
        
    symptoms = st.text_area("Describe symptoms / farmer query", "Leaves are curling upwards with yellow spots and whiteflies underneath.")
    
    uploaded_file = st.file_uploader("Upload Leaf / Crop Image (Optional)", type=["jpg", "png", "jpeg"])
    
    submitted = st.form_submit_button("Run Autonomous Agri-Agent Pipeline")

if submitted:
    if not api_key_input:
        st.error("⚠️ Please enter your OpenAI API Key in the left sidebar first!")
    else:
        with st.spinner("Agent is orchestrating vision analysis, agronomy tools, and mandi pricing engines..."):
            try:
                result = run_agri_agent(crop_name, location, symptoms, uploaded_file, api_key=api_key_input)
                st.success("Autonomous Execution Complete!")
                st.markdown("### 📋 Agent Intelligence Report")
                st.markdown(result)
            except Exception as e:
                st.error(f"Execution Error: {e}")