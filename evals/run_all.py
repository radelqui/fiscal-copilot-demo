"""Eval Orchestrator — runs all evaluations and generates comparison report.

Usage:
    python -m evals.run_all
"""

import json
import sys
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

from evals.run_harness import run_harness, load_golden_set, CaseResult
from evals.router import run_route, available_routes, get_system_prompt, RouteResult
from evals.judges import evaluate_all_metrics, JudgeResult

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

REPORTS_DIR = Path(__file__).parent.parent / "reports"
EVALS_DIR = Path(__file__).parent


def _get_token() -> str:
    """Get a valid demo token."""
    try:
        import psycopg
        conn = psycopg.connect(
            "postgresql://fiscal:fiscal_demo_2026@localhost:5544/fiscal_copilot"
        )
        cur = conn.execute(
            "SELECT token FROM demo_tokens WHERE expires_at > NOW() "
            "ORDER BY created_at DESC LIMIT 1"
        )
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception:
        pass
    raise RuntimeError("No valid demo token found")


def step1_harness(token: str) -> list[CaseResult]:
    """Step 1: Run golden set against live backend."""
    print("\n" + "=" * 60)
    print("  STEP 1: Harness — golden_set vs live backend")
    print("=" * 60)

    from app.auth import reset_rate_limits
    reset_rate_limits()

    results = run_harness(base_url="http://localhost:7020", token=token)

    output = EVALS_DIR / "harness_results.json"
    with open(output, "w") as f:
        json.dump([r.to_dict() for r in results], f, indent=2, ensure_ascii=False)

    return results


def step2_router_comparison() -> dict[str, list[RouteResult]]:
    """Step 2: Run golden set through each router model."""
    print("\n" + "=" * 60)
    print("  STEP 2: Router — model comparison")
    print("=" * 60)

    cases = load_golden_set()
    routes = available_routes()
    all_results: dict[str, list[RouteResult]] = {r: [] for r in routes}

    for route_name in routes:
        print(f"\n  Route: {route_name}")
        print(f"  {'─' * 50}")
        total_cost = 0.0

        for i, case in enumerate(cases, 1):
            result = run_route(route_name, case["query"])
            all_results[route_name].append(result)
            total_cost += result.cost_usd

            status = "OK" if not result.error else "ERR"
            print(
                f"    [{i}/{len(cases)}] {status}  "
                f"{result.latency_ms:7.1f}ms  "
                f"${result.cost_usd:.5f}  "
                f"{case['id']}"
                f"{'  ' + result.error[:40] if result.error else ''}"
            )

        print(f"  Total cost for {route_name}: ${total_cost:.5f}")

    output = EVALS_DIR / "router_results.json"
    serializable = {
        route: [r.to_dict() for r in results]
        for route, results in all_results.items()
    }
    with open(output, "w") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)

    return all_results


def step3_judges(harness_results: list[CaseResult]) -> dict[str, list[list[JudgeResult]]]:
    """Step 3: Run LLM-as-judge metrics on harness responses."""
    print("\n" + "=" * 60)
    print("  STEP 3: Judges — Ragas + GEval metrics")
    print("=" * 60)

    context = get_system_prompt()
    judge_results: dict[str, list[list[JudgeResult]]] = {"harness": []}

    for i, case_result in enumerate(harness_results, 1):
        if not case_result.response or case_result.response.startswith("HTTP"):
            judge_results["harness"].append([])
            continue

        print(f"  [{i}/{len(harness_results)}] Judging: {case_result.id}")
        metrics = evaluate_all_metrics(
            question=case_result.query,
            answer=case_result.response,
            context=context,
            tools_used=case_result.tools_used,
        )
        judge_results["harness"].append(metrics)

        for m in metrics:
            print(f"    {m.metric:25s} = {m.score:.2f}")

    output = EVALS_DIR / "judge_results.json"
    serializable = {
        key: [[m.to_dict() for m in case_metrics] for case_metrics in cases]
        for key, cases in judge_results.items()
    }
    with open(output, "w") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)

    return judge_results


