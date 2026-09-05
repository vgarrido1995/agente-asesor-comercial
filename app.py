"""
Interfaz Web con Streamlit — Asistente Técnico Garrido Sportech.
Ejecución: streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from agent import CommercialAgent
from config import COMPANY_NAME, MODEL_NAME

# ── Configuración de página ──────────────────────────────────────────────
st.set_page_config(
    page_title=f"Asistente Técnico - {COMPANY_NAME}",
    page_icon="🏋️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🏋️ Garrido Sportech")
    st.caption("Sistemas de medición biomecánica")
    st.caption(f"Fabricación chilena 🇨🇱")
    st.caption(f"**Modelo IA:** {MODEL_NAME}")
    st.divider()

    if st.button("🔄 Nueva conversación", use_container_width=True):
        st.session_state.messages = []
        if "agent" in st.session_state:
            st.session_state.agent.reset()
        st.rerun()

    st.divider()
    st.markdown("### 💡 Consultas de ejemplo")
    examples = [
        "¿Qué sistemas tienen disponibles?",
        "Necesito medir fuerza en isometrías, ¿qué me sirve?",
        "¿Cuál es la diferencia entre G-FORCE Alpha y la celda individual?",
        "Cotízame el G-FORCE Alpha",
        "¿Qué mide exactamente la plataforma G-JUMP?",
        "¿Qué frecuencia de análisis tienen las placas de fuerza?",
    ]
    for ex in examples:
        if st.button(f"📝 {ex[:50]}{'...' if len(ex) > 50 else ''}", key=ex, use_container_width=True):
            st.session_state.pending_example = ex

    st.divider()
    st.markdown("### 📦 Catálogo")
    st.markdown("""
    - ⚙️ **G-FORCE α** — Placas de fuerza · $850.000
    - 💪 **G-FORCE** — Celda tipo S · $300.000
    - 🦶 **G-JUMP** — Plataforma contacto · $95.000
    
    _Precios en CLP + IVA_
    """)

    st.divider()
    st.markdown("### 🌐 Web y contacto")
    st.markdown("""
    - 🌐 [garridosportech.cl](https://garridosportech.cl)
    - 📱 [WhatsApp](https://wa.me/56921711836?text=Hola,%20me%20interesa%20conocer%20mas%20sobre%20Garrido%20Sportech)
    - 📸 [Instagram](https://www.instagram.com/garrido_sportech/)
    """)

    st.divider()
    st.markdown("### 📄 Publicaciones")
    st.markdown("""
    - [Confiabilidad celda G-Force (MDPI 2025)](https://www.mdpi.com/2076-3417/15/21/11457)
    - [Validación plataforma G-Force (MDPI 2025)](https://www.mdpi.com/2076-3417/15/23/12409)
    """)

    if "agent" in st.session_state:
        st.divider()
        st.caption(st.session_state.agent.get_conversation_summary())
        if st.session_state.agent.tool_log:
            with st.expander("🔧 Herramientas usadas"):
                for entry in st.session_state.agent.tool_log:
                    st.code(f"{entry['tool']}({entry['args']})", language="python")


# ── Inicialización del estado ────────────────────────────────────────────
if "agent" not in st.session_state:
    st.session_state.agent = CommercialAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []


# ── Header ───────────────────────────────────────────────────────────────
st.title("🏋️ Asistente Técnico — Garrido Sportech")
st.caption(
    "Consulta especificaciones técnicas, solicita cotizaciones, "
    "compara sistemas y resuelve dudas sobre medición biomecánica."
)

# ── Historial de mensajes ────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🏋️"):
        st.markdown(msg["content"])

# ── Input del usuario ────────────────────────────────────────────────────
# Manejar ejemplos del sidebar
user_input = None
if "pending_example" in st.session_state:
    user_input = st.session_state.pending_example
    del st.session_state.pending_example

prompt = st.chat_input("Consulta técnica, cotización o comparación de sistemas...")
if prompt:
    user_input = prompt

if user_input:
    # Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Respuesta del agente
    with st.chat_message("assistant", avatar="🏋️"):
        with st.spinner("🔍 Consultando catálogo de sistemas..."): 
            try:
                response = st.session_state.agent.chat(user_input)
            except Exception as e:
                response = (
                    f"❌ **Error:** {str(e)}\n\n"
                    "Verifica que tu `OPENAI_API_KEY` esté configurada en el archivo `.env`."
                )
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
