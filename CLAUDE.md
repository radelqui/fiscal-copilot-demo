# Fiscal Copilot — Demo Total (NAIIAN)

## Proyecto
Demo técnica de agente fiscal dominicano sobre AWS Bedrock para entrevista.
Stack: Bedrock Agents + KB + Action Groups + Guardrails + HITL + FastAPI + PostgreSQL + LangGraph + Evals.

## Región AWS
eu-central-1 (Frankfurt). Inference profiles: `eu.anthropic.claude-*`.
Servidor 67 está en Alemania → latencia ~5ms. GDPR como argumento de entrevista.

## Presupuesto
$15 máximo de $100 en créditos. Gate de coste INFORMA pero no detiene (orden de Carlos).

## Puertos
- 7020: FastAPI (este proyecto)
- 5544: PostgreSQL demo (este proyecto)
- 7008/7009: OCUPADOS (no tocar)

## Comandos frecuentes
```bash
make test          # pytest
make evals         # evals/run_all.py
make demo          # demo/demo_10min.sh
make serve         # uvicorn app.main:app --port 7020
```

## Variables de entorno
```bash
source ~/.env-demototal   # AWS keys + OPENAI_API_KEY
export USE_MOCK_AGENT=1   # Simula invoke_agent con tools locales (dev)
```

## Reglas de oro
1. Ciclo 6 pasos siempre: analizar→planificar→implementar→verificar→gate→commit
2. Sin evidencia no hay gate
3. Solo S3 Vectors (PROHIBIDO OpenSearch Serverless)
4. Solo eu-central-1 (salvo fallback documentado)
5. Solo recursos listados en el plan
6. Credenciales JAMÁS en repo ni logs
7. Grep de secretos antes de cada commit/push
8. Coste pegado en cada gate con recursos AWS
9. Sub-agentes: SIEMPRE sonnet

## PROHIBIDO
- OpenSearch Serverless
- Credenciales en repo o logs
- Recursos fuera de eu-central-1 sin justificación
- Tocar contenedores existentes (postiz, temporal, cliproxy, claw)
- Puertos 7008/7009