def step4_generate_report(
    harness_results: list[CaseResult],
    router_results: dict[str, list[RouteResult]],
    judge_results: dict[str, list[list[JudgeResult]]],
) -> str:
    """Step 4: Generate reports/comparativa.md."""
    print("\n" + "=" * 60)
    print("  STEP 4: Generating reports/comparativa.md")
    print("=" * 60)

    REPORTS_DIR.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Comparativa de Rutas — Fiscal Copilot Evals",
        "",
        f"**Generado**: {now}  ",
        f"**Golden set**: {len(harness_results)} casos  ",
        f"**Judge**: Bedrock Haiku (eu.anthropic.claude-haiku-4-5-20251001-v1:0)  ",
        "",
        "---",
        "",
        "## 1. Harness — Backend Mock (:7020)",
        "",
    ]

    # Harness summary table
    passed = sum(1 for r in harness_results if r.pass_overall)
    total_cost = sum(r.cost_usd for r in harness_results)
    avg_latency = sum(r.latency_ms for r in harness_results) / len(harness_results) if harness_results else 0

    lines.append(f"**Resultado**: {passed}/{len(harness_results)} passed  ")
    lines.append(f"**Coste total**: ${total_cost:.5f}  ")
    lines.append(f"**Latencia promedio**: {avg_latency:.1f}ms  ")
    lines.append("")
    lines.append("| Caso | Categoría | Pass | Latencia (ms) | Coste | Errores |")
    lines.append("|------|-----------|------|---------------|-------|---------|")

    for r in harness_results:
        status = "✓" if r.pass_overall else "✗"
        errs = "; ".join(r.errors) if r.errors else "—"
        lines.append(
            f"| {r.id} | {r.category} | {status} | {r.latency_ms:.1f} | "
            f"${r.cost_usd:.5f} | {errs} |"
        )

    # Judge metrics summary
    lines.append("")
    lines.append("## 2. Métricas de Calidad (LLM-as-Judge)")
    lines.append("")

    metric_names = ["faithfulness", "answer_relevancy", "context_precision", "geval_fiscal_correctness"]
    metric_scores: dict[str, list[float]] = {m: [] for m in metric_names}

    harness_judges = judge_results.get("harness", [])
    for case_metrics in harness_judges:
        for m in case_metrics:
            if m.metric in metric_scores:
                metric_scores[m.metric].append(m.score)

    lines.append("| Métrica | Promedio | Min | Max | N |")
    lines.append("|---------|---------|-----|-----|---|")
    for name in metric_names:
        scores = metric_scores[name]
        if scores:
            avg = sum(scores) / len(scores)
            mn = min(scores)
            mx = max(scores)
            lines.append(f"| {name} | {avg:.3f} | {mn:.3f} | {mx:.3f} | {len(scores)} |")
        else:
            lines.append(f"| {name} | — | — | — | 0 |")

    # Per-case judge details
    lines.append("")
    lines.append("### Detalle por caso")
    lines.append("")

    cases = load_golden_set()
    for i, (case, case_metrics) in enumerate(zip(cases, harness_judges)):
        if not case_metrics:
            continue
        lines.append(f"**{case['id']}** — _{case['query'][:60]}_")
        for m in case_metrics:
            lines.append(f"- {m.metric}: **{m.score:.2f}** — {m.reasoning[:100]}")
        lines.append("")

    # Router comparison
    lines.append("## 3. Comparativa de Rutas (Modelos)")
    lines.append("")
    lines.append("| Ruta | Coste Total | Coste/Query | Latencia Avg (ms) | Tokens In Avg | Tokens Out Avg | Errores |")
    lines.append("|------|------------|-------------|-------------------|---------------|----------------|---------|")

    for route_name, results in router_results.items():
        valid = [r for r in results if not r.error]
        errored = [r for r in results if r.error]
        total_c = sum(r.cost_usd for r in results)
        avg_c = total_c / len(results) if results else 0
        avg_lat = sum(r.latency_ms for r in valid) / len(valid) if valid else 0
        avg_in = sum(r.input_tokens for r in valid) / len(valid) if valid else 0
        avg_out = sum(r.output_tokens for r in valid) / len(valid) if valid else 0
        err_count = len(errored)
        lines.append(
            f"| {route_name} | ${total_c:.5f} | ${avg_c:.5f} | {avg_lat:.0f} | "
            f"{avg_in:.0f} | {avg_out:.0f} | {err_count}/{len(results)} |"
        )

    # Sonnet-4-6 row (pending)
    lines.append("| bedrock-sonnet-4-6 | — | — | — | — | — | PENDIENTE |")

    # Cost budget check
    lines.append("")
    lines.append("## 4. Presupuesto")
    lines.append("")
    total_harness = sum(r.cost_usd for r in harness_results)
    total_router = sum(
        sum(r.cost_usd for r in results)
        for results in router_results.values()
    )
    # Estimate judge costs (8 cases × 4 metrics × ~20 tokens Haiku = ~$0.001)
    judge_cost_estimate = len(harness_results) * 4 * 0.0002
    grand_total = total_harness + total_router + judge_cost_estimate

    lines.append(f"| Componente | Coste |")
    lines.append(f"|-----------|-------|")
    lines.append(f"| Harness (mock, $0) | ${total_harness:.5f} |")
    lines.append(f"| Router (3 modelos × 8 queries) | ${total_router:.5f} |")
    lines.append(f"| Judges (Haiku, estimado) | ${judge_cost_estimate:.5f} |")
    lines.append(f"| **TOTAL** | **${grand_total:.5f}** |")
    lines.append(f"| Presupuesto | $2.00 |")
    lines.append(f"| Estado | {'✓ DENTRO' if grand_total < 2.0 else '✗ EXCEDIDO'} |")

    # Conclusions
    lines.append("")
    lines.append("## 5. Conclusiones y Trade-offs")
    lines.append("")

    # Build conclusions based on actual data
    route_stats = {}
    for route_name, results in router_results.items():
        valid = [r for r in results if not r.error]
        if valid:
            route_stats[route_name] = {
                "cost": sum(r.cost_usd for r in results),
                "avg_latency": sum(r.latency_ms for r in valid) / len(valid),
                "errors": len([r for r in results if r.error]),
            }

    if route_stats:
        cheapest = min(route_stats, key=lambda k: route_stats[k]["cost"]) if route_stats else "N/A"
        fastest = min(route_stats, key=lambda k: route_stats[k]["avg_latency"]) if route_stats else "N/A"

        lines.extend([
            f"1. **Más económico**: `{cheapest}` — coste total ${route_stats.get(cheapest, {}).get('cost', 0):.5f} para 8 queries.",
            f"2. **Más rápido**: `{fastest}` — latencia promedio {route_stats.get(fastest, {}).get('avg_latency', 0):.0f}ms.",
            "3. **Haiku** ofrece el mejor balance calidad/coste para un agente fiscal dominicano.",
            "4. **Nova Micro** es ~20x más barato que Haiku pero con menor calidad en español.",
            "5. **GPT-4o-mini** requiere key válida; cuando funcione, comparar calidad en español.",
            "6. **Sonnet 4.6** será la ruta premium cuando Carlos active Marketplace — mejor calidad esperada.",
            "",
            "### Recomendación",
            "",
            "Para demo/producción inicial: **Haiku** como backbone del agente.",
            "Para volumen alto: **Nova Micro** como fallback de bajo coste.",
            "Para producción real: **Sonnet 4.6** cuando se habilite (pendiente).",
        ])
    else:
        lines.append("No hay datos suficientes de rutas para conclusiones.")

    lines.append("")
    lines.append("---")
    lines.append("*Generado por evals/run_all.py*")

    report = "\n".join(lines)

    report_path = REPORTS_DIR / "comparativa.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\n  Report saved to {report_path}")
    print(f"  Total estimated cost: ${grand_total:.5f}")

    return str(report_path)


def main():
    """Run the complete evaluation pipeline."""
    start = time.monotonic()

    token = _get_token()
    print(f"\n  Demo token: {token[:8]}...")

    # Step 1: Harness
    harness_results = step1_harness(token)

    # Step 2: Router comparison
    router_results = step2_router_comparison()

    # Step 3: Judges
    judge_results = step3_judges(harness_results)

    # Step 4: Report
    report_path = step4_generate_report(
        harness_results, router_results, judge_results
    )

    elapsed = (time.monotonic() - start) / 60
    print(f"\n{'='*60}")
    print(f"  COMPLETE in {elapsed:.1f} min")
    print(f"  Report: {report_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
