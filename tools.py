"""
Herramientas (tools) del agente Garrido Sportech.
Cada herramienta se registra con su schema JSON para OpenAI function calling.
"""

from __future__ import annotations

import json
from typing import Any

from catalog import (
    calculate_quote,
    get_all_products,
    get_categories,
    get_compatible_products,
    get_product_by_id,
    search_products,
)

# ── Schemas para OpenAI tool calling ─────────────────────────────────────

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "buscar_sistemas",
            "description": (
                "Busca sistemas de medición en el catálogo Garrido Sportech. "
                "Filtra por texto libre (nombre, tipo, uso, métrica), categoría "
                "o precio máximo en CLP. Usa esta herramienta cuando el usuario "
                "pregunte por productos, sistemas, qué hay disponible o qué sirve "
                "para cierta evaluación."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Texto de búsqueda: nombre del sistema, tipo de prueba (CMJ, IMTP, etc.), métrica (RFD, impulso, etc.) o palabra clave.",
                    },
                    "category": {
                        "type": "string",
                        "description": "Categoría del sistema.",
                        "enum": get_categories(),
                    },
                    "max_price": {
                        "type": "integer",
                        "description": "Precio máximo en CLP (antes de IVA).",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ver_ficha_tecnica",
            "description": (
                "Muestra la ficha técnica completa de un sistema específico: "
                "especificaciones, qué incluye, usos, notas técnicas y precio. "
                "IDs disponibles: GF-ALPHA, GF-CELL, GJ-001."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "ID del sistema (GF-ALPHA, GF-CELL, GJ-001).",
                        "enum": ["GF-ALPHA", "GF-CELL", "GJ-001"],
                    },
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cotizar",
            "description": (
                "Genera una cotización formal con precio neto, IVA 19%% y total "
                "para un sistema en cantidad específica. Precios en CLP."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "ID del sistema a cotizar.",
                        "enum": ["GF-ALPHA", "GF-CELL", "GJ-001"],
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Cantidad de unidades.",
                        "minimum": 1,
                    },
                },
                "required": ["product_id", "quantity"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sistemas_complementarios",
            "description": (
                "Lista los sistemas complementarios a uno dado. Útil para "
                "armar kits de evaluación más completos."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "ID del sistema base.",
                        "enum": ["GF-ALPHA", "GF-CELL", "GJ-001"],
                    },
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "comparar_sistemas",
            "description": (
                "Compara dos o más sistemas lado a lado: specs, métricas, "
                "usos y precios."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["GF-ALPHA", "GF-CELL", "GJ-001"],
                        },
                        "description": "Lista de IDs de sistemas a comparar.",
                        "minItems": 2,
                    },
                },
                "required": ["product_ids"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_contacto",
            "description": (
                "Devuelve la información de contacto de Garrido Sportech: "
                "WhatsApp, Instagram, web y correo. Usa esta herramienta cuando "
                "el usuario quiera cotización formal, comunicarse, o contactar a la empresa."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ver_publicaciones",
            "description": (
                "Devuelve las publicaciones científicas indexadas que validan los "
                "sistemas Garrido Sportech. Usa esta herramienta cuando el usuario "
                "pregunte por validación, evidencia científica, papers o estudios."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ver_descargas",
            "description": (
                "Devuelve los links de descarga de software (Windows) y drivers "
                "(Windows, macOS, Linux) para los sistemas Garrido Sportech. "
                "Usa cuando el usuario pregunte por software, descarga, drivers o instalación."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_catalogo",
            "description": (
                "Muestra un resumen de todos los sistemas disponibles en el catálogo "
                "Garrido Sportech con nombre, categoría, descripción breve y precio."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


# ── Serialización de productos ───────────────────────────────────────────

def _product_summary(p) -> dict:
    """Resumen completo de un producto para devolver al LLM."""
    return {
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "description": p.description,
        "price_clp": f"${p.price:,} CLP + IVA".replace(",", "."),
        "specs": p.specs,
        "includes": p.includes,
        "use_cases": p.use_cases,
        "tags": p.tags,
        "technical_notes": p.technical_notes,
    }


def _product_brief(p) -> dict:
    """Resumen breve para listados."""
    return {
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "description": p.description[:120] + "..." if len(p.description) > 120 else p.description,
        "price_clp": f"${p.price:,} CLP + IVA".replace(",", "."),
    }


# ── Ejecución de herramientas ────────────────────────────────────────────

def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    """Ejecuta una herramienta y devuelve el resultado como JSON string."""

    if name == "buscar_sistemas":
        results = search_products(
            query=arguments.get("query", ""),
            category=arguments.get("category", ""),
            max_price=arguments.get("max_price"),
        )
        if not results:
            return json.dumps(
                {"message": "No se encontraron sistemas con esos criterios."},
                ensure_ascii=False,
            )
        return json.dumps(
            {"count": len(results), "systems": [_product_summary(p) for p in results]},
            ensure_ascii=False, indent=2,
        )

    elif name == "ver_ficha_tecnica":
        p = get_product_by_id(arguments["product_id"])
        if not p:
            return json.dumps(
                {"error": f"Sistema '{arguments['product_id']}' no encontrado."},
                ensure_ascii=False,
            )
        return json.dumps(_product_summary(p), ensure_ascii=False, indent=2)

    elif name == "cotizar":
        quote = calculate_quote(arguments["product_id"], arguments["quantity"])
        return json.dumps(quote, ensure_ascii=False, indent=2)

    elif name == "sistemas_complementarios":
        compatibles = get_compatible_products(arguments["product_id"])
        if not compatibles:
            return json.dumps(
                {"message": "No se encontraron sistemas complementarios."},
                ensure_ascii=False,
            )
        return json.dumps(
            {"complementary_systems": [_product_summary(p) for p in compatibles]},
            ensure_ascii=False, indent=2,
        )

    elif name == "comparar_sistemas":
        ids = arguments["product_ids"]
        products = [get_product_by_id(pid) for pid in ids]
        found = [p for p in products if p is not None]
        missing = [pid for pid, p in zip(ids, products) if p is None]
        comparison = {"systems_compared": [_product_summary(p) for p in found]}
        if missing:
            comparison["not_found"] = missing
        return json.dumps(comparison, ensure_ascii=False, indent=2)

    elif name == "obtener_contacto":
        contacto = {
            "empresa": "Garrido Sportech",
            "web": "https://garridosportech.cl",
            "whatsapp": {
                "numero": "+56 9 2171 1836",
                "link": "https://wa.me/56921711836?text=Hola,%20me%20interesa%20conocer%20más%20sobre%20Garrido%20Sportech",
            },
            "instagram": {
                "usuario": "@garrido_sportech",
                "link": "https://www.instagram.com/garrido_sportech/",
            },
            "ubicacion": "Chile 🇨🇱",
        }
        return json.dumps(contacto, ensure_ascii=False, indent=2)

    elif name == "ver_publicaciones":
        publicaciones = [
            {
                "titulo": "Reliability and Repeatability of the Low-Cost G-Force Load Cell System in Isometric Hip Abduction and Adduction Tests",
                "autores": "Garrido-Osorio V., Fuentes-Barria H., et al.",
                "revista": "Applied Sciences (MDPI)",
                "año": 2025,
                "hallazgo": "Peak Force mostró excelente confiabilidad (ICC = 0.94-0.96)",
                "link": "https://www.mdpi.com/2076-3417/15/21/11457",
            },
            {
                "titulo": "Validation of the G-Force Platform for Isometric Tests in Physically Active Young Adults",
                "autores": "Garrido-Osorio V., Fuentes-Barria H., et al.",
                "revista": "Applied Sciences (MDPI)",
                "año": 2025,
                "hallazgo": "Herramienta válida, confiable y de bajo costo para evaluación de fuerza isométrica",
                "link": "https://www.mdpi.com/2076-3417/15/23/12409",
            },
        ]
        return json.dumps({"publicaciones": publicaciones}, ensure_ascii=False, indent=2)

    elif name == "ver_descargas":
        descargas = {
            "software_windows": [
                {"nombre": "G-Force Pro v8 — Isometría", "link": "https://github.com/vgarrido1995/garridosportech/raw/main/software/GFORCE_Pro_v8.exe"},
                {"nombre": "Force Plate Jump Pro — Saltos", "link": "https://github.com/vgarrido1995/garridosportech/raw/main/software/GARRIDO_JumpAnalyzer_Pro.exe"},
                {"nombre": "G-Force v7 — Isometría", "link": "https://github.com/vgarrido1995/garridosportech/releases/download/v1.0/GFORCE_v7.3.exe"},
                {"nombre": "G-Force JumpPlate v1 — Saltos", "link": "https://github.com/vgarrido1995/garridosportech/releases/download/v1.0/GFORCE_JumpPlate_v1.2.exe"},
                {"nombre": "Garrido Jump v3 — Contacto", "link": "https://github.com/vgarrido1995/garridosportech/releases/download/v1.0/GarridoJump_v3.4.exe"},
            ],
            "drivers": [
                {"sistema": "Windows", "link": "https://github.com/vgarrido1995/garridosportech/releases/download/v1.0/CH34x_Install_Windows_v3_4.zip"},
                {"sistema": "macOS", "link": "https://github.com/vgarrido1995/garridosportech/releases/download/v1.0/CH341SER_MAC_V1_8.zip"},
                {"sistema": "Linux", "link": "https://github.com/vgarrido1995/garridosportech/releases/download/v1.0/CH340_LINUX.zip"},
            ],
        }
        return json.dumps(descargas, ensure_ascii=False, indent=2)

    elif name == "listar_catalogo":
        all_products = get_all_products()
        return json.dumps(
            {"catalog": [_product_brief(p) for p in all_products]},
            ensure_ascii=False, indent=2,
        )

    else:
        return json.dumps(
            {"error": f"Herramienta '{name}' no reconocida."},
            ensure_ascii=False,
        )
