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
orders = db.orders
products = db.products

app = FastAPI(title="Order Service")

class OrderItem(BaseModel):
    product_id: str
    quantity: int

class CreateOrder(BaseModel):
    user_id: str
    items: list[OrderItem]

@app.get("/health/db")
def health_db():
    try:
        start = time.time()
        client.admin.command("ping")
        return {"status":"ok","db":DB_NAME,"latency_ms": round((time.time()-start)*1000,2)}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/orders", status_code=201)
def create_order(payload: CreateOrder):
    for it in payload.items:
        try:
            p = products.find_one({"_id": ObjectId(it.product_id)})
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid product id {it.product_id}")
        if not p:
            raise HTTPException(status_code=400, detail=f"Product {it.product_id} not found")
        if p.get("stock", 0) < it.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {it.product_id}")
    doc = {"user_id": payload.user_id, "items": [it.dict() for it in payload.items], "status":"PLACED"}
    res = orders.insert_one(doc)
    for it in payload.items:
        products.update_one({"_id": ObjectId(it.product_id)}, {"$inc": {"stock": -it.quantity}})
    return {"id": str(res.inserted_id), "status": "PLACED"}

@app.get("/orders/{order_id}")
def get_order(order_id: str):
    try:
        o = orders.find_one({"_id": ObjectId(order_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid order id")
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"id": str(o["_id"]), "user_id": o["user_id"], "items": o["items"], "status": o["status"]}
