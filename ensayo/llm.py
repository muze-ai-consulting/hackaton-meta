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
from ensayo.costs import ASR_MODEL, ASR_PRICE_PER_HOUR, IMAGE_PRICE, PHASE_CAPS, Ledger, chat_cost

log = logging.getLogger(__name__)

BASE = "https://api.meta.ai/v1"
RETRY_STATUS = {429, 500, 502, 503, 504}
ATTEMPTS = 5
PRODUCT_DEADLINE = 75.0  # segundos que espera el producto en vivo por una llamada, reintentos incluidos
# Spark 1.3 razona antes de responder y esos tokens cuentan dentro de max_tokens (sonda del 2-nov: con 200 tokens
# y el esfuerzo por defecto, la respuesta salía vacía). Se fija el esfuerzo y se suma un margen para razonar.
DEFAULT_EFFORT = "low"
REASONING_ALLOWANCE = {"minimal": 400, "low": 2000, "medium": 6000, "high": 12000}


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
        # Solo el largo: el texto del modelo puede citar el mensaje de la persona, y esto termina en los logs.
        raise ValueError(f"Sin JSON en la respuesta ({len(text)} caracteres)")
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
        effort: str = DEFAULT_EFFORT,
    ) -> None:
        self.effort = effort
        self.deadline: float | None = None  # segundos por llamada, reintentos incluidos; el producto en vivo lo fija
        headers = {}
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
        key = os.environ.get("MODEL_API_KEY") or os.environ.get("META_API_KEY")
        if not key:
            raise SystemExit("Falta MODEL_API_KEY (o META_API_KEY) en .env (ver .env.example). Para probar sin gastar: --mock")
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
        msg = await self.chat_message(model, messages, phase=phase, max_tokens=max_tokens, upcoming_usd=upcoming_usd, note=note)
        return ChatResult(text=msg.get("content") or "", usage=msg["_usage"], usd=msg["_usd"])

    async def chat_message(
        self,
        model: str,
        messages: list[dict[str, Any]],
        *,
        phase: str,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 1500,
        upcoming_usd: float = 0.0,
        note: str = "",
    ) -> dict[str, Any]:
        """El mensaje completo de la respuesta (con tool_calls si se pasaron herramientas), más _usage y _usd."""
        self.ledger.check(phase, upcoming_usd)
        # max_tokens es lo que necesita la respuesta; se le suma el margen para razonar del esfuerzo elegido.
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens + REASONING_ALLOWANCE[self.effort],
            "reasoning_effort": self.effort,
        }
        if tools:
            payload["tools"] = tools
        async with self._sem:
            body = await self._post("/chat/completions", payload)
        usage = body.get("usage") or {}
        usd = self.ledger.record_chat(phase, model, usage, note=note)
        return {**body["choices"][0]["message"], "_usage": usage, "_usd": usd}

    async def image(self, model: str, prompt: str, *, phase: str, size: str = "1024x1024", note: str = "") -> dict[str, Any]:
        """Una imagen de /images/generations; se cobra el precio fijo por imagen de IMAGE_PRICE."""
        usd = IMAGE_PRICE[model]
        self.ledger.check(phase, usd)
        async with self._sem:
            body = await self._post("/images/generations", {"model": model, "prompt": prompt, "n": 1, "size": size})
        self.ledger.record(phase, model, usd, {"images": 1}, note=note)
        return body

    async def transcribe(self, wav: bytes, *, phase: str, note: str = "") -> str:
        """Texto de un WAV con Muse Voice Transcribe (/asr/transcribe, multipart; detecta el idioma solo)."""
        # 16 kHz mono de 16 bits: 32.000 bytes por segundo.
        self.ledger.check(phase, len(wav) / 32_000 / 3600 * ASR_PRICE_PER_HOUR)
        request = json.dumps({"model": ASR_MODEL, "audioEncoding": "WAV"})
        files = {"request": (None, request, "application/json"), "audio": ("audio.wav", wav, "audio/wav")}
        async with self._sem:
            body = await self._post("/asr/transcribe", files=files)
        seconds = float(body.get("audioDurationMs") or 0) / 1000
        self.ledger.record(phase, ASR_MODEL, seconds / 3600 * ASR_PRICE_PER_HOUR, {"audio_seconds": seconds}, note=note)
        return str(body.get("transcript") or "")

    async def _post(self, path: str, payload: dict[str, Any] | None = None, *, files: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            async with asyncio.timeout(self.deadline):
                return await self._post_with_retries(path, payload, files)
        except TimeoutError as exc:
            raise RuntimeError(f"Model API: sin respuesta en {self.deadline} s") from exc

    async def _post_with_retries(self, path: str, payload: dict[str, Any] | None, files: dict[str, Any] | None) -> dict[str, Any]:
        for attempt in range(ATTEMPTS):
            try:
                r = await self._http.post(path, json=payload) if files is None else await self._http.post(path, files=files)
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
