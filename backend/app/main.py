import os
import json
import base64
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime

# FastAPI initialize karein
app = FastAPI(title="MartCart AI Agent API", version="1.0.0")

# Paths Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE_PATH = os.path.join(BASE_DIR, "martcart_data.json")
LOCAL_STORAGE_PATH = os.path.join(BASE_DIR, "user_storage.json")

# Create a dedicated static folder if it doesn't exist to avoid root clashes
STATIC_DIR = os.path.join(BASE_DIR, "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# Mount only the actual static folder
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VoiceChatRequest(BaseModel):
    text: str

def load_martcart_data():
    if not os.path.exists(DATA_FILE_PATH):
        return None
    try:
        with open(DATA_FILE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return None

def save_to_local_storage(user_msg: str, ai_msg: str):
    data = []
    if os.path.exists(LOCAL_STORAGE_PATH):
        try:
            with open(LOCAL_STORAGE_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
        except:
            data = []
            
    new_log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_query": user_msg,
        "agent_response": ai_msg
    }
    data.append(new_log)
    
    with open(LOCAL_STORAGE_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

@app.get("/get-stores")
def get_stores_from_json():
    data = load_martcart_data()
    if not data: return {"error": "Data file nahi mili."}
    home_sections = data.get("homeSections", [])
    stores_list = []
    for section in home_sections:
        if section.get("type") == "STORES":
            stores_list.extend(section.get("items", []))
    return {"recommended_and_top_stores": stores_list}

@app.get("/get-local-logs")
def get_local_logs():
    if os.path.exists(LOCAL_STORAGE_PATH):
        with open(LOCAL_STORAGE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

# 🧠 Simple Conversation Context (Pichli baat yaad rakhne ke liye)
last_discussed_item = ""

@app.post("/api/voice/chat")
def voice_chat_endpoint(payload: VoiceChatRequest):
    global last_discussed_item
    from app.services.voice_service import generate_llm_response, text_to_speech
    
    raw_json = load_martcart_data()
    context_data = ""
    
    if raw_json:
        home_sections = raw_json.get("homeSections", [])
        for section in home_sections:
            section_title = section.get("title", "Category")
            items = section.get("items", [])
            for item in items:
                title = item.get("title", item.get("name", "Unknown Item"))
                price = item.get("price", item.get("discountedPrice", ""))
                price_str = f" - Price: {price}" if price else ""
                context_data += f"- [{section_title}] {title}{price_str}\n"

        if "products" in raw_json:
            for prod in raw_json["products"]:
                p_name = prod.get("name", prod.get("title", ""))
                p_price = prod.get("price", "")
                context_data += f"- Product: {p_name} (Price: {p_price})\n"

    if not context_data.strip():
        context_data = "MartCart Inventory Data: Items including Pizzas, Chicken, Fast Food, and Grocery items are available."

    user_query = payload.text.strip()

    # System instruction with strict rule: NEVER repeat greetings or previous turns!
    full_prompt = (
        f"You are MartCart AI Voice Assistant.\n"
        f"INVENTORY DATA:\n{context_data}\n\n"
        f"CURRENT DISCUSSED ITEM / CONTEXT: {last_discussed_item}\n"
        f"CUSTOMER'S NEW INPUT: '{user_query}'\n\n"
        f"RULES FOR RESPONSE:\n"
        f"1. Answer ONLY the customer's new input directly in 1 short sentence.\n"
        f"2. DO NOT repeat your greeting (like Assalam o Alaikum or how can I help) if already greeted.\n"
        f"3. DO NOT repeat previous conversation responses.\n"
        f"4. If the user asks 'price?', 'bhej do', or 'rate kya hai' without naming the item, use the CURRENT DISCUSSED ITEM context.\n"
        f"5. Reply naturally in Roman Urdu / English."
    )
    
    ai_response_text = generate_llm_response(full_prompt)
    
    # Save/Update current item context for next query
    last_discussed_item = f"User asked: '{user_query}', Agent replied: '{ai_response_text}'"
    
    # Save log
    save_to_local_storage(payload.text, ai_response_text)
    
    # Audio generation
    audio_filename = "output_response.mp3"
    audio_path = os.path.join(STATIC_DIR, audio_filename)
    
    try:
        text_to_speech(ai_response_text, output_path=audio_path)
    except Exception as e:
        print(f"TTS Inner Error: {e}")

    if os.path.exists(audio_path):
        return {
            "status": "success",
            "message": ai_response_text,
            "audio_url": f"/static/{audio_filename}"
        }
    
    return {"error": "Audio file not generated, but log saved."}