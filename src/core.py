from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = ("answer", "confidence", "actions")


@dataclass(frozen=True)
class UsageMetrics:
    tokens_prompt: int
    tokens_completion: int
    total_tokens: int
    latency_ms: int
    estimated_cost_usd: float
    timestamp: str


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_json_output(raw_text: str) -> dict[str, Any]:
    parsed = json.loads(raw_text)
    if not isinstance(parsed, dict):
        raise ValueError("El output no es un objeto JSON.")
    return parsed


def validate_contract(payload: dict[str, Any]) -> tuple[bool, str | None]:
    for key in REQUIRED_FIELDS:
        if key not in payload:
            return False, f"Falta el campo requerido: {key}"
    if not isinstance(payload["answer"], str):
        return False, "El campo 'answer' debe ser string."
    confidence = payload["confidence"]
    if not isinstance(confidence, (int, float)):
        return False, "El campo 'confidence' debe ser numerico."
    if not 0 <= float(confidence) <= 1:
        return False, "El campo 'confidence' debe estar entre 0 y 1."
    if not isinstance(payload["actions"], list) or not all(
        isinstance(item, str) for item in payload["actions"]
    ):
        return False, "El campo 'actions' debe ser lista de strings."
    return True, None


def estimate_cost_usd(
    prompt_tokens: int,
    completion_tokens: int,
    input_cost_per_1m: float = 0.15,
    output_cost_per_1m: float = 0.60,
) -> float:
    input_cost = (prompt_tokens / 1_000_000) * input_cost_per_1m
    output_cost = (completion_tokens / 1_000_000) * output_cost_per_1m
    return round(input_cost + output_cost, 8)


def ensure_metrics_file(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "timestamp",
                "tokens_prompt",
                "tokens_completion",
                "total_tokens",
                "latency_ms",
                "estimated_cost_usd",
            ]
        )


def append_metrics(path: Path, metrics: UsageMetrics) -> None:
    ensure_metrics_file(path)
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                metrics.timestamp,
                metrics.tokens_prompt,
                metrics.tokens_completion,
                metrics.total_tokens,
                metrics.latency_ms,
                f"{metrics.estimated_cost_usd:.8f}",
            ]
        )
