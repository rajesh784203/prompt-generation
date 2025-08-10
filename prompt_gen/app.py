from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.orm_models import Base
from database.db import engine
from api.prompt.prompt_routes import router as prompt_router
from api.auth.auth_routes import app as auth_router

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prompt_router, prefix="/api")
app.include_router(auth_router, prefix="/api")