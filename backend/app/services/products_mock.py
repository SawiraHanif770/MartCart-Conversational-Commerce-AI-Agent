# app/services/products_mock.py

MOCK_PRODUCTS = [
    {
        "_id": "64c9d7b3e4b0a1b2c3d4e5f1",
        "name": "Wireless Bluetooth Headphones",
        "description": "High-quality over-ear headphones with active noise cancellation and 40-hour battery life.",
        "price": 89.99,
        "sku": "TECH-HEAD-001",
        "stock": 45,
        "images": [{"url": "https://example.com/images/headphones.jpg", "altText": "Black Wireless Headphones"}],
        "category": "64c9d5a1e4b0a1b2c3d4e5f0",
        "subCategory": "64c9d6b2e4b0a1b2c3d4e5f0",
        "isActive": True
    },
    {
        "_id": "64c9d7b3e4b0a1b2c3d4e5f2",
        "name": "Organic Almond Milk",
        "description": "Unsweetened, non-dairy vanilla almond milk, rich in calcium.",
        "price": 3.49,
        "sku": "GROC-MILK-002",
        "stock": 12,
        "images": [{"url": "https://example.com/images/almond_milk.jpg", "altText": "1 Litre Almond Milk Carton"}],
        "category": "64c9d5a1e4b0a1b2c3d4e5f5",
        "subCategory": "64c9d6b2e4b0a1b2c3d4e5f6",
        "isActive": True
    }
]

def search_products_mock(query: str):
    """Simulates searching MartCart products by keyword matching."""
    if not query:
        return MOCK_PRODUCTS
    
    query_lower = query.lower()
    results = []
    for product in MOCK_PRODUCTS:
        if query_lower in product["name"].lower() or query_lower in product["description"].lower():
            if product["isActive"]:
                results.append(product)
    return results