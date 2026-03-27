# PI Report - Multitasking Text Utility

## 1) Arquitectura breve

El sistema se implementa como una utilidad CLI en Python (`src/run_query.py`) con tres capas:

1. **Entrada y orquestacion**  
   Recibe `--question`, carga entorno, ejecuta seguridad, llama al modelo (o mock), valida contrato y persiste metricas.

2. **Contrato y observabilidad** (`src/core.py`)  
   - Parsing/validacion de JSON con campos obligatorios (`answer`, `confidence`, `actions`).  
   - Calculo de costo estimado USD desde tokens de uso.  
   - Registro en `metrics/metrics.csv`.

3. **Seguridad** (`src/safety.py`)  
   - Deteccion heuristica de prompts adversariales.  
   - Fallback seguro sin romper el contrato JSON.

## 2) Tecnica de prompting usada y por que

Se eligio **few-shot prompting** en `prompts/main_prompt.md`:
- define esquema JSON esperado;
- incluye ejemplos concretos de casos de soporte;
- restringe salida a JSON puro.

Motivo de eleccion: en asistentes de soporte, la prioridad es confiabilidad estructural para integraciones downstream. Few-shot ayuda a reducir variabilidad de formato con bajo costo de implementacion.

## 3) Metricas capturadas

Por cada ejecucion:
- `tokens_prompt`
- `tokens_completion`
- `total_tokens`
- `latency_ms`
- `estimated_cost_usd`
- `timestamp`

Persistencia: `metrics/metrics.csv` (append por consulta).

## 4) Resultados de muestra

Se registraron ejecuciones de ejemplo:

- Consulta normal (`--mock`): salida JSON valida con `confidence=0.83`.  
- Consulta adversarial (`--mock`, intento de prompt injection): bloqueada por seguridad con fallback.

Ejemplo de decision adversarial:
- `blocked=true`
- `risk_score=0.7`
- `reason=\"Prompt potencialmente adversarial detectado.\"`

## 5) Trade-offs y desafios

1. **Costo vs robustez**  
   Se usa `gpt-4o-mini` para mantener costo bajo, aceptando menor capacidad que modelos mas grandes.

2. **JSON estricto vs expresividad**  
   Forzar contrato mejora integracion, pero limita respuestas extensas del modelo.

3. **Seguridad heuristica vs moderacion completa**  
   La heuristica actual es rapida y simple, pero no cubre todos los ataques.

## 6) Mejoras futuras

- Añadir moderacion de entrada/salida con endpoint dedicado.
- Migrar de heuristicas a clasificador de riesgo por contexto.
- Incorporar retries con validacion de esquema mas estricta (pydantic/jsonschema).
- Agregar dashboards de metricas y trazabilidad por request_id.
