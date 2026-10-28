# test_groq.py
import os
from dotenv import load_dotenv
from groq import Groq

# .env file se variables load karne ke liye
load_dotenv()

# API Key check karne ke liye
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ Error: GROQ_API_KEY nahi mili! Apni .env file check karein.")
    exit()

print("🔑 API Key successfully detect ho gayi hai!")

# Groq client initialize karein
client = Groq(api_key=api_key)

try:
    print("🤖 Llama 3 se connect ho raha hai... Please wait...")
    
    # Llama 3 model ko ek simple message bhej kar test karein
    completion = client.chat.completions.create(
       model="llama-3.1-8b-instant",  # Updated to Groq's active Llama 3.1 model
        messages=[
            {
                "role": "user",
                "content": "Hello! I am building MartCart, a voice agent for visually impaired users. Say a quick hello!"
            }
        ],
        temperature=0.7,
        max_tokens=100
    )
    
    # Response print karein
    print("\n🎉 Success! Llama 3 ka response:")
    print(completion.choices[0].message.content)

except Exception as e:
    print(f"\n❌ Kuch galti hui hai: {e}")