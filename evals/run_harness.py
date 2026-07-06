"""Eval Harness — runs golden_set.jsonl against live backend.

Usage:
    python -m evals.run_harness [--base-url URL] [--token TOKEN]
"""

import json
import sys
import time
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.jsonl"


@dataclass
class CaseResult:
    id: str
    query: str
    category: str
    response: str
    expected_contains_pass: bool
    expected_not_contains_pass: bool
    expected_tool_pass: bool
    tools_used: list[str]
    cost_usd: float
    latency_ms: float
    provider: str
    model: str
    pass_overall: bool
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _get_demo_token(base_url: str) -> str | None:
    """Try to get a valid demo token from the DB."""
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
        return row[0] if row else None
    except Exception as e:
        logger.warning("Could not fetch token from DB: %s", e)
        return None


def load_golden_set() -> list[dict]:
    """Load golden set from JSONL file."""
    cases = []
    with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


def evaluate_case(
    case: dict, base_url: str, token: str, client: httpx.Client
) -> CaseResult:
    """Run a single golden set case against the live API."""
    url = f"{base_url}/demo/{token}/ask"
    errors: list[str] = []

    try:
        start = time.monotonic()
        r = client.post(
            url,
            json={"query": case["query"], "tenant_id": "eval-harness"},
            timeout=30.0,
        )
        wall_latency = (time.monotonic() - start) * 1000

        if r.status_code != 200:
            return CaseResult(
                id=case["id"], query=case["query"],
                category=case.get("category", "unknown"),
                response=f"HTTP {r.status_code}: {r.text[:200]}",
                expected_contains_pass=False, expected_not_contains_pass=False,
                expected_tool_pass=False, tools_used=[], cost_usd=0.0,
                latency_ms=round(wall_latency, 2), provider="error",
                model="error", pass_overall=False,
                errors=[f"HTTP {r.status_code}"],
            )

        data = r.json()
        response_text = data.get("response", "")
        trace = data.get("trace", {})
        tools = trace.get("tools", [])
        tool_names = [t.get("tool_name", "") for t in tools]

        # Check expected_contains (ANY match = pass)
        expected_contains = case.get("expected_response_contains", [])
        contains_pass = True
        if expected_contains:
            response_lower = response_text.lower()
            if not any(exp.lower() in response_lower for exp in expected_contains):
                contains_pass = False
                errors.append(f"Missing all expected: {expected_contains}")

        # Check expected_not_contains
        expected_not = case.get("expected_response_not_contains", [])
        not_contains_pass = True
        if expected_not:
            response_lower = response_text.lower()
            for forbidden in expected_not:
                if forbidden.lower() in response_lower:
                    not_contains_pass = False
                    errors.append(f"Found forbidden: '{forbidden}'")

        # Check expected tools
        expected_tools = case.get("expected_tools", [])
        tool_pass = True
        if expected_tools:
            for et in expected_tools:
                if et not in tool_names:
                    tool_pass = False
                    errors.append(f"Missing tool: '{et}'")
        elif tool_names:
            pass

        overall = contains_pass and not_contains_pass and tool_pass

        return CaseResult(
            id=case["id"], query=case["query"],
            category=case.get("category", "unknown"),
            response=response_text,
            expected_contains_pass=contains_pass,
            expected_not_contains_pass=not_contains_pass,
            expected_tool_pass=tool_pass,
            tools_used=tool_names,
            cost_usd=trace.get("cost_usd", 0.0),
            latency_ms=trace.get("latency_ms", 0.0),
            provider=trace.get("provider", "unknown"),
            model=trace.get("model", "unknown"),
            pass_overall=overall,
            errors=errors,
        )

    except Exception as e:
        return CaseResult(
            id=case["id"], query=case["query"],
            category=case.get("category", "unknown"),
            response="", expected_contains_pass=False,
            expected_not_contains_pass=False, expected_tool_pass=False,
            tools_used=[], cost_usd=0.0, latency_ms=0.0,
            provider="error", model="error", pass_overall=False,
            errors=[str(e)],
        )


def run_harness(
    base_url: str = "http://localhost:7020",
    token: str | None = None,
) -> list[CaseResult]:
    """Run the full golden set harness."""
    if token is None:
        token = _get_demo_token(base_url)
        if token is None:
            raise RuntimeError("No valid demo token found")

    cases = load_golden_set()
    results: list[CaseResult] = []

    print(f"\n{'='*60}")
    print(f"  FISCAL COPILOT — Eval Harness")
    print(f"  Backend: {base_url}")
    print(f"  Token: {token[:8]}...")
    print(f"  Cases: {len(cases)}")
    print(f"{'='*60}\n")

    with httpx.Client() as client:
        for i, case in enumerate(cases, 1):
            result = evaluate_case(case, base_url, token, client)
            results.append(result)
            status = "PASS" if result.pass_overall else "FAIL"
            symbol = "✓" if result.pass_overall else "✗"
            print(
                f"  [{i}/{len(cases)}] {symbol} {case['id']:20s} "
                f"{status:4s}  {result.latency_ms:7.1f}ms  "
                f"${result.cost_usd:.5f}  "
                f"{'  '.join(result.errors) if result.errors else ''}"
            )

    passed = sum(1 for r in results if r.pass_overall)
    total_cost = sum(r.cost_usd for r in results)
    avg_latency = sum(r.latency_ms for r in results) / len(results) if results else 0

    print(f"\n{'─'*60}")
    print(f"  Results: {passed}/{len(results)} passed")
    print(f"  Total cost: ${total_cost:.5f}")
    print(f"  Avg latency: {avg_latency:.1f}ms")
    print(f"{'─'*60}\n")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:7020")
    parser.add_argument("--token", default=None)
    args = parser.parse_args()

    from app.auth import reset_rate_limits
    reset_rate_limits()

    results = run_harness(base_url=args.base_url, token=args.token)

    output_path = Path(__file__).parent / "harness_results.json"
    with open(output_path, "w") as f:
        json.dump([r.to_dict() for r in results], f, indent=2, ensure_ascii=False)
    print(f"  Results saved to {output_path}")
