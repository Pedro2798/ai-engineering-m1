# Multitasking Text Utility (JSON Assistant)

Utilidad CLI en Python para soporte al cliente. Recibe una pregunta y devuelve JSON valido con:
- `answer`
- `confidence`
- `actions`

Adicionalmente registra metricas por ejecucion:
- `tokens_prompt`
- `tokens_completion`
- `total_tokens`
- `latency_ms`
- `estimated_cost_usd`

## Estructura

- `src/run_query.py`: script ejecutable principal.
- `src/safety.py`: deteccion basica de prompts adversariales + fallback.
- `src/core.py`: validacion de contrato JSON, costo y metricas.
- `prompts/main_prompt.md`: prompt principal con tecnica few-shot.
- `metrics/metrics.csv`: log de metricas por consulta.
- `tests/test_core.py`: pruebas automatizadas.
- `reports/PI_report_en.md`: reporte breve de arquitectura/resultados.
- `.env.example`: variables de entorno requeridas.

## Requisitos

- Python 3.10+ (probado en Python 3.13)
- Cuenta OpenAI + API key

## Setup

```bash
python -m pip install -r requirements.txt
```

Copia `.env.example` a `.env` y define:

```bash
OPENAI_API_KEY=tu_api_key
OPENAI_MODEL=gpt-4o-mini
```

## Ejecutar

### 1) Ejecucion real (API OpenAI)

```bash
python -m src.run_query --question "No puedo acceder a mi cuenta"
```

### 2) Ejecucion local sin API (mock)

```bash
python -m src.run_query --question "Tengo un cargo duplicado en mi factura" --mock
```

La salida siempre es JSON y las metricas se agregan a `metrics/metrics.csv`.

## Tecnica de prompt engineering aplicada

Se usa **few-shot prompting** en `prompts/main_prompt.md`:
- define un esquema JSON estricto;
- incluye ejemplos de soporte tecnico y billing;
- obliga a no generar texto fuera del JSON.

Esta tecnica mejora consistencia estructural en respuestas downstream.

## Seguridad (bonus)

`src/safety.py` aplica una heuristica de riesgo adversarial (patrones tipo *ignore previous instructions*).  
Si el riesgo supera el umbral, se bloquea la consulta y se devuelve fallback JSON seguro.
Ademas, cada evaluacion de seguridad se registra en `metrics/safety_decisions.csv` con:
- `timestamp`
- `question_hash` (SHA-256 de la consulta)
- `blocked`
- `risk_score`
- `reason`

## Tests

```bash
python -m pytest -q
```

## Reproducir metricas

1. Ejecuta una o mas consultas (real o `--mock`).
2. Revisa `metrics/metrics.csv`.
3. Verifica columnas:
   - `timestamp`
   - `tokens_prompt`
   - `tokens_completion`
   - `total_tokens`
   - `latency_ms`
   - `estimated_cost_usd`

## Limitaciones conocidas

- El costo estimado usa una tabla fija de precios en codigo y puede quedar desactualizada.
- La capa de seguridad es heuristica; no reemplaza un pipeline de moderacion completo.
- En modo `--mock` los tokens son simulados para facilitar pruebas locales.
