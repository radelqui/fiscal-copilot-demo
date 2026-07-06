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
        assert data["status"] == "ok"
        assert data["mock_mode"] is True

    def test_health_version(self):
        r = client.get("/health")
        assert r.json()["version"] == "0.1.0"


class TestAsk:
    def test_ask_itbis_calculation(self):
        r = client.post("/ask", json={"query": "¿Cuánto ITBIS pago por 100000 pesos?"})
        assert r.status_code == 200
        data = r.json()
        assert data["provider"] == "mock"
        assert data["trace_id"]
        assert "18,000" in data["response"] or "18000" in data["response"]
        assert len(data["tools_used"]) == 1
        assert data["tools_used"][0]["tool_name"] == "calcular_itbis"

    def test_ask_itbis_included(self):
        r = client.post("/ask", json={"query": "Tengo 118000 con ITBIS incluido, cuánto es el ITBIS?"})
        assert r.status_code == 200
        data = r.json()
        assert "18,000" in data["response"] or "18000" in data["response"]

    def test_ask_validar_ncf(self):
        r = client.post("/ask", json={"query": "¿Es válido el NCF E010000000001?"})
        assert r.status_code == 200
        data = r.json()
        assert "válido" in data["response"]
        assert len(data["tools_used"]) == 1
        assert data["tools_used"][0]["tool_name"] == "validar_ncf"

    def test_ask_ncf_invalido(self):
        r = client.post("/ask", json={"query": "Valida el NCF E990000000001"})
        assert r.status_code == 200
        assert "inválido" in r.json()["response"]

    def test_ask_knowledge_base(self):
        r = client.post("/ask", json={"query": "¿Cuál es la fecha límite del 606?"})
        assert r.status_code == 200
        assert "15" in r.json()["response"]

    def test_ask_empty_query(self):
        r = client.post("/ask", json={"query": ""})
        assert r.status_code == 422

    def test_ask_cost_zero_in_mock(self):
        r = client.post("/ask", json={"query": "Calcula ITBIS de 50000"})
        assert r.json()["cost_usd"] == 0.0

    def test_response_has_trace_id(self):
        r = client.post("/ask", json={"query": "¿Qué es el ITBIS?"})
        data = r.json()
        assert len(data["trace_id"]) == 36  # UUID format

    def test_pydantic_strict_response(self):
        """Verify that the response matches the strict Pydantic model."""
        r = client.post("/ask", json={"query": "Calcula ITBIS de 200000"})
        data = r.json()
        required_fields = {"trace_id", "response", "provider", "model", "tools_used",
                          "input_tokens", "output_tokens", "cost_usd", "latency_ms"}
        assert required_fields.issubset(set(data.keys()))
        assert isinstance(data["input_tokens"], int)
        assert isinstance(data["output_tokens"], int)
        assert isinstance(data["cost_usd"], float)
        assert isinstance(data["latency_ms"], float)
