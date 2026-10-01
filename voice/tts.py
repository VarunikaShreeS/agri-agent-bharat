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
            rec = plan.get("recommendation", "marginal")
            best = plan.get("best", {})
            best_m = best.get("market", "")
            best_net = int(best.get("net", 0))
            uplift = int(plan.get("uplift_inr_vs_local", 0))
            pct = round(plan.get("uplift_pct_vs_local", 0), 2)
            
            if rec == "travel":
                m_text = f"{best_m} சந்தையில் செலவுகளுக்குப் பிறகு உள்ளூர் சந்தையை விட சுமார் ₹{uplift:,} கூடுதலாக, தோராயமாக ₹{best_net:,} நிகர லாபம் கிடைக்கலாம். இது மதிப்பீடு மட்டுமே."
            elif rec == "marginal":
                m_text = f"{best_m} சந்தையில் விற்பது கிட்டத்தட்ட சமநிலையானது (+{pct}%). உள்ளூர் சந்தையில் விற்பது குறைந்த ஆபத்து உடையது."
            elif rec == "sell_local":
                target_m = plan.get("local_baseline") or plan.get("best", {})
                m_name = target_m.get("market", "")
                net_val = int(target_m.get("net", 0))
                m_text = f"உள்ளூர் சந்தை {m_name} உங்களுக்கு சிறந்தது, அங்கு நிகர லாபம் சுமார் ₹{net_val:,} ஆகும்."
            else:
                m_text = f"உள்ளூர் சந்தை {best_m} உங்களுக்கு சிறந்தது, அங்கு நிகர லாபம் சுமார் ₹{best_net:,} ஆகும்."
        
        disclaimer = "இது மாதிரி தரவு மட்டுமே, நேரடி விலை அல்ல. " if plan and plan.get("is_synthetic") else ""
        return f"{disclaimer}{d_text} இயற்கை மற்றும் பரிந்துரைக்கப்பட்ட முறைகளை உடனடியாக பயன்படுத்தவும். {m_text} அடுத்த 3 நாட்களில் அறுவடை மற்றும் விற்பனை திட்டத்தை செயல்படுத்தவும்."

    # Hindi summary template
    elif "hindi" in lang_lower or "हिंदी" in lang_lower:
        d_text = "फसल का विश्लेषण पूरा हो गया है।"
        if diagnosis and diagnosis.get("image_available"):
            dis = diagnosis.get("disease", "").replace("_", " ")
            sev = int(diagnosis.get("severity", 0) * 100)
            d_text = f"आपकी फसल में {dis} का प्रकोप लगभग {sev}% पाया गया है।"
            if diagnosis.get("severity", 0) >= 0.7:
                d_text += " गंभीर संक्रमण के कारण तुरंत नजदीकी KVK से संपर्क करें।"
        
        m_text = ""
        if plan and plan.get("ok"):
            rec = plan.get("recommendation", "marginal")
            best = plan.get("best", {})
            best_m = best.get("market", "")
            best_net = int(best.get("net", 0))
            uplift = int(plan.get("uplift_inr_vs_local", 0))
            pct = round(plan.get("uplift_pct_vs_local", 0), 2)
            
            if rec == "travel":
                m_text = f"{best_m} में लगभग ₹{best_net:,} शुद्ध आय हो सकती है, जो खर्चों के बाद स्थानीय मंडी से लगभग ₹{uplift:,} अधिक है। यह अनुमानित है।"
            elif rec == "marginal":
                m_text = f"{best_m} में बेचना लगभग बराबर है (+{pct}%)। अपनी स्थानीय मंडी में बेचना कम जोखिम भरा है।"
            elif rec == "sell_local":
                target_m = plan.get("local_baseline") or plan.get("best", {})
                m_name = target_m.get("market", "")
                net_val = int(target_m.get("net", 0))
                m_text = f"स्थानीय मंडी {m_name} में बेचना सबसे बेहतर है, जहाँ अनुमानित शुद्ध आय ₹{net_val:,} है।"
            else:
                m_text = f"स्थानीय मंडी {best_m} में बेचना सबसे बेहतर है, जहाँ अनुमानित शुद्ध आय ₹{best_net:,} है।"
        
        disclaimer = "यह केवल नमूना डेटा है, वास्तविक दरें नहीं। " if plan and plan.get("is_synthetic") else ""
        return f"{disclaimer}{d_text} पहले जैविक उपचार अपनाएं और सुरक्षा निर्देशों का पालन करें। {m_text} अगले 3 दिनों में सही समय पर कटाई और बिक्री करें।"

    # English summary template (default)
    else:
        d_text = "Crop analysis is complete."
        if diagnosis and diagnosis.get("image_available"):
            dis = diagnosis.get("disease", "").replace("_", " ").title()
            sev = int(diagnosis.get("severity", 0) * 100)
            d_text = f"Your crop has been diagnosed with {dis} at {sev}% severity."
        
        m_text = ""
        if plan and plan.get("ok"):
            rec = plan.get("recommendation", "marginal")
            best = plan.get("best", {})
            best_m = best.get("market", "the remote mandi")
            best_net = int(best.get("net", 0))
            uplift = int(plan.get("uplift_inr_vs_local", 0))
            pct = round(plan.get("uplift_pct_vs_local", 0), 2)
            
            if rec == "travel":
                m_text = f"{best_m} may net about Rs {best_net:,}, about Rs {uplift:,} more than your local mandi after costs. Estimated."
            elif rec == "marginal":
                m_text = f"Selling at {best_m} is roughly break-even (+{pct}%). Selling at your local mandi is lower risk."
            elif rec == "sell_local":
                target_m = plan.get("local_baseline") or plan.get("best", {})
                m_name = target_m.get("market", "the local mandi")
                net_val = int(target_m.get("net", 0))
                m_text = f"The local mandi {m_name} is your best option with estimated net earnings of ₹{net_val:,}. Remote markets do not offer additional profit after transport costs."
            else:
                m_text = f"The local mandi {best_m} is your best option with estimated net earnings of ₹{best_net:,}."
        
        disclaimer = "This is sample data, not live prices. " if plan and plan.get("is_synthetic") else ""
        return f"{disclaimer}{d_text} Apply organic treatments first and observe pre-harvest safety intervals. {m_text} Execute your harvest and sales plan within the next 3 days."


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
