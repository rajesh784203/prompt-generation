from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.orm_models import User
from models.pydantic_models import UserLogin, TokenResponse, GoogleAuthRequest, UserResponse
from database.db import SessionLocal
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

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

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


def get_current_user(token: Optional[str] = Cookie(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"email": payload["sub"]}


# === ROUTES ===

# @app.get("/signup", response_class=HTMLResponse)
# async def signup_page(request: Request):
#     return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signin", response_model=TokenResponse)
def signin(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.gmail_id == data.gmail_id).first()
    if not db_user or db_user.password != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": data.gmail_id})
    response.set_cookie(key="token", value=access_token, httponly=True, samesite="lax")
    return TokenResponse(access_token=access_token)


@app.post("/auth/google", response_model=TokenResponse)
def auth_google(data: GoogleAuthRequest, response: Response, db: Session = Depends(get_db)):
    try:
        decoded_token = firebase_auth.verify_id_token(data.token)
        email = decoded_token.get('email')
        name = decoded_token.get('name', '')
        google_id = decoded_token.get('user_id') or decoded_token.get('sub')

        user = db.query(User).filter(User.gmail_id == email).first()
        if not user:
            new_user = User(
                gmail_id=email,
                user_name=name,
                password=hash_password(google_id)  # we hash google_id as a dummy password
            )
            db.add(new_user)
            db.commit()

        access_token = create_access_token({"sub": email})
        response.set_cookie(key="token", value=access_token, httponly=True, samesite="lax")
        return TokenResponse(access_token=access_token)

    except Exception as e:
        print(f"Firebase verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid Firebase ID token")


@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("token")
    return {"success": True}


@app.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.gmail_id == user["email"]).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

