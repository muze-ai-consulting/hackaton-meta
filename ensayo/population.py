"""Motor de población: personas sintéticas deterministas a partir de la segmentación de un anuncio.

La población se arma solo con datos de entrada del anuncio (target_ages, target_gender, target_locations),
nunca con su alcance: el alcance es la etiqueta del backtest.

Las proporciones de edad y de plataforma son supuestos iniciales (marcados abajo). Se reemplazan
por las del set de desarrollo con `calibrate_age_weights`, nunca con el set sellado.
"""

import hashlib
import json
import logging
import random
from dataclasses import asdict, dataclass, field
from typing import Any

from ensayo import DATA

log = logging.getLogger(__name__)

AGE_BUCKETS = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
BUCKET_RANGES = {"18-24": (18, 24), "25-34": (25, 34), "35-44": (35, 44), "45-54": (45, 54), "55-64": (55, 64), "65+": (65, 80)}

# Supuesto: perfil de edad aproximado de usuarios adultos de Facebook e Instagram en Europa.
DEFAULT_AGE_WEIGHTS = {"18-24": 0.17, "25-34": 0.27, "35-44": 0.21, "45-54": 0.16, "55-64": 0.11, "65+": 0.08}
# Supuesto: probabilidad de ver el anuncio en Instagram (y no en Facebook) según edad.
INSTAGRAM_SHARE = {"18-24": 0.75, "25-34": 0.65, "35-44": 0.5, "45-54": 0.35, "55-64": 0.25, "65+": 0.2}

INTERESTS = [
    "moda", "deporte", "fitness", "cocina", "viajes", "tecnología", "videojuegos", "belleza", "maternidad",
    "finanzas personales", "música", "cine y series", "mascotas", "decoración", "jardinería", "autos",
    "sustentabilidad", "salud", "humor", "emprendimiento",
]
ATTENTION = [
    "pasa rápido y solo frena con imágenes llamativas",
    "lee el texto si la primera línea le interesa",
    "mira los videos si enganchan en los primeros segundos",
    "desconfía de la publicidad y busca pruebas sociales",
]
PRICE_SENSITIVITY = ["baja", "media", "alta"]
LIFE_STAGE = {
    "18-24": ["estudiante", "primer trabajo"],
    "25-34": ["joven profesional", "pareja sin hijos", "padres primerizos"],
    "35-44": ["familia con hijos chicos", "profesional consolidado"],
    "45-54": ["familia con adolescentes", "profesional senior"],
    "55-64": ["hijos independientes", "preparando el retiro"],
    "65+": ["jubilado", "abuelo o abuela"],
}


@dataclass(frozen=True)
class TargetSpec:
    """Segmentación de entrada del anuncio."""

    age_min: int = 18
    age_max: int = 65
    genders: tuple[str, ...] = ("female", "male")
    countries: tuple[str, ...] = ("GB",)
    country_weights: dict[str, float] = field(default_factory=dict)

    def key(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:12]


@dataclass(frozen=True)
class Persona:
    id: str
    age: int
    age_bucket: str
    gender: str
    country: str
    platform: str
    life_stage: str
    interests: tuple[str, ...]
    attention: str
    price_sensitivity: str

    def describe(self) -> str:
        """Descripción breve en español para el prompt de simulación."""
        genero = {"female": "mujer", "male": "hombre"}.get(self.gender, "persona")
        plataforma = "Instagram" if self.platform == "instagram" else "Facebook"
        return (
            f"{genero.capitalize()} de {self.age} años en {self.country}, {self.life_stage}. "
            f"Le interesa: {', '.join(self.interests)}. En {plataforma} {self.attention}. "
            f"Sensibilidad al precio: {self.price_sensitivity}."
        )


