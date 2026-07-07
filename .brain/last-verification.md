## Verificacion: ORDEN-REGISTRY-POLISH (P1 + P2 + P4)

**Fecha**: 2026-07-07
**Orden**: ORDEN-REGISTRY-POLISH — Time-slider web + Export digest + Server-sync bundle

### P1 — Time-Slider Web

1. **snapshot-history.py** ejecutado: 19 scans, 204388 change_events, 19 projects
2. **API endpoints verificados**:
```
GET /history/scans/fiscal-copilot → { count: 1, scans: [{scan_id:11, ts:"2026-07-07T01:42:18Z", node_count:821, edge_count:1145}] }
GET /history/snapshot/11 → Nodes: 821, Edges: 1145
GET /history/changes/11 → Changes: 1966
```
3. **UI time-slider** integrado en index.html (CSS lines 751-813, HTML line 974, JS lines 2087-2182)
4. **registry-build.sh** FASE 4.5 run_snapshots integrada (line 307, 388)

### P2 — Export Digest Web

1. **Endpoint verificado**:
```
GET /multi/digest/fiscal-copilot → 128 lines Markdown
Content: Overview, Code Structure, API Routes, File Tree
Content-Disposition: attachment; filename="fiscal-copilot-digest.md"
```
2. **Download button** en index.html line 1233 (buildCGDetail)
3. **downloadDigest()** function en index.html line 2000

### P4 — Server-Sync Bundle

1. **Bundle creado**: /tmp/registry-server-sync.bundle (3.5MB)
2. **Branch**: server-sync en ~/repos/registry-v22/ (3 commits):
```
5190faf feat: history snapshots — snapshot-history.py, seed-history.py, FASE 4.5 in build
86c110f feat: web UI — file viewer modal, download digest button, time-slider
a5b92cf feat: server routes — codegraph null-safety, file-content endpoint, history route
```
3. **No push a GitHub** (verificado)

### Registry API health
```
GET /health → {"status":"ok","services":3,"registry":true,"fleet":false}
```

### Resultado
what_changed: "P1 time-slider (scripts + API + UI), P2 digest endpoint + button, P4 server-sync bundle 3.5MB"
how_verified: "curl a 5 endpoints con output real + ls bundle + git log server-sync + grep UI components"
result: "19 projects en history.db, 3 API endpoints OK, UI slider + digest button integrados, bundle listo en /tmp"
