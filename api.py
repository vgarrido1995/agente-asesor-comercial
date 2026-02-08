"""
API REST del Agente IA — Garrido Sportech.
Endpoint para el widget de chat embebible en garridosportech.cl

Ejecución: uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agent import CommercialAgent


# ── Sesiones de conversación ─────────────────────────────────────────────
sessions: dict[str, CommercialAgent] = {}
MAX_SESSIONS = 100


def get_or_create_session(session_id: str | None) -> tuple[str, CommercialAgent]:
    """Obtiene o crea una sesión de agente."""
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]

    # Limpiar sesiones si hay demasiadas
    if len(sessions) >= MAX_SESSIONS:
        oldest = next(iter(sessions))
        del sessions[oldest]

    new_id = session_id or str(uuid.uuid4())
    agent = CommercialAgent()
    sessions[new_id] = agent
    return new_id, agent


# ── App FastAPI ──────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    sessions.clear()


app = FastAPI(
    title="Garrido Sportech — Asistente Técnico API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: permitir garridosportech.cl y localhost para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://garridosportech.cl",
        "https://www.garridosportech.cl",
        "http://localhost",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:5500",
        "*",  # Desarrollo — restringir en producción
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos del widget
app.mount("/widget", StaticFiles(directory="widget"), name="widget")


# ── Modelos ──────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    tools_used: list[str]


# ── Endpoints ────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "service": "Garrido Sportech — Asistente Técnico IA",
        "status": "online",
        "docs": "/docs",
        "widget_demo": "/widget/demo.html",
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Envía un mensaje al agente y recibe la respuesta."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")

    session_id, agent = get_or_create_session(request.session_id)

    try:
        reply = agent.chat(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del agente: {str(e)}")

    tools = [entry["tool"] for entry in agent.tool_log[-5:]]  # últimas 5

    return ChatResponse(
        reply=reply,
        session_id=session_id,
        tools_used=tools,
    )


@app.post("/reset")
async def reset_session(session_id: str | None = None):
    """Reinicia una conversación."""
    if session_id and session_id in sessions:
        sessions[session_id].reset()
        return {"status": "reset", "session_id": session_id}
    return {"status": "no_session", "message": "Sesión no encontrada."}


@app.get("/health")
async def health():
    return {"status": "ok", "active_sessions": len(sessions)}
