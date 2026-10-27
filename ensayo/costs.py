"""Medidor de gasto de la Model API con tope por fase.

Tenemos 150 créditos para toda la hackatón. Cada llamada se anota en results/costs.jsonl y, antes de llamar,
`Ledger.check` corta si la fase o el total ya llegaron a su tope. Precios en US$ por millón de tokens
(dev.meta.ai/products/meta-model-api, verificados el 26-oct): entrada, entrada en caché, salida.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ensayo import RESULTS

log = logging.getLogger(__name__)

PRICES = {
    "muse-spark-1.3": (1.25, 0.15, 4.25),
    "muse-spark-1.3-contributor": (0.10, 0.002, 0.20),
}
IMAGE_PRICE = {"muse-image-1.0": 0.01}

TOTAL_BUDGET = 150.0
# Topes por fase; lo que sobra queda de reserva para repetir algo o para el demo.
PHASE_CAPS = {
    "pruebas": 5.0,
    "calibracion": 25.0,
    "sellado": 20.0,
    "en-vivo": 20.0,
    "demo": 30.0,
}


class BudgetExceeded(RuntimeError):
    pass


def chat_cost(model: str, usage: dict[str, Any]) -> float:
    """Costo de una respuesta con el formato de uso de Chat Completions."""
    price_in, price_cached, price_out = PRICES[model]
    prompt = int(usage.get("prompt_tokens") or 0)
    cached = int((usage.get("prompt_tokens_details") or {}).get("cached_tokens") or 0)
    completion = int(usage.get("completion_tokens") or 0)
    return ((prompt - cached) * price_in + cached * price_cached + completion * price_out) / 1e6


@dataclass
class Ledger:
    path: Path = RESULTS / "costs.jsonl"
    total_budget: float = TOTAL_BUDGET
    caps: dict[str, float] = field(default_factory=lambda: dict(PHASE_CAPS))

    def entries(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def spent(self, phase: str | None = None) -> float:
        return sum(e["usd"] for e in self.entries() if phase is None or e["phase"] == phase)

    def check(self, phase: str, upcoming_usd: float = 0.0) -> None:
        """Corta antes de llamar si la fase o el total se pasarían de su tope."""
        if phase not in self.caps:
            raise ValueError(f"Fase desconocida: {phase}. Fases: {', '.join(self.caps)}")
        total, in_phase = self.spent(), self.spent(phase)
        if total + upcoming_usd > self.total_budget:
            raise BudgetExceeded(f"Total gastado US$ {total:.2f} de {self.total_budget:.0f}")
        if in_phase + upcoming_usd > self.caps[phase]:
            raise BudgetExceeded(f"Fase {phase}: US$ {in_phase:.2f} de {self.caps[phase]:.0f}")

    def record(self, phase: str, model: str, usd: float, usage: dict[str, Any] | None = None, note: str = "") -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        entry = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "phase": phase, "model": model, "usd": round(usd, 6), "usage": usage or {}, "note": note}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def record_chat(self, phase: str, model: str, usage: dict[str, Any], note: str = "") -> float:
        usd = chat_cost(model, usage)
        self.record(phase, model, usd, usage, note)
        return usd

    def report(self) -> dict[str, Any]:
        by_phase = {p: round(self.spent(p), 2) for p in self.caps}
        return {"total": round(self.spent(), 2), "budget": self.total_budget, "by_phase": by_phase, "caps": self.caps}


def estimate_batch_usd(
    model: str,
    variants: int,
    personas: int = 1000,
    per_call: int = 20,
    orders: int = 4,
    image_tokens: int = 1200,
    cache_hit: float = 0.0,
) -> float:
    """Costo esperado de simular un lote. image_tokens y cache_hit se reemplazan por lo medido en la prueba del día 0."""
    price_in, price_cached, price_out = PRICES[model]
    calls = -(-personas // per_call) * orders
    fixed = variants * image_tokens + 300
    var = per_call * 80
    out = per_call * 120
    cost_in = (fixed * (cache_hit * price_cached + (1 - cache_hit) * price_in) + var * price_in) / 1e6
    return calls * (cost_in + out * price_out / 1e6)
