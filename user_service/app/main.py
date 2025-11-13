from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient, errors
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import os, time

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "ecommerce")
JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
JWT_ALGO = "HS256"

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
users = db.users

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="User & Auth Service")

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    name: str = ""

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str

def create_token(user_id: str):
    expire = datetime.utcnow() + timedelta(hours=12)
    to_encode = {"sub": user_id, "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO)

@app.get("/health/db")
def health_db():
    try:
        start = time.time()
        client.admin.command("ping")
        return {"status":"ok","db":DB_NAME,"latency_ms": round((time.time()-start)*1000,2)}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/users/register", response_model=UserOut)
def register(user: RegisterIn):
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    raw = user.password or ""
    safe_bytes = raw.encode("utf-8")[:72]
    safe_pw = safe_bytes.decode("utf-8", "ignore")
    hashed = pwd_ctx.hash(safe_pw)
    doc = {"email": user.email, "password": hashed, "name": user.name}
    try:
        res = users.insert_one(doc)
    except errors.DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")
    return {"id": str(res.inserted_id), "email": user.email, "name": user.name}

@app.post("/users/login")
def login(user: LoginIn):
    doc = users.find_one({"email": user.email})
    if not doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    raw = user.password or ""
    safe_pw = raw.encode("utf-8")[:72].decode("utf-8", "ignore")
    if not pwd_ctx.verify(safe_pw, doc["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(str(doc["_id"]))
    return {"access_token": token, "token_type": "bearer"}
