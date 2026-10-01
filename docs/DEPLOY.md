# Streamlit Community Cloud Deployment Guide

Follow these simple steps to deploy KrishiChain Bharat on Streamlit Community Cloud:

### 1. Push Code to GitHub
Ensure the `main` branch of your GitHub repository contains the latest code, including `data/`, `demo_cache/`, `requirements.txt`, and `app.py`.

### 2. Connect Repository on Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.
2. Click **New app**.
3. Select:
   - **Repository**: `VarunikaShreeS/agri-agent-bharat` (or your fork)
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Click **Advanced Settings** before deploying.

### 3. Configure Secrets in Streamlit Cloud
In the **Secrets** section under Advanced Settings, paste the following configuration:

```toml
# Required: Google Gemini API Key
GEMINI_API_KEY = "your_real_gemini_api_key_here"

# Model Selection
GEMINI_MODEL = "gemini-2.5-flash"

# Optional: data.gov.in API key for live Agmarknet
DATA_GOV_API_KEY = ""

# Demo Mode toggle (set to 1 to force offline replay mode, or 0 for live agent)
DEMO_MODE = "0"
```

### 4. Deploy!
Click **Deploy**. Streamlit Cloud will install all dependencies from `requirements.txt` and launch the application.

---

### Environment Variable & Secrets Verification
`app.py` automatically checks both `st.secrets` and `os.environ` so that API keys and configurations function seamlessly in both local and cloud environments.
