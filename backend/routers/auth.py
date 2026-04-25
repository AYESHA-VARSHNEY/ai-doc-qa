from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.schemas import UserRegister, UserLogin, Token
from passlib.context import CryptContext
from jose import jwt, JWTError
import os, datetime

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"])
security = HTTPBearer()
SECRET = os.getenv("JWT_SECRET", "supersecretkey")

users_db = {}

@router.post("/register")
async def register(user: UserRegister):
    if user.username in users_db:
        raise HTTPException(400, "User already exists")
    users_db[user.username] = pwd_context.hash(user.password)
    return {"message": "Registered successfully"}

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    hashed = users_db.get(user.username)
    if not hashed or not pwd_context.verify(user.password, hashed):
        raise HTTPException(401, "Invalid credentials")
    token = jwt.encode(
        {"sub": user.username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
        SECRET, algorithm="HS256"
    )
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET, algorithms=["HS256"])
        return payload["sub"]
    except JWTError:
        raise HTTPException(401, "Invalid token")
