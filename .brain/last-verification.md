# Verificación: Registry v2.2 Update

## Fecha: 2026-07-07
## Tarea: ORDEN-REGISTRY-V22

## Qué cambió
- scanner.py, classifier.py, registry-build.sh actualizados de v2.2
- codegraph.js: null-safety + endpoint /codegraph/file-content + ESM fix
- index.html: file viewer modal con click en archivos del code graph

## Evidencia

### Health (200 OK)
```json
{"status":"ok","services":3,"registry":true,"fleet":false}
```

### File viewer endpoint (200 + contenido)
```
$ curl "http://localhost:7009/codegraph/file-content?path=/home/sypnose/proyectos/fiscal-copilot/app/main.py"
{"path":"/home/sypnose/proyectos/fiscal-copilot/app/main.py","size":863,"lines":36,"content":"import logging..."}
```

### Seguridad (403 para path traversal)
```
$ curl "http://localhost:7009/codegraph/file-content?path=/etc/passwd"
{"error":"Access denied: path must be under /home/sypnose/"}

$ curl "http://localhost:7009/codegraph/file-content?path=/home/sypnose/../../etc/passwd"
{"error":"Access denied: path must be under /home/sypnose/"}
```

### Topology preservada (12 proyectos)
```
$ curl http://localhost:7009/multi/topology → Projects: 12
```

### Codegraph disponible
```json
{"available":true,"endpoints":["/routes","/routes-with-tables","/route/:path","/summary","/file-content"]}
```

### Frontend (file viewer integrado)
```
file-viewer-modal: 7 occurrences
openFileViewer: 2 occurrences
```

## Resultado: PASS
