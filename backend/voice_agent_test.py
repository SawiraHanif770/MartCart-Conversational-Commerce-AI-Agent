import os
import wave
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS
import sounddevice as sd
import numpy as np

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_voice_response(text_content, filename="response.mp3"):
    print("?? Text ko voice mein convert kiya ja raha hai (gTTS)...")
    tts = gTTS(text=text_content, lang="en")
    tts.save(filename)
    print(f"?? Audio file '{filename}' successfully save ho gayi hai!")

def record_audio_test(filename="user_input.wav", duration=4, fs=44100):
    print(f"\n??? Mic On! Agle {duration} seconds ke liye kuch bolein...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    print("?? Recording khatam!")
    
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(recording.tobytes())
    print(f"?? Aapki recording '{filename}' mein save ho gayi hai!\n")

try:
    record_audio_test()

    print("?? Llama 3.1 se request process ho rahi hai...")
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": "Give a welcoming 1-sentence grocery store greeting for a blind customer shopping on MartCart."
            }
        ]
    )
    
    ai_text = completion.choices[0].message.content
    print(f"\n?? AI Ne Kaha: {ai_text}\n")
    
    generate_voice_response(ai_text)
    print("\n?? Sab kuch sahi chal gaya! Apne folder mein 'user_input.wav' aur 'response.mp3' check karein!")

except Exception as e:
    print(f"? Error: {e}")
