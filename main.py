from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise RuntimeError("MONGO_URL not found in environment variables")

client = MongoClient(MONGO_URL)
db = client.get_database("ecommerce")

app = FastAPI(title="Ecommerce Backend", description="HROne Backend Intern Task")

# Pydantic Models
class ProductSize(BaseModel):
    size: str
    quantity: int

class ProductRequest(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    sizes: List[ProductSize]

class ProductCreateResponse(BaseModel):
    product_id: str

class ProductResponse(BaseModel):
    product_id: str
    name: str
    price: float
    description: str
    sizes: List[ProductSize]

class OrderItem(BaseModel):
    product_id: str
    bought_quantity: int
    total_amount: float

class OrderRequest(BaseModel):
    user_id: str
    items: List[OrderItem]
    user_address: str

class OrderResponse(BaseModel):
    order_id: str
    user_id: str
    items: List[OrderItem]
    user_address: str
    timestamp: datetime
    total_amount: float

class StandardResponse(BaseModel):
    message: str

# Helper functions
def product_helper(product) -> dict:
    return {
        "product_id": str(product["_id"]),
        "name": product["name"],
        "price": product["price"],
        "description": product["description"],
        "sizes": product["sizes"]
    }

def order_helper(order) -> dict:
    return {
        "order_id": str(order["_id"]),
        "user_id": order["user_id"],
        "items": order["items"],
        "user_address": order["user_address"],
        "timestamp": order["timestamp"],
        "total_amount": order["total_amount"]
    }

# API Endpoints

@app.post("/products", response_model=ProductCreateResponse, status_code=201)
async def create_product(product: ProductRequest):
    """Create a new product"""
    try:
        product_dict = product.dict()
        product_dict["created_at"] = datetime.utcnow()
        
        result = db.products.insert_one(product_dict)
        
        if result.inserted_id:
            return ProductCreateResponse(product_id=str(result.inserted_id))
        else:
            raise HTTPException(status_code=500, detail="Failed to create product")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products")
async def list_products(
    name: Optional[str] = Query(None, description="Filter by product name (supports regex)"),
    size: Optional[str] = Query(None, description="Filter by size"),
    limit: Optional[int] = Query(10, description="Number of products to return"),
    offset: Optional[int] = Query(0, description="Number of products to skip")
):
    """List products with optional filters"""
    try:
        query_filter = {}
        if name:
            query_filter["name"] = {"$regex": name, "$options": "i"}
        
        # Size filter
        if size:
            query_filter["sizes.size"] = size
        
        # Execute query with pagination
        cursor = db.products.find(query_filter).skip(offset).limit(limit)
        products = []
        
        for product in cursor:
            products.append(product_helper(product))
        
        return {"products": products}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/orders", status_code=201)
async def create_order(order: OrderRequest):
    """Create a new order"""
    try:
        for item in order.items:
            product = db.products.find_one({"_id": ObjectId(item.product_id)})
            if not product:
                raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")
        
        total_amount = sum(item.total_amount for item in order.items)
        
        order_dict = order.dict()
        order_dict["timestamp"] = datetime.utcnow()
        order_dict["total_amount"] = total_amount
        
        result = db.orders.insert_one(order_dict)
        
        if result.inserted_id:
            return {"id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=500, detail="Failed to create order")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/orders/{user_id}")
async def get_user_orders(
    user_id: str,
    limit: Optional[int] = Query(10, description="Number of orders to return"),
    offset: Optional[int] = Query(0, description="Number of orders to skip")
):
    """Get orders for a specific user"""
    try:
        cursor = db.orders.find({"user_id": user_id}).skip(offset).limit(limit)
        orders = []
        
        for order in cursor:
            orders.append(order_helper(order))
        
        return {"orders": orders}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Ecommerce Backend API is running"}

@app.get("/health")
async def health_check():
    try:
        db.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)