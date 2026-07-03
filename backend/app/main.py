# app/main.py
import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
# 1. StaticFiles import hamesha top par baki imports ke sath aayega
from fastapi.staticfiles import StaticFiles 
from pydantic import BaseModel
from urllib.parse import quote

from app.services.voice_service import generate_llm_response, text_to_speech

# 2. Pehle app initialize hogi
app = FastAPI(title="MartCart AI Agent API", version="1.0.0")

# 3. App initialize hone ke bilkul BAAD static directory mount hogi
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

# 4. Uske baad CORS middleware aayega
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VoiceChatRequest(BaseModel):
    text: str

DATA_FILE_PATH = os.path.join(BASE_DIR, "martcart_data.json")
# ... baki ka code (endpoints aur functions) iske niche wese hi chalega
def load_martcart_data():
    """Sir ki di hui original raw JSON file se data load karne ka function"""
    if not os.path.exists(DATA_FILE_PATH):
        return None
    try:
        with open(DATA_FILE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"JSON Read Error: {e}")
        return None

@app.get("/get-stores")
def get_stores_from_json():
    data = load_martcart_data()
    if not data:
        return {"error": "Data file nahi mili."}
        
    home_sections = data.get("homeSections", [])
    stores_list = []
    for section in home_sections:
        if section.get("type") == "STORES":
            stores_list.extend(section.get("items", []))
            
    return {"recommended_and_top_stores": stores_list}

@app.post("/api/voice/chat")
def voice_chat_endpoint(payload: VoiceChatRequest):
    """User ke text input ko Sir ki ASLI JSON file ke data se match karta hai"""
    
    raw_json = load_martcart_data()
    
    # Asli data se stores aur unke items ka text context banana
    context_data = ""
    if raw_json:
        home_sections = raw_json.get("homeSections", [])
        for section in home_sections:
            if section.get("type") == "STORES":
                items = section.get("items", [])
                for idx, item in enumerate(items, 1):
                    title = item.get("title", "Unknown Store")
                    # Agar json mein price ya tags hon toh woh bhi nikal sakte hain
                    context_data += f"{idx}. Store Name: {title}\n"
    
    # Agar file khali ho ya data na mile
    if not context_data:
        context_data = "No active stores found in MartCart system database."

    # Prompt ke sath sirf aur sirf asli context bhejna
    full_prompt = (
        f"Context Data from MartCart Database (Strictly use this):\n{context_data}\n\n"
        f"User Question: {payload.text}"
    )
    
    # Llama response generate karega
    ai_response_text = generate_llm_response(full_prompt)
    
    # Audio generation
    audio_filename = "output_response.mp3"
    audio_path = text_to_speech(ai_response_text, output_path=audio_filename)
    
    if audio_path and os.path.exists(audio_path):
        return FileResponse(
            path=audio_path, 
            media_type="audio/mpeg", 
            filename=audio_filename,
            headers={"X-AI-Response-Text": quote(ai_response_text)} 
        )
    
    return {"error": "Audio generation failed"}# app/main.py
import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from urllib.parse import quote

from app.services.voice_service import generate_llm_response, text_to_speech