def spec_from_ad(ad: dict[str, Any], fallback_country: str = "GB") -> TargetSpec:
    """Lee target_ages, target_gender y target_locations de un anuncio de ads_archive, con valores por defecto."""
    ages = ad.get("target_ages") or []
    try:
        age_min = int(str(ages[0]).rstrip("+")) if ages else 18
        age_max = int(str(ages[-1]).rstrip("+")) if ages else 65
    except ValueError:
        age_min, age_max = 18, 65
    gender = str(ad.get("target_gender") or "All").lower()
    genders = ("female",) if gender in ("women", "female") else ("male",) if gender in ("men", "male") else ("female", "male")
    countries = tuple(
        sorted(
            {
                loc.get("name", "")
                for loc in ad.get("target_locations") or []
                if not loc.get("excluded") and loc.get("type") == "countries" and loc.get("name")
            }
        )
    )
    return TargetSpec(age_min=max(18, age_min), age_max=max(age_min, age_max), genders=genders, countries=countries or (fallback_country,))


def bucket_weights(spec: TargetSpec, base: dict[str, float]) -> dict[str, float]:
    """Pesos de edad restringidos al rango segmentado; un tramo parcial pesa en proporción a los años cubiertos."""
    out: dict[str, float] = {}
    for bucket, (lo, hi) in BUCKET_RANGES.items():
        overlap = min(hi, spec.age_max if spec.age_max < 65 else 80) - max(lo, spec.age_min) + 1
        if overlap > 0:
            out[bucket] = base[bucket] * overlap / (hi - lo + 1)
    total = sum(out.values())
    return {b: w / total for b, w in out.items()}


def build_population(spec: TargetSpec, n: int = 1000, seed: int = 7, age_weights: dict[str, float] | None = None) -> list[Persona]:
    """Población determinista: la misma segmentación y semilla dan siempre las mismas personas."""
    rng = random.Random(f"{seed}-{spec.key()}")
    weights = bucket_weights(spec, age_weights or DEFAULT_AGE_WEIGHTS)
    buckets, bucket_w = zip(*weights.items())
    countries = list(spec.countries)
    country_w = [spec.country_weights.get(c, 1.0) for c in countries]
    people: list[Persona] = []
    for i in range(n):
        bucket = rng.choices(buckets, bucket_w)[0]
        lo, hi = BUCKET_RANGES[bucket]
        age = rng.randint(max(lo, spec.age_min), min(hi, spec.age_max) if spec.age_max < 65 else hi)
        people.append(
            Persona(
                id=f"{spec.key()}-{seed}-{i:04d}",
                age=age,
                age_bucket=bucket,
                gender=rng.choice(spec.genders),
                country=rng.choices(countries, country_w)[0],
                platform="instagram" if rng.random() < INSTAGRAM_SHARE[bucket] else "facebook",
                life_stage=rng.choice(LIFE_STAGE[bucket]),
                interests=tuple(rng.sample(INTERESTS, 3)),
                attention=rng.choice(ATTENTION),
                price_sensitivity=rng.choice(PRICE_SENSITIVITY),
            )
        )
    return people


def load_or_build(spec: TargetSpec, n: int = 1000, seed: int = 7) -> list[Persona]:
    """Caché en data/populations/: evita recalcular y deja registro de qué población vio cada lote."""
    path = DATA / "populations" / f"{spec.key()}-{seed}-{n}.json"
    if path.exists():
        rows = json.loads(path.read_text(encoding="utf-8"))
        return [Persona(**{**r, "interests": tuple(r["interests"])}) for r in rows]
    people = build_population(spec, n=n, seed=seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([asdict(p) for p in people], ensure_ascii=False), encoding="utf-8")
    log.info(f"Población {path.name}: {n} personas")
    return people


def calibrate_age_weights(dev_ads: list[dict[str, Any]]) -> dict[str, float]:
    """Perfil de edad real desde age_country_gender_reach_breakdown del set de desarrollo (nunca del sellado)."""
    totals = dict.fromkeys(AGE_BUCKETS, 0.0)
    for ad in dev_ads:
        for country in ad.get("age_country_gender_reach_breakdown") or []:
            for row in country.get("age_gender_breakdowns") or []:
                bucket = row.get("age_range")
                if bucket in totals:
                    totals[bucket] += sum(float(row.get(k) or 0) for k in ("male", "female", "unknown"))
    total = sum(totals.values())
    if not total:
        return dict(DEFAULT_AGE_WEIGHTS)
    return {b: v / total for b, v in totals.items()}
