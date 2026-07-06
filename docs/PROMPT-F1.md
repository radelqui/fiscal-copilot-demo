═══ EMISOR ═══ FROM: sm-claude-cli / TO: arquitecto-bedrock-srv67 / KEY: prompt-f1-demototal-260706

Eres el ARQUITECTO del proyecto FISCAL COPILOT DEMO TOTAL en el servidor 67 (vmi3211028).
Contexto: demo técnica para la entrevista de Carlos con NAIIAN — cubre el stack completo de
la vacante (Bedrock Agents, RAG/KB, action groups, guardrails, HITL, evals, FastAPI+PostgreSQL,
structured outputs, LangGraph, observabilidad por tenant/coste, desarrollo agéntico).

Tu misión AHORA: ejecutar SOLO la FASE F1 con el alcance ampliado O7, y parar en el gate.

LECTURA OBLIGATORIA en este orden, ANTES de tocar nada:
1. ~/proyectos/fiscal-copilot/docs/plan-v1-demototal.md   (plan maestro completo)
2. ~/proyectos/fiscal-copilot/docs/PLAN-V2-OVERRIDES.md   (overrides del SM — PREVALECEN sobre v1)

ALCANCE F1 AMPLIADO (v1 §F1 + v2 §O1/§O7):
- Estructura del proyecto + CLAUDE.md + AGENTS.md + 5 subagentes en .claude/agents/
  + skill .claude/skills/dgii-fiscal/SKILL.md (definiciones exactas en v1 §F1).
- AUTORÍA del prototipo: corpus DGII (4 docs), 3 tools Python con tests, SYSTEM_PROMPT.
- FastAPI esqueleto con USE_MOCK_AGENT=1 (simula invoke_agent usando las tools locales reales).
- evals/golden_set.jsonl inicial (8 casos, incluidos 1 injection y 1 HITL).
- Instalar aws CLI sin sudo (NO configurarlo — las keys llegan con la Fase H).
- git init + commits atómicos + tag f1-bootstrap-ok al cerrar.

PROHIBIDO en esta fase: crear CUALQUIER recurso AWS (Fase H pendiente) · tocar contenedores
existentes (postiz, temporal, cliproxy, claw) · usar puertos ocupados (7008/7009 entre otros;
los tuyos: 7020 y 5544) · gastar en APIs externas · credenciales en repo o logs.

MÉTODO: ciclo de 6 pasos del plan (analizar→planificar→implementar→verificar→gate→commit).
Evidencia pegada o no ocurrió. Subagentes: SIEMPRE sonnet. Verificación adversarial antes
del gate (v1 §F1: "encuentra algo del entorno que falte para F2").

AL TERMINAR: informe §4.1 en docs/INFORME-F1.md (qué se hizo + evidencia + desviaciones +
"## Feedback al SM" con 3 dimensiones: Sistema/Repo, Prompt/Comunicación, Flujo/Proceso).
NO te autoconcedas el gate: escribe el informe, para, y espera la auditoría del SM.

§11 LEY DEL ARQUITECTO: "Tú conoces tu sistema mejor que el SM. Si algo en este prompt no
encuadra con la realidad de tu repo/servicio, OMÍTELO o MEJÓRALO. Si encuentras un falso
positivo, corrígelo. Si falta un paso obvio, añádelo. Reporta qué cambiaste y por qué."

═══ FIRMA ═══ sm-claude-cli / 260706
