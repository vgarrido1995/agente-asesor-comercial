"""
Catálogo oficial de sistemas Garrido Sportech.
Fabricación chilena 🇨🇱 | Envíos a todo Chile y Latinoamérica.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Product:
    id: str
    name: str
    category: str
    description: str
    specs: dict[str, str]
    price: int  # precio en CLP + IVA
    includes: list[str] = field(default_factory=list)
    use_cases: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    compatible_with: list[str] = field(default_factory=list)
    technical_notes: list[str] = field(default_factory=list)


# ── Catálogo oficial Garrido Sportech ────────────────────────────────────
CATALOG: list[Product] = [
    Product(
        id="GF-ALPHA",
        name="G-FORCE α (Alpha)",
        category="Placas de Fuerza",
        description=(
            "Sistema de placas de fuerza para evaluación de saltos e isometrías. "
            "Conjunto de 2 placas con 4 celdas por placa y 1 canal por placa. "
            "Incluye software propio de adquisición y análisis desarrollado en Python."
        ),
        specs={
            "Configuración": "Conjunto de 2 placas de fuerza",
            "Sensórica": "4 celdas por placa",
            "Canales": "1 canal por placa",
            "Frecuencia de análisis": "Hasta 1000 Hz",
            "Variables disponibles": "Fuerza, curva fuerza-tiempo, impulso, RFD y métricas derivadas (según software y protocolo)",
            "Exportación de datos": "CSV y otros formatos definidos por el software",
            "Fabricación": "Chilena 🇨🇱",
        },
        price=850_000,
        includes=[
            "2 placas de fuerza (4 celdas c/u)",
            "Software propio de adquisición y análisis (Python)",
            "Soporte técnico",
        ],
        use_cases=[
            "Evaluación de saltos: CMJ, SJ, DJ",
            "Evaluación de isometrías (según configuración)",
            "Análisis de curva fuerza-tiempo",
            "Cálculo de RFD e impulso",
        ],
        tags=["fuerza", "placa", "salto", "CMJ", "SJ", "DJ", "isometría", "RFD", "impulso", "curva fuerza-tiempo"],
        compatible_with=["GF-CELL"],
        technical_notes=[
            "Frecuencia de análisis hasta 1000 Hz.",
        ],
    ),
    Product(
        id="GF-CELL",
        name="G-FORCE (Celda Individual)",
        category="Celdas de Carga",
        description=(
            "Celda de carga tipo S de 500 kg con adaptadores de muslo. "
            "Diseñada para pruebas isométricas: IMTP, aducción, abducción, "
            "empujes y tracciones según montaje."
        ),
        specs={
            "Tipo de celda": "Tipo S",
            "Capacidad nominal": "500 kg",
            "Frecuencia de análisis": "Hasta 1000 Hz",
            "Métricas disponibles": "Fuerza máxima, curva fuerza-tiempo, impulso, RFD (según software y protocolo)",
            "Exportación de datos": "CSV y otros formatos",
            "Fabricación": "Chilena 🇨🇱",
        },
        price=300_000,
        includes=[
            "Celda de carga tipo S (500 kg)",
            "Adaptadores de muslo",
            "Software propio en Python",
            "Soporte técnico",
        ],
        use_cases=[
            "IMTP (Isometric Mid-Thigh Pull)",
            "Aducción isométrica",
            "Abducción isométrica",
            "Empujes y tracciones isométricas (según montaje)",
        ],
        tags=["fuerza", "celda", "isometría", "IMTP", "aducción", "abducción", "tipo S", "500kg"],
        compatible_with=["GF-ALPHA"],
        technical_notes=[
            "Frecuencia de análisis hasta 1000 Hz.",
            "Las pruebas posibles dependen del montaje y adaptadores utilizados.",
        ],
    ),
    Product(
        id="GJ-001",
        name="G-JUMP (Plataforma de Contacto)",
        category="Plataformas de Contacto",
        description=(
            "Plataforma de contacto refaccionada para medición práctica en terreno. "
            "Mide tiempo de vuelo y tiempo de contacto, calcula altura estimada de salto "
            "y RSI-mod. Software desarrollado en Python con librerías de pygame."
        ),
        specs={
            "Tipo": "Plataforma de contacto refaccionada",
            "Qué mide": "Tiempo de vuelo y tiempo de contacto",
            "Qué calcula": "Altura estimada de salto (por tiempo de vuelo) y RSI-mod",
            "Software": "Desarrollado en Python (pygame)",
            "Enfoque": "Medición práctica en terreno",
            "Fabricación": "Chilena 🇨🇱",
        },
        price=95_000,
        includes=[
            "Plataforma de contacto",
            "Software propio (Python/pygame)",
            "Soporte técnico",
        ],
        use_cases=[
            "Medición de altura de salto en terreno",
            "Evaluación de RSI-mod (Reactive Strength Index modificado)",
            "Monitoreo práctico de rendimiento en salto",
        ],
        tags=["salto", "contacto", "vuelo", "RSI", "altura", "terreno", "plataforma"],
        compatible_with=["GF-ALPHA"],
        technical_notes=[
            "La altura de salto se estima por tiempo de vuelo, no por medición directa de desplazamiento.",
            "RSI-mod = altura de salto / tiempo de contacto.",
        ],
    ),
]

# ── Índices de búsqueda rápida ───────────────────────────────────────────
_BY_ID: dict[str, Product] = {p.id: p for p in CATALOG}
_CATEGORIES: set[str] = {p.category for p in CATALOG}


def get_product_by_id(product_id: str) -> Optional[Product]:
    return _BY_ID.get(product_id.upper())


def search_products(
    query: str = "",
    category: str = "",
    max_price: int | None = None,
) -> list[Product]:
    """Búsqueda flexible por texto, categoría y precio máximo."""
    query_lower = query.lower()
    results = []
    for p in CATALOG:
        if category and p.category.lower() != category.lower():
            continue
        if max_price is not None and p.price > max_price:
            continue
        if query_lower:
            searchable = " ".join([
                p.name.lower(),
                p.description.lower(),
                " ".join(p.tags),
                " ".join(p.specs.values()).lower(),
                " ".join(p.use_cases).lower(),
                p.category.lower(),
            ])
            if query_lower not in searchable:
                continue
        results.append(p)
    return results


def get_categories() -> list[str]:
    return sorted(_CATEGORIES)


def get_all_products() -> list[Product]:
    return list(CATALOG)


def calculate_quote(product_id: str, quantity: int) -> dict:
    """Genera una cotización simple (sin descuentos por volumen por ahora)."""
    product = get_product_by_id(product_id)
    if not product:
        return {"error": f"Producto {product_id} no encontrado."}

    unit_price = product.price
    subtotal = unit_price * quantity
    iva = round(subtotal * 0.19)
    total_con_iva = subtotal + iva

    return {
        "product_id": product.id,
        "product_name": product.name,
        "quantity": quantity,
        "unit_price_clp": unit_price,
        "subtotal_neto": subtotal,
        "iva_19": iva,
        "total_con_iva": total_con_iva,
        "currency": "CLP",
        "nota": "Precios en pesos chilenos. IVA 19% incluido en total.",
        "envio": "Envíos a todo Chile y Latinoamérica.",
    }


def get_compatible_products(product_id: str) -> list[Product]:
    """Devuelve productos compatibles/complementarios."""
    product = get_product_by_id(product_id)
    if not product:
        return []
    return [p for pid in product.compatible_with if (p := get_product_by_id(pid))]
