"""Transcribes farmer's speech in English, Hindi, or Tamil using Gemini multimodal audio capabilities."""
import os
from google import genai
from google.genai import types

def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/wav", language_hint: str = "English", api_key: str = None, model: str = None) -> dict:
    """Transcribe audio bytes to text in the spoken language.
    Returns: {"ok": bool, "text": str, "error": str | None}
    """
    if not audio_bytes or len(audio_bytes) < 100:
        return {"ok": False, "text": "", "error": "No audio data received or audio clip too short."}

    k = api_key or os.getenv("GEMINI_API_KEY")
    if not k:
        return {"ok": False, "text": "", "error": "No Gemini API key available for audio transcription."}

    m = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    client = genai.Client(api_key=k)

    prompt = (
        f"You are an agricultural voice assistant for Indian farmers. "
        f"Transcribe the spoken audio into text in the original language ({language_hint}, Hindi, Tamil, Marathi, Telugu, or English). "
        f"Return ONLY the exact transcribed text words without any preamble, translation, or extra explanations."
    )

    try:
        resp = client.models.generate_content(
            model=m,
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                prompt
            ],
            config=types.GenerateContentConfig(temperature=0.0)
        )
        text = (resp.text or "").strip()
        if not text:
            return {"ok": False, "text": "", "error": "Audio could not be transcribed or was silent."}
        return {"ok": True, "text": text, "error": None}
    except Exception as e:
        return {"ok": False, "text": "", "error": f"Transcription error: {str(e)}"}
