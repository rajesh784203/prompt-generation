from fastapi import FastAPI
from models.orm_models import Base
from database.db import engine
from api.routes import router as user_router
from api.prompt.prompt_routes import router as prompt_router
from api.auth.auth_routes import app as auth_router
Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(user_router)
app.include_router(prompt_router)
app.include_router(auth_router)
