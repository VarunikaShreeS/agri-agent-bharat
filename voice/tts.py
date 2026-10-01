"""Text-to-speech module using gTTS with concise 5-sentence audio summary generator."""
import io
import re

LANG_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Hindi (हिंदी)": "hi",
    "Tamil": "ta",
    "Tamil (தமிழ்)": "ta",
    "Marathi": "mr",
    "Marathi (मराठी)": "mr",
    "Telugu": "te",
    "Telugu (తెలుగు)": "te",
    "Punjabi": "pa",
    "Punjabi (ਪੰਜਾਬੀ)": "pa"
}


def build_spoken_summary(diagnosis: dict, plan: dict, language: str = "English") -> str:
    """Build a concise ~5-sentence spoken summary suitable for audio playback:
    1. Diagnosis & severity
    2. Primary treatment
    3. Best market and net realization
    4. Uplift vs local baseline
    5. Actionable timing in next 3 days
    """
    lang_lower = language.lower()
    
    # Tamil summary template
    if "tamil" in lang_lower or "தமிழ்" in lang_lower:
        d_text = "பயிர் பரிசோதனை முடிந்தது."
        if diagnosis and diagnosis.get("image_available"):
            dis = diagnosis.get("disease", "").replace("_", " ")
            sev = int(diagnosis.get("severity", 0) * 100)
            d_text = f"உங்கள் பயிரில் {dis} நோய் {sev}% பாதிப்பு கண்டறியப்பட்டுள்ளது."
        
        m_text = ""
        if plan and plan.get("ok"):
            best = plan.get("best", {})
            m_name = best.get("market", "")
            net_val = int(best.get("net", 0))
            uplift = int(plan.get("uplift_inr_vs_local", 0))
            m_text = f"உங்கள் பயிரை விற்க சிறந்த சந்தை {m_name}. அங்கு நிகர லாபம் சுமார் ₹{net_val:,}. உள்ளூர் சந்தையை விட ₹{uplift:,} கூடுதல் லாபம் கிடைக்கும்."
        
        return f"{d_text} இயற்கை மற்றும் பரிந்துரைக்கப்பட்ட முறைகளை உடனடியாக பயன்படுத்தவும். {m_text} அடுத்த 3 நாட்களில் அறுவடை மற்றும் விற்பனை திட்டத்தை செயல்படுத்தவும்."

    # Hindi summary template
    elif "hindi" in lang_lower or "हिंदी" in lang_lower:
        d_text = "फसल का विश्लेषण पूरा हो गया है।"
        if diagnosis and diagnosis.get("image_available"):
            dis = diagnosis.get("disease", "").replace("_", " ")
            sev = int(diagnosis.get("severity", 0) * 100)
            d_text = f"आपकी फसल में {dis} का प्रकोप लगभग {sev}% पाया गया है।"
        
        m_text = ""
        if plan and plan.get("ok"):
            best = plan.get("best", {})
            m_name = best.get("market", "")
            net_val = int(best.get("net", 0))
            uplift = int(plan.get("uplift_inr_vs_local", 0))
            m_text = f"फसल बेचने के लिए सबसे अच्छा बाज़ार {m_name} है। यहाँ आपकी शुद्ध आय लगभग ₹{net_val:,} होगी, जो स्थानीय मंडी से ₹{uplift:,} अधिक है।"
        
        return f"{d_text} पहले जैविक उपचार अपनाएं और सुरक्षा निर्देशों का पालन करें। {m_text} अगले 3 दिनों में सही समय पर कटाई और बिक्री करें।"

    # English summary template (default)
    else:
        d_text = "Crop analysis is complete."
        if diagnosis and diagnosis.get("image_available"):
            dis = diagnosis.get("disease", "").replace("_", " ").title()
            sev = int(diagnosis.get("severity", 0) * 100)
            d_text = f"Your crop has been diagnosed with {dis} at {sev}% severity."
        
        m_text = ""
        if plan and plan.get("ok"):
            best = plan.get("best", {})
            m_name = best.get("market", "the best market")
            net_val = int(best.get("net", 0))
            uplift = int(plan.get("uplift_inr_vs_local", 0))
            m_text = f"The best market to sell is {m_name} with estimated net earnings of ₹{net_val:,}, providing a gain of ₹{uplift:,} over your local mandi."
        
        return f"{d_text} Apply organic treatments first and observe pre-harvest safety intervals. {m_text} Execute your harvest and sales plan within the next 3 days."


def clean_text_for_speech(text: str) -> str:
    """Remove markdown syntax, emojis, bolding, hashes, and code blocks for clean TTS audio."""
    if not text:
        return ""
    t = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    t = re.sub(r"[#*_~`]", "", t)
    t = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", t)
    t = re.sub(r"[🟢🔵🟡🚀🌾⚙️📋🔍✅⚠️]", "", t)
    return " ".join(t.split())[:1200]


def generate_speech(text: str, language_label: str = "English") -> bytes | None:
    """Return mp3 audio bytes via gTTS or None if failed. Never raises unhandled exceptions."""
    try:
        from gtts import gTTS
        lang_code = "en"
        for k, code in LANG_CODES.items():
            if language_label.startswith(k) or k.startswith(language_label):
                lang_code = code
                break

        clean_text = clean_text_for_speech(text)
        if not clean_text:
            return None

        buf = io.BytesIO()
        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        print(f"TTS generation error: {e}")
        return None
