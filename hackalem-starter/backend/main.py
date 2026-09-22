"""
Точка входа в приложение.

Запуск (из корня проекта):
    uvicorn backend.main:app --reload

Дальше открой http://localhost:8000 — там простой чат, чтобы сразу
проверить, что агент отвечает, до того как строить что-то поверх.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import db
from .agent import run_agent

app = FastAPI(title="HackAlem AI — стартовый каркас")

# CORS открыт на всё — для хакатона это нормально, скорость важнее.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat")
def chat(req: ChatRequest):
    reply = run_agent(req.message, req.session_id)
    return {"reply": reply, "session_id": req.session_id}


@app.get("/api/history/{session_id}")
def history(session_id: str):
    return db.get_history(session_id, limit=100)


# Отдаём фронтенд как статику. Роуты /api/* объявлены выше, поэтому они имеют
# приоритет — mount("/") ловит всё остальное, включая "/" -> frontend/index.html.
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
