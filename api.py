"""
API REST del Agente IA — Garrido Sportech.
Endpoint para el widget de chat embebible en garridosportech.cl

Ejecución: uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import uuid
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from agent import CommercialAgent


# ── Sesiones de conversación ─────────────────────────────────────────────
sessions: dict[str, CommercialAgent] = {}
MAX_SESSIONS = 100
RATE_LIMIT_REQUESTS = 20
RATE_LIMIT_WINDOW_SECONDS = 60
request_times: dict[str, deque[float]] = defaultdict(deque)


def enforce_rate_limit(request: Request) -> None:
    """Limita solicitudes por IP para reducir abuso de la cuota del proveedor."""
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    history = request_times[client_ip]
    while history and now - history[0] >= RATE_LIMIT_WINDOW_SECONDS:
        history.popleft()
    if len(history) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Demasiadas solicitudes. Intente nuevamente en un minuto.")
    history.append(now)


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
    request_times.clear()


app = FastAPI(
    title="Garrido Sportech — Asistente Técnico API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: sólo sitios oficiales y desarrollo local explícito
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://garridosportech.cl",
        "https://www.garridosportech.cl",
        "https://garridosportech.com",
        "https://www.garridosportech.com",
        "http://localhost",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos del widget
app.mount("/widget", StaticFiles(directory="widget"), name="widget")


# ── Modelos ──────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = Field(default=None, max_length=100)


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
async def chat(request: ChatRequest, http_request: Request):
    """Envía un mensaje al agente y recibe la respuesta."""
    enforce_rate_limit(http_request)
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")

    session_id, agent = get_or_create_session(request.session_id)

    try:
        reply = agent.chat(request.message)
    except Exception:
        raise HTTPException(status_code=503, detail="El asistente no está disponible temporalmente.")

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
