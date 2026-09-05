"""
Motor principal del Agente IA — Garrido Sportech.
Implementa el loop ReAct con tool calling (compatible OpenAI / Groq).
"""

from __future__ import annotations

import json
from typing import Generator

from openai import OpenAI

from config import (
    GROQ_API_KEY,
    GROQ_BASE_URL,
    MAX_TOKENS,
    MAX_TOOL_ROUNDS,
    MODEL_NAME,
    SYSTEM_PROMPT,
    TEMPERATURE,
)
from tools import TOOL_DEFINITIONS, execute_tool


class AgentError(Exception):
    pass


def _sanitize_message(msg: dict) -> dict:
    """Limpia mensajes para compatibilidad con Groq (whitelist de propiedades)."""
    role = msg.get("role", "")

    if role == "system":
        return {"role": "system", "content": msg.get("content", "")}

    if role == "user":
        return {"role": "user", "content": msg.get("content", "")}

    if role == "assistant":
        cleaned = {"role": "assistant", "content": msg.get("content") or ""}
        # Solo incluir tool_calls si existen y no están vacíos
        if msg.get("tool_calls"):
            sanitized_calls = []
            for tc in msg["tool_calls"]:
                if isinstance(tc, dict):
                    tc_clean = {"id": tc["id"], "type": tc.get("type", "function"),
                                "function": tc["function"]}
                    sanitized_calls.append(tc_clean)
            if sanitized_calls:
                cleaned["tool_calls"] = sanitized_calls
        return cleaned

    if role == "tool":
        return {
            "role": "tool",
            "tool_call_id": msg.get("tool_call_id", ""),
            "content": msg.get("content", ""),
        }

    # Fallback: solo role + content
    return {"role": role, "content": msg.get("content", "")}


class CommercialAgent:
    """Agente conversacional con herramientas para asesoría comercial técnica."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.client = OpenAI(
            api_key=api_key or GROQ_API_KEY,
            base_url=GROQ_BASE_URL,
        )
        self.model = model or MODEL_NAME
        self.messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.tool_log: list[dict] = []  # historial de herramientas usadas

    # ── API pública ──────────────────────────────────────────────────────

    def chat(self, user_message: str) -> str:
        """Envía un mensaje y devuelve la respuesta final del agente."""
        self.messages.append({"role": "user", "content": user_message})
        return self._run_agent_loop()

    def chat_stream(self, user_message: str) -> Generator[str, None, None]:
        """Versión streaming que yield tokens parciales."""
        self.messages.append({"role": "user", "content": user_message})
        yield from self._run_agent_loop_stream()

    def reset(self):
        """Reinicia la conversación manteniendo el system prompt."""
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.tool_log.clear()

    def get_conversation_summary(self) -> str:
        """Resumen rápido de la conversación actual."""
        user_msgs = [m for m in self.messages if m["role"] == "user"]
        return f"Conversación: {len(user_msgs)} mensajes del usuario, {len(self.tool_log)} herramientas usadas."

    # ── Loop interno del agente ──────────────────────────────────────────

    def _clean_messages(self) -> list[dict]:
        """Devuelve copia de messages sin propiedades que Groq no soporta."""
        return [_sanitize_message(m) for m in self.messages]

    def _run_agent_loop(self) -> str:
        """Ejecuta el loop ReAct: LLM → tool calls → LLM → ... hasta respuesta final."""
        for _ in range(MAX_TOOL_ROUNDS):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self._clean_messages(),
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )

            message = response.choices[0].message

            # Si no hay tool calls, es la respuesta final
            if not message.tool_calls:
                assistant_content = message.content or ""
                self.messages.append({"role": "assistant", "content": assistant_content})
                return assistant_content

            # Procesar tool calls
            self.messages.append(_sanitize_message(message.model_dump()))
            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                self.tool_log.append({"tool": fn_name, "args": fn_args})
                result = execute_tool(fn_name, fn_args)

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

        # Si se excedieron las rondas
        return "⚠️ Se alcanzó el límite de iteraciones. Por favor, reformula tu pregunta."

    def _run_agent_loop_stream(self) -> Generator[str, None, None]:
        """Loop con streaming para la respuesta final."""
        for _ in range(MAX_TOOL_ROUNDS):
            # Primero hacer una llamada no-stream para detectar tool calls
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self._clean_messages(),
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )

            message = response.choices[0].message

            if not message.tool_calls:
                # Respuesta final: ahora sí hacemos streaming
                # Removemos el último intento y hacemos stream
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=self._clean_messages(),
                    tools=TOOL_DEFINITIONS,
                    tool_choice="none",
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                    stream=True,
                )
                full_response = []
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        full_response.append(delta.content)
                        yield delta.content

                final = "".join(full_response)
                self.messages.append({"role": "assistant", "content": final})
                return

            # Procesar tool calls
            self.messages.append(_sanitize_message(message.model_dump()))
            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                self.tool_log.append({"tool": fn_name, "args": fn_args})
                yield f"\n🔧 Usando: {fn_name}({json.dumps(fn_args, ensure_ascii=False)})\n"

                result = execute_tool(fn_name, fn_args)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

        yield "\n⚠️ Se alcanzó el límite de iteraciones."
