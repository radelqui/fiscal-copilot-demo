# Verification Evidence — ORDEN REGISTRY SOLO DEMO

## Date: 2026-07-07

## What changed
- Created /home/sypnose/.registry/backstage-api/public/demo.html — dedicated single-project page
- Updated /home/sypnose/.registry/backstage-api/server.js — added /demo route
- Updated catalog-info.yaml — description in Spanish

## Verification

### R1: Display Name
```
curl localhost:7009/demo | grep "Cómo Estoy Hecho" → 1 match
```

### R2: Isolation
```
curl localhost:7009/demo | grep -ci "stratos|eagleview|postiz|..." → 0 matches
```

### R3: Content
```
/multi/deep/fiscal-copilot → 383 nodes, 481 edges
/codegraph/file-content → works (lines: 36, size: 869 for app/main.py)
```

### R4: Sanity
- Demo page only calls /multi/deep/fiscal-copilot and /codegraph/file-content
- No /registry/, /api/, /multi/projects, /multi/topology calls
- No search functionality

### URL for interviewer
https://registry.sypnose.cloud/demo

### No Cloudflare changes needed
Cloudflare already routes registry.sypnose.cloud → localhost:7009
The /demo route is served by Express static + explicit route

## Verdict: PASS
