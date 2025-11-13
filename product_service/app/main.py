from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient, errors
import os, time
from bson.objectid import ObjectId

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "ecommerce")

client = None
for i in range(10):
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        break
    except Exception:
        if i == 9:
            raise
        time.sleep(1)

db = client[DB_NAME]
products = db.products

app = FastAPI(title="Product Catalog Service")

class ProductIn(BaseModel):
    name: str
    description: str = ""
    price: float
    category: str = ""
    stock: int = 0

class ProductOut(ProductIn):
    id: str

@app.get("/health/db")
def health_db():
    try:
        start = time.time()
        client.admin.command("ping")
        return {"status":"ok","db":DB_NAME,"latency_ms": round((time.time()-start)*1000,2)}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/products", response_model=ProductOut, status_code=201)
def create_product(payload: ProductIn):
    doc = payload.dict()
    res = products.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    return doc

@app.get("/products", response_model=list[ProductOut])
def list_products(q: str = None):
    query = {}
    if q:
        query = {"name": {"$regex": q, "$options": "i"}}
    items = []
    for p in products.find(query):
        p["id"] = str(p["_id"])
        items.append(p)
    return items
