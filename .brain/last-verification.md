# Verificación: click tooltips en diagrama Mermaid

## Fecha: 2026-07-07
## Commit: d5d9ccb

## Qué cambió
- 17 `click` statements añadidos al diagrama Mermaid en `app/static/architecture.html`
- `securityLevel: 'loose'` en `mermaid.initialize()` para habilitar click events

## Evidencia

### Tests (84/84 passed)
```
84 passed, 1 warning in 1.40s
```

### Curl /architecture (200 con token válido)
```
$ curl -s "http://localhost:7020/demo/1a9b6ff25f5c485ab502d34a/architecture" | head -5
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Fiscal Copilot — Arquitectura</title>
```

### 401 sin token
```
$ curl -s -o /dev/null -w "%{http_code}" "http://localhost:7020/demo/invalid-token/architecture"
401
```

### Click statements verificados
```
$ grep -c "click " app/static/architecture.html
17
```

## Resultado: PASS
