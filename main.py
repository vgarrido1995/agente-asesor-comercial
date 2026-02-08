#!/usr/bin/env python3
"""
Interfaz CLI — Asistente Técnico Garrido Sportech.
Ejecución: python main.py
"""

from __future__ import annotations

import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from agent import CommercialAgent
from config import COMPANY_NAME, MODEL_NAME

console = Console()


BANNER = f"""
╔══════════════════════════════════════════════════════════════╗
║    🏋️  Garrido Sportech — Asistente Técnico IA  🇨🇱         ║
║                                                              ║
║  Sistemas de medición biomecánica y rendimiento deportivo    ║
║  Modelo:  {MODEL_NAME:<47s} ║
║                                                              ║
║  Comandos:                                                   ║
║    /nuevo   → Nueva conversación                             ║
║    /estado  → Estado de la conversación                      ║
║    /salir   → Salir del programa                             ║
╚══════════════════════════════════════════════════════════════╝
"""


def main():
    console.print(BANNER, style="bold cyan")
    console.print(
        "💡 Consulta sobre sistemas de medición, especificaciones técnicas, "
        "cotizaciones y compatibilidad.\n",
        style="dim",
    )

    agent = CommercialAgent()

    while True:
        try:
            user_input = console.input("[bold green]Tú > [/]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n👋 ¡Hasta luego!", style="bold yellow")
            break

        if not user_input:
            continue

        # Comandos especiales
        if user_input.lower() == "/salir":
            console.print("👋 ¡Hasta luego!", style="bold yellow")
            break
        elif user_input.lower() == "/nuevo":
            agent.reset()
            console.print("🔄 Conversación reiniciada.\n", style="bold yellow")
            continue
        elif user_input.lower() == "/estado":
            console.print(agent.get_conversation_summary(), style="bold blue")
            if agent.tool_log:
                console.print("Herramientas usadas:", style="bold blue")
                for entry in agent.tool_log[-5:]:
                    console.print(f"  → {entry['tool']}({entry['args']})", style="dim blue")
            console.print()
            continue

        # Enviar al agente con streaming
        console.print()
        with console.status("[bold yellow]Pensando...[/]", spinner="dots"):
            # Usamos chat normal (no stream) para simplicidad en CLI
            try:
                response = agent.chat(user_input)
            except Exception as e:
                console.print(f"❌ Error: {e}", style="bold red")
                console.print(
                    "Verifica tu OPENAI_API_KEY en el archivo .env\n",
                    style="dim red",
                )
                continue

        # Mostrar respuesta como Markdown
        console.print()
        console.print(Panel(
            Markdown(response),
            title="🏋️ Garrido Sportech",
            title_align="left",
            border_style="cyan",
            padding=(1, 2),
        ))
        console.print()


if __name__ == "__main__":
    main()
