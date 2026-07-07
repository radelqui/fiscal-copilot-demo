"""F7-UI tests — demo token auth, rate limiting, cost cap, UI endpoints.

Requires PostgreSQL on localhost:5544 with fiscal_copilot database.
Run with: USE_MOCK_AGENT=1 .venv/bin/python -m pytest tests/test_f7.py -v
"""

import pytest


def _get_valid_token(db_client) -> str:
    """Fetch a valid demo token from the DB via health-triggering lifespan."""
    from app.db import get_conn
    import asyncio

    async def _fetch():
        async with get_conn() as conn:
            row = await conn.execute(
                "SELECT token FROM demo_tokens WHERE expires_at > NOW() "
                "ORDER BY created_at DESC LIMIT 1"
            )
            result = await row.fetchone()
            return result[0] if result else None

    loop = asyncio.get_event_loop_policy().new_event_loop()
    try:
        return loop.run_until_complete(_fetch())
    finally:
        loop.close()


@pytest.fixture(scope="module")
def demo_token(db_client):
    """Get a valid demo token (created by lifespan)."""
    token = _get_valid_token(db_client)
    assert token is not None, "No demo token found — lifespan should create one"
    return token


class TestTokenValidation:
    def test_invalid_token_returns_401(self, db_client):
        r = db_client.get("/demo/not-a-real-token-at-all")
        assert r.status_code == 401

    def test_valid_token_returns_html(self, db_client, demo_token):
        r = db_client.get(f"/demo/{demo_token}")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]
        assert "Cómo Estoy Hecho" in r.text

    def test_html_has_injected_token(self, db_client, demo_token):
        r = db_client.get(f"/demo/{demo_token}")
        assert demo_token in r.text
        assert "DEMO_TOKEN" in r.text
        assert "API_BASE" in r.text

    def test_invalid_token_ask_returns_401(self, db_client):
        r = db_client.post(
            "/demo/fake-token-xyz/ask",
            json={"query": "test"},
        )
        assert r.status_code == 401

    def test_invalid_token_approvals_returns_401(self, db_client):
        r = db_client.get("/demo/fake-token-xyz/approvals")
        assert r.status_code == 401

    def test_invalid_token_decide_returns_401(self, db_client):
        r = db_client.post(
            "/demo/fake-token-xyz/approvals/1/decide",
            json={"decision": "approved"},
        )
        assert r.status_code == 401


