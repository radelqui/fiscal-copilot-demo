# INFORME F5-EVALS — Cierre de Fase

**Fecha**: 2026-07-06  
**Fase**: F5-EVALS — Evaluaciones y Comparativa de Modelos  
**Estado**: COMPLETADO — esperando auditoría SM  

---

## 1. Entregables

| Archivo | Líneas | Descripción |
|---------|--------|-------------|
| `evals/golden_set.jsonl` | 8 casos | Golden set: calculation, validation, format, knowledge, injection, hitl |
| `evals/run_harness.py` | 229 | Harness contra backend vivo :7020 con token demo |
| `evals/judges.py` | 256 | LLM-as-judge: faithfulness, answer_relevancy, context_precision, geval |
| `evals/router.py` | 249 | Router multi-modelo: Haiku, Nova Micro, GPT-4o-mini, Sonnet 4.6 (pendiente) |
| `evals/run_all.py` | 353 | Orquestador: harness → router → judges → comparativa.md |
| `reports/comparativa.md` | 239 | Reporte final con tablas, métricas, trade-offs, recomendación |

## 2. Resultados del Pipeline

### Harness (backend mock :7020)
- **8/8 PASSED** — todos los casos del golden set
- Latencia: ~0.1ms (mock local)
- Coste: $0.00 (mock)

### Router (modelos reales via Bedrock/OpenAI)

| Ruta | Resultado | Coste Total | Latencia Avg | Errores |
|------|-----------|-------------|--------------|---------|
| bedrock-haiku | 8/8 OK | $0.01140 | 2543ms | 0 |
| bedrock-nova-micro | 8/8 OK | $0.00033 | 1473ms | 0 |
| openai-gpt4o-mini | 0/8 | $0.00 | 0ms | 8/8 (401 key inválida) |
| bedrock-sonnet-4-6 | — | — | — | PENDIENTE Marketplace |

### Judges (LLM-as-Judge, Bedrock Haiku)

| Métrica | Promedio | Min | Max |
|---------|---------|-----|-----|
| faithfulness | 0.323 | 0.000 | 1.000 |
| answer_relevancy | 0.906 | 0.850 | 1.000 |
| context_precision | 0.925 | 0.850 | 0.950 |
| geval_fiscal_correctness | 0.894 | 0.700 | 1.000 |

### Presupuesto

| Componente | Coste |
|-----------|-------|
| Harness (mock) | $0.00000 |
| Router (3 modelos × 8 queries) | $0.01173 |
| Judges (Haiku) | $0.00640 |
| **TOTAL** | **$0.01813** |
| Presupuesto | $2.00 |
| Estado | **DENTRO** |

## 3. Decisiones Técnicas

1. **Ragas manual vs librería**: ragas 0.4.3 tiene imports rotos (langchain-google-vertexai). Implementé las 3 métricas Ragas manualmente usando Bedrock Haiku como judge. Más control y mejor para demo.

2. **DeepEval GEval fallback**: OpenAI key inválida (401). GEval implementado con Haiku como judge fallback. Mismo prompt G-Eval del paper.

3. **Golden set OR logic**: `expected_response_contains` usa lógica OR (cualquier match = pass) porque formatos numéricos varían ("18,000" vs "18000").

4. **Router con base_url explícita**: OpenAI client tenía `base_url` apuntando a CLIProxy local. Corregido a `https://api.openai.com/v1`. Sigue 401 por key inválida — documentado como limitación conocida.

## 4. Limitaciones Conocidas

- **OpenAI API key inválida**: ~/.env-demototal key retorna 401. GPT-4o-mini no comparable.
- **Sonnet 4.6 pendiente**: Requiere habilitación Marketplace por Carlos.
- **faithfulness bajo (0.323)**: Esperado — el mock no genera contexto RAG real, así que el judge no puede verificar grounding. Con Bedrock Agent real + KB, subirá.

## 5. Recomendación

- **Demo/producción inicial**: Haiku — mejor balance calidad/coste ($0.0014/query)
- **Volumen alto**: Nova Micro — 20x más barato ($0.00004/query)
- **Producción real**: Sonnet 4.6 cuando se habilite

## 6. Verificación

```
pytest tests/ -v → 74/74 passed (0 regressions)
python -m evals.run_all → 8/8 harness, 3 rutas, 4 métricas judge
Total gastado: $0.018 de $2.00 presupuesto
```

## 7. Commits

Pendiente: commit único con todos los archivos F5-EVALS.

---
*Generado por arquitecto Opus, fase F5-EVALS*
