# app/services/voice_service.py
import os
import sys
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS

if sys.platform.startswith("win"):
    import _locale
    _locale._getdefaultlocale = lambda *args: ("en_US", "utf8")

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def generate_llm_response(user_text: str) -> str:
    if not client:
        return "Error: Groq API Key set nahi hai."
        
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are MartCart's voice assistant for Pakistani users.\n"
                        "CRITICAL RULES FOR ACCURACY:\n"
                        "1. Rely ONLY on the provided Context Data. Do NOT hallucinate or invent store names (like Savour Foods).\n"
                        "2. If the user asks for a store or food item that is NOT in the context, strictly reply in Urdu that it is not available (e.g., 'Yeh store hamare paas nahi hai').\n"
                        "3. Keep your response in simple Urdu script, but write official store names in English text so gTTS reads them perfectly.\n"
                        "4. Keep it under 10 words."
                    )
                },
                {
                    "role": "user",
                    "content": f"{user_text}"
                }
            ],
            temperature=0.1 # Temperature kam karne se AI jhoot nahi bolta, strict rehta hai
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Error: {str(e)}")
        return "سستم میں خرابی ہے۔"

def text_to_speech(text_content: str, output_path: str = "output_response.mp3") -> str:
    """gTTS ko standard 'ur' par rakh kar natural clean phrasing dena"""
    try:
        safe_text = str(text_content)
        # Hum language ko wapas 'ur' (Urdu) par set kar rahe hain jo Pakistani sound produce karega
        tts = gTTS(text=safe_text, lang="ur", slow=False)
        abs_path = os.path.abspath(output_path)
        
        if os.path.exists(abs_path):
            try: os.remove(abs_path)
            except: pass
                
        tts.save(abs_path)
        return abs_path
    except Exception as e:
        print(f"TTS Error: {str(e)}")
        return ""