"""F3 integration tests — backend + PostgreSQL + observability.

Requires PostgreSQL on localhost:5544 with fiscal_copilot database.
Run with: USE_MOCK_AGENT=1 .venv/bin/python -m pytest tests/test_f3.py -v
"""

import pytest
from pydantic import ValidationError


class TestHealthWithDB:
    def test_health_shows_db_connected(self, db_client):
        r = db_client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["db_connected"] is True
        assert data["db_tables"] >= 5
        assert data["status"] == "ok"

    def test_health_shows_mock_mode(self, db_client):
        r = db_client.get("/health")
        assert r.json()["mock_mode"] is True


class TestAskWithPersistence:
    def test_ask_persists_trace(self, db_client):
        r = db_client.post("/ask", json={
            "query": "¿Cuánto ITBIS pago por 50000?",
            "tenant_id": "tenant-acme",
        })
        assert r.status_code == 200
        trace_id = r.json()["trace_id"]

        traces = db_client.get("/traces?tenant_id=tenant-acme")
        assert traces.status_code == 200
        trace_ids = [t["trace_id"] for t in traces.json()["traces"]]
        assert trace_id in trace_ids

    def test_ask_creates_approval_for_606(self, db_client):
        r = db_client.post("/ask", json={
            "query": "Presenta el formato 606 del periodo 202606 con 10 registros",
            "tenant_id": "tenant-acme",
        })
        assert r.status_code == 200
        trace_id = r.json()["trace_id"]

        approvals = db_client.get("/approvals?tenant_id=tenant-acme&status=pending")
        assert approvals.status_code == 200
        approval_trace_ids = [a["trace_id"] for a in approvals.json()["approvals"]]
        assert trace_id in approval_trace_ids


class TestApprovals:
    def _create_pending_approval(self, db_client) -> int:
        r = db_client.post("/ask", json={
            "query": "Presenta el 606 del periodo 202601 con 5 registros",
            "tenant_id": "tenant-caribe",
        })
        trace_id = r.json()["trace_id"]
        approvals = db_client.get("/approvals?status=pending&tenant_id=tenant-caribe")
        for a in approvals.json()["approvals"]:
            if a["trace_id"] == trace_id:
                return a["id"]
        raise AssertionError("No pending approval found for trace")

    def test_list_approvals(self, db_client):
        r = db_client.get("/approvals")
        assert r.status_code == 200
        data = r.json()
        assert "approvals" in data
        assert "total" in data

    def test_approve_approval(self, db_client):
        aid = self._create_pending_approval(db_client)
        r = db_client.post(f"/approvals/{aid}/decide", json={
            "decision": "approved",
            "decided_by": "test-user",
        })
        assert r.status_code == 200
        assert r.json()["status"] == "approved"
        assert r.json()["decided_by"] == "test-user"

    def test_reject_approval(self, db_client):
        aid = self._create_pending_approval(db_client)
        r = db_client.post(f"/approvals/{aid}/decide", json={
            "decision": "rejected",
            "decided_by": "test-user",
        })
        assert r.status_code == 200
        assert r.json()["status"] == "rejected"

    def test_double_decide_returns_409(self, db_client):
        aid = self._create_pending_approval(db_client)
        db_client.post(f"/approvals/{aid}/decide", json={"decision": "approved"})
        r = db_client.post(f"/approvals/{aid}/decide", json={"decision": "rejected"})
        assert r.status_code == 409

    def test_decide_nonexistent_returns_404(self, db_client):
        r = db_client.post("/approvals/99999/decide", json={"decision": "approved"})
        assert r.status_code == 404

    def test_invalid_decision_returns_422(self, db_client):
        aid = self._create_pending_approval(db_client)
        r = db_client.post(f"/approvals/{aid}/decide", json={"decision": "maybe"})
        assert r.status_code == 422


class TestTraces:
    def test_list_traces_with_filter(self, db_client):
        db_client.post("/ask", json={
            "query": "¿Qué es el ITBIS?",
            "tenant_id": "tenant-global",
        })
        r = db_client.get("/traces?tenant_id=tenant-global")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1
        assert data["filters"]["tenant_id"] == "tenant-global"
        for t in data["traces"]:
            assert t["tenant_id"] == "tenant-global"

    def test_list_traces_with_limit(self, db_client):
        r = db_client.get("/traces?limit=2")
        assert r.status_code == 200
        assert len(r.json()["traces"]) <= 2

    def test_trace_has_all_fields(self, db_client):
        db_client.post("/ask", json={"query": "Calcula ITBIS de 100000"})
        r = db_client.get("/traces?limit=1")
        trace = r.json()["traces"][0]
        required = {"trace_id", "tenant_id", "query", "response", "provider",
                    "model", "input_tokens", "output_tokens", "cost_usd",
                    "latency_ms", "tools_used", "created_at"}
        assert required.issubset(set(trace.keys()))


class TestDashboard:
    def test_dashboard_returns_html(self, db_client):
        r = db_client.get("/dashboard")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]
        assert "Fiscal Copilot" in r.text
        assert "Dashboard" in r.text

    def test_dashboard_shows_tables(self, db_client):
        db_client.post("/ask", json={"query": "ITBIS de 1000", "tenant_id": "tenant-acme"})
        r = db_client.get("/dashboard")
        assert r.status_code == 200
        assert "tenant-acme" in r.text or "Tenant" in r.text


class TestMalformedOutputRejection:
    """Demonstrates that Pydantic REJECTS malformed structured outputs."""

    def test_pydantic_rejects_missing_required_field(self):
        from app.routers.ask import AskResponse
        with pytest.raises(ValidationError) as exc_info:
            AskResponse(
                trace_id="abc",
                response="hello",
            )
        errors = exc_info.value.errors()
        missing_fields = {e["loc"][0] for e in errors}
        assert "provider" in missing_fields
        assert "model" in missing_fields

    def test_pydantic_rejects_wrong_types(self):
        from app.routers.ask import AskResponse
        with pytest.raises(ValidationError):
            AskResponse(
                trace_id="abc",
                response="hello",
                provider="bedrock",
                model="sonnet",
                tools_used=[],
                input_tokens="not_a_number",
                output_tokens=10,
                cost_usd="free",
                latency_ms=1.0,
            )

    def test_pydantic_rejects_invalid_approval_decision(self):
        from app.schemas import ApprovalDecision
        with pytest.raises(ValidationError):
            ApprovalDecision(decision="maybe")
        with pytest.raises(ValidationError):
            ApprovalDecision(decision="")
        ApprovalDecision(decision="approved")
        ApprovalDecision(decision="rejected")

    def test_pydantic_rejects_empty_query(self, db_client):
        r = db_client.post("/ask", json={"query": ""})
        assert r.status_code == 422

    def test_pydantic_rejects_oversized_query(self, db_client):
        r = db_client.post("/ask", json={"query": "x" * 2001})
        assert r.status_code == 422
