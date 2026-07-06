import os
from contextlib import asynccontextmanager

import psycopg
from psycopg_pool import AsyncConnectionPool

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://fiscal:fiscal_demo_2026@localhost:5544/fiscal_copilot",
)

_pool: AsyncConnectionPool | None = None


async def init_db():
    global _pool
    _pool = AsyncConnectionPool(DATABASE_URL, min_size=2, max_size=10, open=False)
    await _pool.open()
    async with _pool.connection() as conn:
        await _create_tables(conn)


async def close_db():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def get_pool() -> AsyncConnectionPool:
    if _pool is None:
        raise RuntimeError("Database pool not initialized")
    return _pool


@asynccontextmanager
async def get_conn():
    pool = await get_pool()
    async with pool.connection() as conn:
        yield conn


async def _create_tables(conn: psycopg.AsyncConnection):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS traces (
            trace_id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL REFERENCES tenants(id),
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            input_tokens INTEGER NOT NULL DEFAULT 0,
            output_tokens INTEGER NOT NULL DEFAULT 0,
            cost_usd NUMERIC(10, 6) NOT NULL DEFAULT 0,
            latency_ms NUMERIC(10, 2) NOT NULL DEFAULT 0,
            tools_used JSONB DEFAULT '[]',
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS approvals (
            id SERIAL PRIMARY KEY,
            trace_id TEXT REFERENCES traces(trace_id),
            tenant_id TEXT NOT NULL REFERENCES tenants(id),
            action TEXT NOT NULL,
            payload JSONB DEFAULT '{}',
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending', 'approved', 'rejected', 'executed')),
            decided_by TEXT,
            decided_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS facturas (
            id SERIAL PRIMARY KEY,
            ncf TEXT NOT NULL,
            rnc TEXT NOT NULL,
            razon_social TEXT NOT NULL,
            monto NUMERIC(12, 2) NOT NULL,
            itbis NUMERIC(12, 2) NOT NULL,
            periodo TEXT NOT NULL,
            tipo_ncf TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'activa'
                CHECK (estado IN ('activa', 'anulada', 'pagada')),
            tenant_id TEXT NOT NULL REFERENCES tenants(id),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS workflow_steps (
            id SERIAL PRIMARY KEY,
            workflow_id TEXT NOT NULL,
            step_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending', 'running', 'completed', 'failed', 'waiting_approval')),
            retries INTEGER NOT NULL DEFAULT 0,
            max_retries INTEGER NOT NULL DEFAULT 2,
            checkpoint JSONB DEFAULT '{}',
            error TEXT,
            tenant_id TEXT NOT NULL REFERENCES tenants(id),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_traces_tenant ON traces(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_traces_model ON traces(model);
        CREATE INDEX IF NOT EXISTS idx_traces_created ON traces(created_at);
        CREATE INDEX IF NOT EXISTS idx_facturas_tenant ON facturas(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_facturas_rnc ON facturas(rnc);
        CREATE INDEX IF NOT EXISTS idx_facturas_periodo ON facturas(periodo);
        CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status);
        CREATE INDEX IF NOT EXISTS idx_workflow_steps_workflow ON workflow_steps(workflow_id);
    """)
    await conn.commit()
