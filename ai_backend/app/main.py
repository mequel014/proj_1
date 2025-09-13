# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from utils.db import create_db_and_tables
from routers import auth, characters, dialogs, admin

from prometheus_fastapi_instrumentator import Instrumentator

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="LLM Chat Backend", lifespan=lifespan)

# регистрируем /metrics
Instrumentator().instrument(app).expose(app)

# Простой CORS (под фронт локально)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # на проде сузьте!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статика (для картинок персонажей, если захотите)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(characters.router, prefix="/characters", tags=["characters"])
app.include_router(dialogs.router, prefix="/dialogs", tags=["dialogs"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# Для проверки
@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}