app = FastAPI(title="MartCart AI Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VoiceChatRequest(BaseModel):
    text: str

# Path setup: Backend directory ke mutabiq
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE_PATH = os.path.join(BASE_DIR, "martcart_data.json")

def load_martcart_data():
    """Sir ki di hui original raw JSON file se data load karne ka function"""
    if not os.path.exists(DATA_FILE_PATH):
        return None
    try:
        with open(DATA_FILE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"JSON Read Error: {e}")
        return None

@app.get("/get-stores")
def get_stores_from_json():
    data = load_martcart_data()
    if not data:
        return {"error": "Data file nahi mili."}
        
    home_sections = data.get("homeSections", [])
    stores_list = []
    for section in home_sections:
        if section.get("type") == "STORES":
            stores_list.extend(section.get("items", []))
            
    return {"recommended_and_top_stores": stores_list}

@app.post("/api/voice/chat")
def voice_chat_endpoint(payload: VoiceChatRequest):
    """User ke text input ko Sir ki ASLI JSON file ke data se match karta hai"""
    
    raw_json = load_martcart_data()
    
    # Asli data se stores aur unke items ka text context banana
    context_data = ""
    if raw_json:
        home_sections = raw_json.get("homeSections", [])
        for section in home_sections:
            if section.get("type") == "STORES":
                items = section.get("items", [])
                for idx, item in enumerate(items, 1):
                    title = item.get("title", "Unknown Store")
                    # Agar json mein price ya tags hon toh woh bhi nikal sakte hain
                    context_data += f"{idx}. Store Name: {title}\n"
    
    # Agar file khali ho ya data na mile
    if not context_data:
        context_data = "No active stores found in MartCart system database."

    # Prompt ke sath sirf aur sirf asli context bhejna
    full_prompt = (
        f"Context Data from MartCart Database (Strictly use this):\n{context_data}\n\n"
        f"User Question: {payload.text}"
    )
    
    # Llama response generate karega
    ai_response_text = generate_llm_response(full_prompt)
    
    # Audio generation
    audio_filename = "output_response.mp3"
    audio_path = text_to_speech(ai_response_text, output_path=audio_filename)
    
    if audio_path and os.path.exists(audio_path):
        return FileResponse(
            path=audio_path, 
            media_type="audio/mpeg", 
            filename=audio_filename,
            headers={"X-AI-Response-Text": quote(ai_response_text)} 
        )
    
    return {"error": "Audio generation failed"}# app/main.py
import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from urllib.parse import quote

from app.services.voice_service import generate_llm_response, text_to_speech

app = FastAPI(title="MartCart AI Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VoiceChatRequest(BaseModel):
    text: str

# Path setup: Backend directory ke mutabiq
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE_PATH = os.path.join(BASE_DIR, "martcart_data.json")

def load_martcart_data():
    """Sir ki di hui original raw JSON file se data load karne ka function"""
    if not os.path.exists(DATA_FILE_PATH):
        return None
    try:
        with open(DATA_FILE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"JSON Read Error: {e}")
        return None

@app.get("/get-stores")
def get_stores_from_json():
    data = load_martcart_data()
    if not data:
        return {"error": "Data file nahi mili."}
        
    home_sections = data.get("homeSections", [])
    stores_list = []
    for section in home_sections:
        if section.get("type") == "STORES":
            stores_list.extend(section.get("items", []))
            
    return {"recommended_and_top_stores": stores_list}

@app.post("/api/voice/chat")
def voice_chat_endpoint(payload: VoiceChatRequest):
    """User ke text input ko Sir ki ASLI JSON file ke data se match karta hai"""
    
    raw_json = load_martcart_data()
    
    # Asli data se stores aur unke items ka text context banana
    context_data = ""
    if raw_json:
        home_sections = raw_json.get("homeSections", [])
        for section in home_sections:
            if section.get("type") == "STORES":
                items = section.get("items", [])
                for idx, item in enumerate(items, 1):
                    title = item.get("title", "Unknown Store")
                    # Agar json mein price ya tags hon toh woh bhi nikal sakte hain
                    context_data += f"{idx}. Store Name: {title}\n"
    
    # Agar file khali ho ya data na mile
    if not context_data:
        context_data = "No active stores found in MartCart system database."

    # Prompt ke sath sirf aur sirf asli context bhejna
    full_prompt = (
        f"Context Data from MartCart Database (Strictly use this):\n{context_data}\n\n"
        f"User Question: {payload.text}"
    )
    
    # Llama response generate karega
    ai_response_text = generate_llm_response(full_prompt)
    
    # Audio generation
    audio_filename = "output_response.mp3"
    audio_path = text_to_speech(ai_response_text, output_path=audio_filename)
    
    if audio_path and os.path.exists(audio_path):
        return FileResponse(
            path=audio_path, 
            media_type="audio/mpeg", 
            filename=audio_filename,
            headers={"X-AI-Response-Text": quote(ai_response_text)} 
        )
    
    return {"error": "Audio generation failed"}