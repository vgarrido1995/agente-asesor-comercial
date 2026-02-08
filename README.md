# 🏋️ Garrido Sportech — Asistente Técnico IA

Agente de inteligencia artificial que actúa como **Asistente Técnico** oficial de Garrido Sportech, fabricación chilena 🇨🇱 de sistemas de medición biomecánica y rendimiento deportivo.

Capacidades:
- 🔍 **Consultar el catálogo** de sistemas de medición disponibles
- 📋 **Fichas técnicas** con especificaciones, frecuencias, métricas y limitaciones reales
- ⚖️ **Comparar sistemas** lado a lado
- 💰 **Cotizaciones formales** con IVA 19% (precios en CLP)
- 🔗 **Sistemas complementarios** para armar kits de evaluación
- 💬 **Asesoría técnica honesta** — sin exageraciones ni marketing agresivo

## 📦 Catálogo de sistemas

| Sistema | Tipo | Precio |
|---|---|---|
| ⚙️ G-FORCE α (Alpha) | 2 placas de fuerza (4 celdas c/u, 1 canal c/u) | $850.000 CLP + IVA |
| 💪 G-FORCE | Celda tipo S 500 kg + adaptadores de muslo | $300.000 CLP + IVA |
| 🦶 G-JUMP | Plataforma de contacto | $95.000 CLP + IVA |

Todos incluyen software propio (Python) y soporte técnico.

## 📁 Estructura del proyecto

```
agente-asesor-comercial/
├── config.py          # System prompt y configuración Garrido Sportech
├── catalog.py         # Catálogo oficial de sistemas
├── tools.py           # Herramientas del agente (function calling)
├── agent.py           # Motor del agente IA (loop ReAct con OpenAI)
├── main.py            # Interfaz CLI (terminal con Rich)
├── app.py             # Interfaz Web (Streamlit)
├── requirements.txt   # Dependencias Python
├── .env.example       # Variables de entorno de ejemplo
└── README.md
```

## 🚀 Instalación

```bash
cd agente-asesor-comercial

# Entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# Dependencias
pip install -r requirements.txt

# Configurar API Key
cp .env.example .env
# Edita .env con tu OPENAI_API_KEY
```

## 💻 Uso

### Terminal (CLI)
```bash
python main.py
```

### Web (Streamlit)
```bash
streamlit run app.py
```

## 🛠️ Herramientas del agente

| Herramienta | Descripción |
|---|---|
| `buscar_sistemas` | Busca por texto, categoría o precio máximo |
| `ver_ficha_tecnica` | Ficha técnica completa de un sistema |
| `cotizar` | Cotización con neto + IVA 19% |
| `sistemas_complementarios` | Sistemas que se complementan |
| `comparar_sistemas` | Comparación lado a lado |
| `listar_catalogo` | Resumen de todo el catálogo |

## 📝 Ejemplos de consultas

```
> ¿Qué sistemas tienen disponibles?
> Necesito medir fuerza en isometrías, ¿qué me sirve?
> ¿Cuál es la diferencia entre G-FORCE Alpha y la celda individual?
> Cotízame el G-FORCE Alpha
> ¿Qué mide exactamente la plataforma G-JUMP?
> ¿A qué frecuencia real muestrean las placas de fuerza?
> ¿Qué sistemas me sirven para evaluar un equipo de rugby?
```

## ⚙️ Personalización

- **Agregar productos**: edita `catalog.py`
- **Modificar comportamiento**: ajusta `SYSTEM_PROMPT` en `config.py`
- **Cambiar modelo**: modifica `MODEL_NAME` en `.env`
