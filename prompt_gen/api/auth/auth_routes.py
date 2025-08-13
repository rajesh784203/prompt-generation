from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie, Header
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from prompt_gen.models.orm_models import User
from prompt_gen.models.pydantic_models import UserCreate, UserLogin, TokenResponse, GoogleAuthRequest, UserResponse, SuccessLogin
from prompt_gen.database.db import SessionLocal
from fastapi.templating import Jinja2Templates
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
import os
from dotenv import load_dotenv

# === CONFIG ===
load_dotenv()
SECRET_KEY = os.getenv("CLIENT_SECRET", "super_secret_key_change_this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")
app = APIRouter()


# === UTILS ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token invalid")
        return {"email": email}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalid")

# === ROUTES ===



@app.post("/signup/", response_model = UserResponse)
def create_user(user : UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.gmail_id == user.gmail_id).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        gmail_id = user.gmail_id,
        user_name = user.user_name,
        password = user.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



from fastapi.responses import JSONResponse

@app.post("/signin", response_model=SuccessLogin)
def signin(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.gmail_id == data.gmail_id).first()
    if not db_user or db_user.password != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": db_user.gmail_id}, timedelta(minutes=60))

    # ✅ Set the access_token as an HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,         # set to True in production with HTTPS
        samesite="lax"        # can be "strict", "lax", or "none" depending on cross-site needs
    )

    return {
        "user_name": db_user.user_name,
        "gmail_id": db_user.gmail_id,
        "access_token": access_token
    }


@app.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_user), db: Session = Depends(get_db)):
    current_user = db.query(User).filter(User.gmail_id == user["email"]).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "gmail_id": current_user.gmail_id,
        "user_name": current_user.user_name,
        "credits": current_user.credits
    }


