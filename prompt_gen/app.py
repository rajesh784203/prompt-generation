from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prompt_gen.models.orm_models import Base
from prompt_gen.database.db import engine
from prompt_gen.api.prompt.prompt_routes import router as prompt_router
from prompt_gen.api.auth.auth_routes import app as auth_router

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