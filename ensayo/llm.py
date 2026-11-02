"""Cliente de la Meta Model API (Chat Completions, formato OpenAI) con medidor de gasto, reintentos y modo falso.

Toda llamada pasa por `Ledger.check` antes y por `Ledger.record_chat` después (regla de presupuesto del CLAUDE.md).
En modo falso (`mock=True`) las respuestas salen de `ensayo.mock` sin red y el gasto se anota en un medidor
aparte, results/costs_mock.jsonl: sirve para saber cuánto costaría la corrida real sin gastar créditos.
"""

import asyncio
import json
import logging
import os
import random
import re
from dataclasses import dataclass
from typing import Any

import httpx
from dotenv import load_dotenv

from ensayo import RESULTS, ROOT
from ensayo.costs import PHASE_CAPS, Ledger, chat_cost

log = logging.getLogger(__name__)

BASE = "https://api.meta.ai/v1"
RETRY_STATUS = {429, 500, 502, 503, 504}
ATTEMPTS = 5


@dataclass
class ChatResult:
    text: str
    usage: dict[str, Any]
    usd: float


def mock_ledger() -> Ledger:
    """Medidor sin topes reales para el modo falso: registra el costo hipotético sin bloquear."""
    return Ledger(path=RESULTS / "costs_mock.jsonl", total_budget=1e9, caps=dict.fromkeys(PHASE_CAPS, 1e9))


def estimate_call_usd(model: str, prompt_chars: int, completion_tokens: int, image_tokens: int = 0) -> float:
    """Costo aproximado de una llamada antes de hacerla (4 caracteres por token)."""
    return chat_cost(model, {"prompt_tokens": prompt_chars // 4 + image_tokens, "completion_tokens": completion_tokens})


def extract_json(text: str) -> dict[str, Any]:
    """El objeto JSON de una respuesta, aunque venga envuelto en ``` o con texto alrededor."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end <= start:
        raise ValueError(f"Sin JSON en la respuesta: {text[:200]!r}")
    return json.loads(cleaned[start : end + 1])


class ModelClient:
    def __init__(
        self,
        ledger: Ledger,
        *,
        base: str = BASE,
        key: str | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
        concurrency: int = 8,
        timeout: float = 120.0,
    ) -> None:
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        self.ledger = ledger
        self._http = httpx.AsyncClient(base_url=base, headers=headers, transport=transport, timeout=timeout)
        self._sem = asyncio.Semaphore(concurrency)

    @classmethod
    def from_env(cls, *, mock: bool = False, concurrency: int = 8) -> "ModelClient":
        if mock:
            from ensayo.mock import transport

            return cls(mock_ledger(), base="https://mock.local/v1", transport=transport(), concurrency=concurrency)
        load_dotenv(ROOT / ".env")
        key = os.environ.get("MODEL_API_KEY")
        if not key:
            raise SystemExit("Falta MODEL_API_KEY en .env (ver .env.example). Para probar sin gastar: --mock")
        return cls(Ledger(), base=os.environ.get("MODEL_API_BASE", BASE), key=key, concurrency=concurrency)

    async def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        *,
        phase: str,
        max_tokens: int = 1500,
        upcoming_usd: float = 0.0,
        note: str = "",
    ) -> ChatResult:
        self.ledger.check(phase, upcoming_usd)
        payload = {"model": model, "messages": messages, "max_tokens": max_tokens}
        async with self._sem:
            body = await self._post(payload)
        usage = body.get("usage") or {}
        usd = self.ledger.record_chat(phase, model, usage, note=note)
        text = body["choices"][0]["message"].get("content") or ""
        return ChatResult(text=text, usage=usage, usd=usd)

    async def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        for attempt in range(ATTEMPTS):
            try:
                r = await self._http.post("/chat/completions", json=payload)
            except httpx.TransportError as exc:
                if attempt == ATTEMPTS - 1:
                    raise
                log.warning(f"Error de red ({type(exc).__name__}), reintento {attempt + 1}")
            else:
                if r.is_success:
                    return r.json()
                if r.status_code not in RETRY_STATUS or attempt == ATTEMPTS - 1:
                    raise RuntimeError(f"Model API {r.status_code}: {r.text[:300]}")
                log.warning(f"Model API {r.status_code}, reintento {attempt + 1}")
            await asyncio.sleep(2**attempt + random.random())
        raise RuntimeError("Model API: sin respuesta tras los reintentos")

    async def aclose(self) -> None:
        await self._http.aclose()
