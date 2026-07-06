"""Tests for GET /metrics endpoint."""
import json

import pytest
from fastapi.testclient import TestClient


def test_metrics_empty_db(db_client):
    """Verify that /metrics returns valid schema and zero values when traces table is empty."""
    import psycopg

    conn = psycopg.connect(
        "postgresql://fiscal:fiscal_demo_2026@localhost:5544/fiscal_copilot"
    )
    # Snapshot current count so we can restore after
    original_count = conn.execute("SELECT COUNT(*) FROM traces").fetchone()[0]

    try:
        # Clear all traces to simulate empty DB
        conn.execute("DELETE FROM approvals")
        conn.execute("DELETE FROM traces")
        conn.commit()

        r = db_client.get("/metrics")
        assert r.status_code == 200
        data = r.json()
        assert data["total_requests"] == 0
        assert data["total_cost_usd"] == 0.0
        assert data["avg_latency_ms"] == 0.0
        assert data["latency_p50_ms"] == 0.0
        assert data["latency_p95_ms"] == 0.0
        assert data["by_model"] == []
        assert data["by_tenant"] == []
        assert "generated_at" in data
    finally:
        conn.close()


def _insert_trace(client, tenant_id, model, cost, latency):
    """Helper to insert a trace directly via the ask endpoint won't work for controlled data,
    so we insert directly."""
    import psycopg
    conn = psycopg.connect(
        "postgresql://fiscal:fiscal_demo_2026@localhost:5544/fiscal_copilot"
    )
    conn.execute(
        "INSERT INTO tenants (id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        [tenant_id, tenant_id],
    )
    import uuid
    tid = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO traces (trace_id, tenant_id, query, response, provider, model, "
        "input_tokens, output_tokens, cost_usd, latency_ms, tools_used) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        [tid, tenant_id, "test", "test", "bedrock", model, 100, 50, cost, latency, "[]"],
    )
    conn.commit()
    conn.close()
    return tid


def test_metrics_with_data(db_client):
    _insert_trace(db_client, "metrics-test-1", "sonnet", 0.01, 1000.0)
    _insert_trace(db_client, "metrics-test-1", "sonnet", 0.02, 2000.0)
    _insert_trace(db_client, "metrics-test-2", "haiku", 0.005, 500.0)

    r = db_client.get("/metrics")
    assert r.status_code == 200
    data = r.json()
    assert data["total_requests"] >= 3
    assert data["total_cost_usd"] > 0
    assert len(data["by_model"]) >= 2
    assert len(data["by_tenant"]) >= 2


def test_metrics_percentiles(db_client):
    for lat in [100, 200, 300, 400, 500, 600, 700, 800, 900, 10000]:
        _insert_trace(db_client, "pct-test", "pct-model", 0.001, float(lat))

    r = db_client.get("/metrics")
    assert r.status_code == 200
    data = r.json()
    assert data["latency_p50_ms"] > 0
    assert data["latency_p95_ms"] > data["latency_p50_ms"]


def test_metrics_response_schema(db_client):
    r = db_client.get("/metrics")
    assert r.status_code == 200
    data = r.json()
    required_keys = [
        "total_requests", "total_cost_usd", "avg_latency_ms",
        "latency_p50_ms", "latency_p95_ms", "by_model", "by_tenant", "generated_at",
    ]
    for key in required_keys:
        assert key in data, f"Missing key: {key}"
