from src.core import estimate_cost_usd, validate_contract


def test_validate_contract_ok() -> None:
    payload = {
        "answer": "Respuesta",
        "confidence": 0.72,
        "actions": ["Accion 1", "Accion 2"],
    }
    is_valid, error = validate_contract(payload)
    assert is_valid is True
    assert error is None


def test_estimate_cost_usd() -> None:
    result = estimate_cost_usd(prompt_tokens=1000, completion_tokens=500)
    assert result > 0
    assert round(result, 8) == 0.00045
