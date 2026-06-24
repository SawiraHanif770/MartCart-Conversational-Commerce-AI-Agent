from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from app.services.products_mock import search_products_mock

app = FastAPI(
    title="MartCart Conversational Commerce AI Agent API",
    description="Voice-First Accessibility Backend for MartCart",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

@app.get("/api/products")
def get_products(search: str = Query(None, description="Search keyword for catalog products")):
    products = search_products_mock(search)
    return {"count": len(products), "results": products}