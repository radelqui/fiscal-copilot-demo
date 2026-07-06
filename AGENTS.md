# AGENTS.md — Fiscal Copilot

## Convenciones de desarrollo agéntico

Este proyecto se desarrolla con Claude Code y subagentes especializados.
Cada agente tiene un rol definido y reglas estrictas.

### Agentes disponibles

| Agente | Archivo | Rol | Cuándo usar |
|--------|---------|-----|-------------|
| analizador | .claude/agents/analizador.md | Read-only recon | ANTES de tocar cualquier código |
| verificador-adversarial | .claude/agents/verificador-adversarial.md | Refutar cambios | DESPUÉS de implementar |
| aws-deployer | .claude/agents/aws-deployer.md | Crear/borrar recursos AWS | Solo en fases con infra AWS |
| backend-dev | .claude/agents/backend-dev.md | FastAPI/PostgreSQL/LangGraph | Código de aplicación |
| evals-engineer | .claude/agents/evals-engineer.md | Evals y comparativas | Golden set, harness, Ragas, DeepEval |

### Reglas de anti-colisión
- Un dueño por archivo por fase
- aws/ y recursos cloud → aws-deployer
- app/ → backend-dev
- evals/ y reports/ → evals-engineer
- specs/, AGENTS.md, README → arquitecto directo
- NUNCA 2 agentes al mismo archivo en paralelo

### Comandos
```bash
# Invocar un agente (Claude Code CLI)
claude /agents

# Ver agentes disponibles
ls .claude/agents/
```

### Flujo de trabajo
1. **Analizar**: lanzar analizador(es) en paralelo, read-only
2. **Implementar**: backend-dev o aws-deployer según el área
3. **Verificar**: 3 verificadores-adversariales en paralelo con lentes distintas
4. **Gate**: evidencia pegada o no pasó