class TestDemoAsk:
    def test_ask_returns_response_and_trace(self, db_client, demo_token):
        r = db_client.post(
            f"/demo/{demo_token}/ask",
            json={"query": "¿Cuánto ITBIS pago por 25000 pesos?"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "response" in data
        assert "trace" in data
        trace = data["trace"]
        assert "provider" in trace
        assert "model" in trace
        assert "tokens_in" in trace
        assert "tokens_out" in trace
        assert "cost_usd" in trace
        assert "latency_ms" in trace

    def test_ask_empty_query_returns_422(self, db_client, demo_token):
        r = db_client.post(
            f"/demo/{demo_token}/ask",
            json={"query": ""},
        )
        assert r.status_code == 422

    def test_ask_oversized_query_returns_422(self, db_client, demo_token):
        r = db_client.post(
            f"/demo/{demo_token}/ask",
            json={"query": "x" * 2001},
        )
        assert r.status_code == 422

    def test_ask_persists_trace_to_db(self, db_client, demo_token):
        r = db_client.post(
            f"/demo/{demo_token}/ask",
            json={"query": "Valida NCF E010000000042", "tenant_id": "demo-visitor"},
        )
        assert r.status_code == 200

        traces = db_client.get("/traces?tenant_id=demo-visitor&limit=5")
        assert traces.status_code == 200
        queries = [t["query"] for t in traces.json()["traces"]]
        assert any("E010000000042" in q for q in queries)


class TestDemoApprovals:
    def test_list_approvals_via_demo(self, db_client, demo_token):
        r = db_client.get(f"/demo/{demo_token}/approvals")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_create_and_decide_approval(self, db_client, demo_token):
        r = db_client.post(
            f"/demo/{demo_token}/ask",
            json={
                "query": "Presenta el formato 606 del periodo 202607 con 8 registros",
                "tenant_id": "demo-visitor",
            },
        )
        assert r.status_code == 200

        approvals = db_client.get(f"/demo/{demo_token}/approvals?status=pending")
        data = approvals.json()
        pending = [a for a in data if a["status"] == "pending"]
        assert len(pending) >= 1

        aid = pending[0]["id"]
        decide = db_client.post(
            f"/demo/{demo_token}/approvals/{aid}/decide",
            json={"decision": "approved"},
        )
        assert decide.status_code == 200
        assert decide.json()["ok"] is True

    def test_decide_nonexistent_returns_404(self, db_client, demo_token):
        r = db_client.post(
            f"/demo/{demo_token}/approvals/99999/decide",
            json={"decision": "approved"},
        )
        assert r.status_code == 404

    def test_double_decide_returns_409(self, db_client, demo_token):
        r = db_client.post(
            f"/demo/{demo_token}/ask",
            json={
                "query": "Presenta el 606 del periodo 202608 con 3 registros",
                "tenant_id": "demo-visitor",
            },
        )
        assert r.status_code == 200

        approvals = db_client.get(f"/demo/{demo_token}/approvals?status=pending")
        pending = [a for a in approvals.json() if a["status"] == "pending"]
        assert len(pending) >= 1
        aid = pending[0]["id"]

        first = db_client.post(
            f"/demo/{demo_token}/approvals/{aid}/decide",
            json={"decision": "rejected"},
        )
        assert first.status_code == 200

        second = db_client.post(
            f"/demo/{demo_token}/approvals/{aid}/decide",
            json={"decision": "approved"},
        )
        assert second.status_code == 409

    def test_invalid_decision_returns_422(self, db_client, demo_token):
        r = db_client.post(
            f"/demo/{demo_token}/ask",
            json={
                "query": "Presenta el 606 del periodo 202609 con 2 registros",
                "tenant_id": "demo-visitor",
            },
        )
        approvals = db_client.get(f"/demo/{demo_token}/approvals?status=pending")
        pending = [a for a in approvals.json() if a["status"] == "pending"]
        assert len(pending) >= 1
        aid = pending[0]["id"]

        r = db_client.post(
            f"/demo/{demo_token}/approvals/{aid}/decide",
            json={"decision": "maybe"},
        )
        assert r.status_code == 422


class TestRateLimit:
    def test_rate_limit_blocks_after_threshold(self, db_client, demo_token):
        from app.auth import reset_rate_limits, RATE_LIMIT_PER_HOUR
        reset_rate_limits()

        for i in range(RATE_LIMIT_PER_HOUR):
            r = db_client.post(
                f"/demo/{demo_token}/ask",
                json={"query": f"ITBIS de {1000 + i}"},
            )
            assert r.status_code == 200, f"Request {i+1} failed unexpectedly"

        r = db_client.post(
            f"/demo/{demo_token}/ask",
            json={"query": "ITBIS de 999999"},
        )
        assert r.status_code == 429
        assert "rate" in r.json()["detail"].lower() or "limit" in r.json()["detail"].lower()

        reset_rate_limits()


class TestCostCap:
    def test_cost_cap_blocks_when_exceeded(self, db_client, demo_token):
        from app.auth import reset_rate_limits
        import asyncio

        reset_rate_limits()

        async def _insert_expensive_trace():
            from app.db import get_conn
            import uuid
            async with get_conn() as conn:
                await conn.execute(
                    "INSERT INTO tenants (id, name) VALUES (%s, %s) "
                    "ON CONFLICT (id) DO NOTHING",
                    ["cost-cap-test", "cost-cap-test"],
                )
                await conn.execute(
                    "INSERT INTO traces (trace_id, tenant_id, query, response, provider, "
                    "model, input_tokens, output_tokens, cost_usd, latency_ms, tools_used) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    [
                        str(uuid.uuid4()), "cost-cap-test", "test", "test",
                        "mock", "local-tools", 0, 0, 2.50, 0.0, "[]",
                    ],
                )
                await conn.commit()

        loop = asyncio.get_event_loop_policy().new_event_loop()
        try:
            loop.run_until_complete(_insert_expensive_trace())
        finally:
            loop.close()

        r = db_client.post(
            f"/demo/{demo_token}/ask",
            json={"query": "test cost cap"},
        )
        assert r.status_code == 429
        assert "cost" in r.json()["detail"].lower() or "limit" in r.json()["detail"].lower()

        async def _cleanup():
            from app.db import get_conn
            async with get_conn() as conn:
                await conn.execute(
                    "DELETE FROM traces WHERE tenant_id = %s", ["cost-cap-test"]
                )
                await conn.commit()

        loop2 = asyncio.get_event_loop_policy().new_event_loop()
        try:
            loop2.run_until_complete(_cleanup())
        finally:
            loop2.close()

        reset_rate_limits()


class TestArchitecture:
    def test_architecture_valid_token(self, db_client, demo_token):
        r = db_client.get(f"/demo/{demo_token}/architecture")
        assert r.status_code == 200
        assert "Cómo Estoy Hecho" in r.text
        assert "mermaid" in r.text.lower() or "Arquitectura" in r.text

    def test_architecture_invalid_token(self, db_client):
        r = db_client.get("/demo/invalid-token-xyz/architecture")
        assert r.status_code == 401
