import os
import pytest
from fastapi.testclient import TestClient

os.environ["USE_MOCK_AGENT"] = "1"

from app.main import app

client = TestClient(app)


class TestHealth:
    def test_health_ok(self):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["version"] == "0.1.0"
        assert data["mock_mode"] is True
        assert "db_connected" in data
        assert "status" in data

    def test_health_version(self):
        r = client.get("/health")
        assert r.json()["version"] == "0.1.0"


class TestAsk:
    def test_ask_explicar_componente(self):
        r = client.post("/ask", json={"query": "¿Cómo funciona el Bedrock Agent?"})
        assert r.status_code == 200
        data = r.json()
        assert data["provider"] == "mock"
        assert data["trace_id"]
        assert len(data["tools_used"]) == 1
        assert data["tools_used"][0]["tool_name"] == "explicar_componente"

    def test_ask_donde_verificar(self):
        r = client.post("/ask", json={"query": "¿Dónde puedo verificar el RAG?"})
        assert r.status_code == 200
        data = r.json()
        assert data["tools_used"][0]["tool_name"] == "donde_verificar"

    def test_ask_knowledge_base(self):
        r = client.post("/ask", json={"query": "¿Qué componentes tiene esta arquitectura?"})
        assert r.status_code == 200
        assert r.json()["response"]

    def test_ask_empty_query(self):
        r = client.post("/ask", json={"query": ""})
        assert r.status_code == 422

    def test_ask_cost_zero_in_mock(self):
        r = client.post("/ask", json={"query": "¿Cómo funciona el guardrail?"})
        assert r.json()["cost_usd"] == 0.0

    def test_response_has_trace_id(self):
        r = client.post("/ask", json={"query": "¿Qué es el RAG?"})
        data = r.json()
        assert len(data["trace_id"]) == 36  # UUID format

    def test_pydantic_strict_response(self):
        """Verify that the response matches the strict Pydantic model."""
        r = client.post("/ask", json={"query": "Explica el backend"})
        data = r.json()
        required_fields = {"trace_id", "response", "provider", "model", "tools_used",
                          "input_tokens", "output_tokens", "cost_usd", "latency_ms"}
        assert required_fields.issubset(set(data.keys()))
        assert isinstance(data["input_tokens"], int)
        assert isinstance(data["output_tokens"], int)
        assert isinstance(data["cost_usd"], float)
        assert isinstance(data["latency_ms"], float)
