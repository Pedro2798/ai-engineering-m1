from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from src.core import UsageMetrics, append_metrics, estimate_cost_usd, parse_json_output, utc_timestamp, validate_contract
from src.safety import SafetyDecision, assess_prompt_risk, build_safe_fallback

ROOT_DIR = Path(__file__).resolve().parents[1]
PROMPT_PATH = ROOT_DIR / "prompts" / "main_prompt.md"
METRICS_PATH = ROOT_DIR / "metrics" / "metrics.csv"


def load_prompt_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"No se encontro el prompt en: {path}")
    return path.read_text(encoding="utf-8")


def build_messages(prompt_template: str, question: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": question},
    ]


def call_openai(
    question: str, prompt_template: str, model_name: str, client: OpenAI
) -> tuple[dict[str, Any], int, int, int]:
    completion = client.chat.completions.create(
        model=model_name,
        messages=build_messages(prompt_template, question),
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    raw_content = completion.choices[0].message.content or "{}"
    payload = parse_json_output(raw_content)
    usage = completion.usage
    prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
    completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
    total_tokens = int(getattr(usage, "total_tokens", prompt_tokens + completion_tokens) or 0)
    return payload, prompt_tokens, completion_tokens, total_tokens


def run(question: str, model_name: str, mock_mode: bool = False) -> dict[str, Any]:
    start = time.perf_counter()
    decision: SafetyDecision = assess_prompt_risk(question)

    if decision.is_blocked:
        payload = build_safe_fallback(decision)
        prompt_tokens = completion_tokens = total_tokens = 0
    elif mock_mode:
        payload = {
            "answer": "Para resolverlo, verifica datos del cliente y confirma el estado del ticket.",
            "confidence": 0.83,
            "actions": ["Validar identidad", "Revisar historial", "Responder con siguientes pasos"],
            "safety": {"blocked": False, "risk_score": decision.risk_score, "reason": decision.reason},
            "meta": {"status": "ok_mock", "model": model_name},
        }
        prompt_tokens, completion_tokens, total_tokens = 120, 60, 180
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            payload = {
                "answer": "Falta configurar OPENAI_API_KEY para ejecutar la consulta.",
                "confidence": 0.0,
                "actions": ["Configura OPENAI_API_KEY en variables de entorno", "Reintenta la ejecucion"],
                "safety": {"blocked": False, "risk_score": decision.risk_score, "reason": decision.reason},
                "meta": {"status": "missing_api_key"},
            }
            prompt_tokens = completion_tokens = total_tokens = 0
        else:
            prompt_template = load_prompt_template(PROMPT_PATH)
            client = OpenAI(api_key=api_key)
            payload, prompt_tokens, completion_tokens, total_tokens = call_openai(
                question=question, prompt_template=prompt_template, model_name=model_name, client=client
            )
            payload.setdefault(
                "safety",
                {"blocked": False, "risk_score": decision.risk_score, "reason": decision.reason},
            )
            payload.setdefault("meta", {"status": "ok", "model": model_name})

    is_valid, error_message = validate_contract(payload)
    if not is_valid:
        payload = {
            "answer": f"Respuesta invalida del modelo: {error_message}",
            "confidence": 0.0,
            "actions": ["Revisar prompt", "Reintentar consulta", "Inspeccionar salida del modelo"],
            "safety": {"blocked": False, "risk_score": decision.risk_score, "reason": decision.reason},
            "meta": {"status": "invalid_model_output", "model": model_name},
        }

    latency_ms = int((time.perf_counter() - start) * 1000)
    estimated_cost_usd = estimate_cost_usd(prompt_tokens, completion_tokens)
    append_metrics(
        METRICS_PATH,
        UsageMetrics(
            tokens_prompt=prompt_tokens,
            tokens_completion=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            estimated_cost_usd=estimated_cost_usd,
            timestamp=utc_timestamp(),
        ),
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multitasking Text Utility (JSON output)")
    parser.add_argument("--question", required=True, help="Pregunta del usuario")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), help="Modelo de OpenAI")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Ejecuta sin llamar API (para demo/tests locales).",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    payload = run(question=args.question, model_name=args.model, mock_mode=args.mock)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
