"""Lotes de ejemplo con la misma forma que los de `ensayo.batches`, para desarrollar sin datos de la Ad Library.

Marcas y textos inventados; el alcance es aleatorio. Sirven para probar el circuito completo, no para medir nada.
"""

import random
from typing import Any

BRANDS = [
    ("Café Andino", "café de especialidad", ["DE", "AT"]),
    ("Zapatillas Kilo", "zapatillas de running", ["GB"]),
    ("Verde Box", "cajas de verduras a domicilio", ["FR", "BE"]),
    ("Luma Skin", "crema hidratante", ["ES"]),
    ("Pata Feliz", "comida para perros", ["NL", "DE"]),
    ("Banco Faro", "cuenta sin comisiones", ["IT"]),
]
HOOKS = [
    "{p}: 20 % de descuento solo esta semana.",
    "Más de 10.000 personas ya cambiaron a nuestro {p}.",
    "¿Cansado de lo de siempre? Prueba un {p} distinto.",
    "Nuestro {p}, hecho en Europa y con envío gratis.",
    "Así se ve un {p} bien hecho. Míralo tú mismo.",
    "Última oportunidad: el {p} que se agotó dos veces vuelve hoy.",
]
TITLES = ["Compra ahora", "Más información", "Pruébalo gratis", "Ver la oferta", "Descúbrelo"]


def demo_batches(n_batches: int = 8, seed: int = 5) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    out = []
    for b in range(n_batches):
        brand, product, countries = BRANDS[b % len(BRANDS)]
        page_id = f"demo{b % len(BRANDS)}"
        week = f"2026W{38 + b // len(BRANDS)}"
        hooks = rng.sample(HOOKS, rng.randint(3, 5))
        variants = [
            {"ad_id": f"{page_id}-{week}-{i}", "body": h.format(p=product), "title": rng.choice(TITLES), "platforms": ["facebook", "instagram"]}
            for i, h in enumerate(hooks)
        ]
        reach = {v["ad_id"]: int(rng.lognormvariate(9, 1)) for v in variants}
        total = sum(reach.values())
        out.append(
            {
                "batch_id": f"{page_id}-{week}",
                "page_id": page_id,
                "page_name": f"{brand} (ejemplo)",
                "week": week,
                "target": {
                    "target_ages": ["25", "54"],
                    "target_gender": "All",
                    "target_locations": [{"name": c, "type": "countries", "excluded": False} for c in countries],
                },
                "variants": variants,
                "labels": {ad: {"reach": r, "reach_share": round(r / total, 4), "longevity_days": None} for ad, r in reach.items()},
                "sealed": False,
            }
        )
    return out
