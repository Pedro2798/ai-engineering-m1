from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

ADVERSARIAL_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"system\s+prompt",
    r"reveal\s+hidden\s+prompt",
    r"bypass\s+safety",
    r"disable\s+guardrails",
]


@dataclass(frozen=True)
class SafetyDecision:
    is_blocked: bool
    risk_score: float
    reason: str


def assess_prompt_risk(user_question: str) -> SafetyDecision:
    text = user_question.lower()
    hits = sum(bool(re.search(pattern, text)) for pattern in ADVERSARIAL_PATTERNS)
    risk_score = min(1.0, hits * 0.35)
    if risk_score >= 0.7:
        return SafetyDecision(
            is_blocked=True,
            risk_score=risk_score,
            reason="Prompt potencialmente adversarial detectado.",
        )
    return SafetyDecision(
        is_blocked=False,
        risk_score=risk_score,
        reason="Sin indicadores criticos de adversarialidad.",
    )


def build_safe_fallback(decision: SafetyDecision) -> dict[str, Any]:
    return {
        "answer": "No puedo procesar esa solicitud de forma segura.",
        "confidence": 0.0,
        "actions": [
            "Reformula tu consulta sin pedir revelar instrucciones internas.",
            "Solicita ayuda sobre un caso de soporte especifico.",
        ],
        "safety": {
            "blocked": decision.is_blocked,
            "risk_score": decision.risk_score,
            "reason": decision.reason,
        },
        "meta": {"status": "blocked_by_safety"},
    }
