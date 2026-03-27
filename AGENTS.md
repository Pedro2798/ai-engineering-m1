# Contexto de trabajo del proyecto

## Objetivo de producto
- Construir una utilidad de texto multitarea que reciba una pregunta y devuelva JSON estable para sistemas downstream.
- Registrar métricas por consulta para control operativo (tokens, latencia, costo estimado).
- Mantener una capa de seguridad básica para prompts adversariales.

## Principios de ingeniería (SOLID + buenas prácticas)
- Single Responsibility: cada modulo tiene una responsabilidad clara (`run_query`, `safety`, `prompts`, `metrics`).
- Open/Closed: reglas de seguridad y precios deben extenderse por configuracion, no por cambios invasivos.
- Liskov + Interface Segregation: funciones puras y contratos de entrada/salida simples (tipos basicos + dicts tipados).
- Dependency Inversion: dependencias externas (cliente OpenAI, reloj) deben inyectarse cuando sea posible para testeo.
- Funciones pequenas y legibles; evitar logica monolitica.
- Errores explicitos y controlados: nunca romper el contrato JSON de salida.
- Logging util y no verboso, sin exponer secretos.

## Contrato JSON obligatorio
- Campos minimos de salida:
  - `answer`: string
  - `confidence`: float entre 0 y 1
  - `actions`: lista de strings
  - `safety`: objeto con decision de seguridad
  - `meta`: objeto con modelo y estado
- Si ocurre error, responder JSON valido con fallback seguro.

## Criterios de calidad por cambio
- Codigo ejecutable localmente con pasos documentados en `README.md`.
- Al menos un test automatizado pasando.
- Sin secretos en repositorio (`OPENAI_API_KEY` solo por entorno).
- Formato de metricas consistente en `metrics/metrics.csv`.
- Documentacion sincronizada entre README y reporte.

## Definicion de Done por etapa
- Existe artefacto verificable del paso (archivo, test o salida).
- Hay criterio de validacion medible y evidenciable.
- No se introduce deuda tecnica evidente (duplicacion excesiva o funciones largas sin necesidad).
