## Verificacion: ORDEN-NOTEBOOK-FLUJO N1 — Open Notebook Local

**Fecha**: 2026-07-07

### Evidencia docker ps
```
NAMES                           STATUS                 PORTS
open-notebook-open_notebook-1   Up About a minute      0.0.0.0:5055->5055/tcp, 0.0.0.0:8502->8502/tcp
open-notebook-surrealdb-1       Up About a minute      0.0.0.0:8000->8000/tcp
```

### Evidencia curl :8502
```
HTTP 200 (Streamlit UI, 1522 bytes)
```

### Evidencia curl :5055
```
GET /health → {"status":"healthy"}
GET /api/notebooks → [{id: "notebook:mb786ov6775hht3we70l", name: "Fiscal Copilot — Meta-Demo"}]
```

### Notebook creado
- ID: notebook:mb786ov6775hht3we70l
- Nombre: Fiscal Copilot — Meta-Demo
- Sources: 25 documentos (docs/ + meta-corpus/ + README.md), 0 failed
- Total: ~145,000 chars de contenido

### Infraestructura
- docker-compose.yml: /home/sypnose/open-notebook/docker-compose.yml
- Volumes: surreal_data/ + notebook_data/
- Systemd: open-notebook.service (enabled, auto-start)
- SurrealDB creds: root/opennotebook

### Resultado
what_changed: "Open Notebook instalado con Docker, notebook fiscal-copilot con 25 docs, systemd habilitado"
how_verified: "docker ps muestra ambos containers Up, curl :8502 HTTP 200, curl :5055/health healthy, API devuelve notebook con 25 sources"
result: "Open Notebook operativo en :8502 (UI) + :5055 (API), notebook fiscal-copilot listo con 25 fuentes"
