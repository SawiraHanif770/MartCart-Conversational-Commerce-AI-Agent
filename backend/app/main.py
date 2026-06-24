from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="MartCart Conversational Commerce AI Agent API",
    description="Voice-First Accessibility Backend for MartCart",
    version="1.0.0"
)

# Configure CORS so your React Native mobile app can talk to it later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the MartCart Accessibility Agent Backend API!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}