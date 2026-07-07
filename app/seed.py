"""Seed data for ¿Cómo Estoy Hecho? demo.

Run: python -m app.seed
Creates 3 tenants and 20 facturas with realistic Dominican tax data.
"""

import asyncio
import random

from app.db import init_db, close_db, get_conn

TENANTS = [
    ("tenant-acme", "ACME Distribuciones SRL"),
    ("tenant-global", "Global Trading Corp"),
    ("tenant-caribe", "Caribe Services SA"),
]

FACTURAS_SEED = [
    # tenant-acme (8 facturas)
    ("E010000000101", "101010101", "Suplidora Nacional SRL", 150000.00, 27000.00, "202606", "01", "activa", "tenant-acme"),
    ("E010000000102", "101010101", "Suplidora Nacional SRL", 85000.00, 15300.00, "202606", "01", "activa", "tenant-acme"),
    ("E020000000103", "000000000", "Consumidor Final", 12500.00, 2250.00, "202606", "02", "activa", "tenant-acme"),
    ("E010000000104", "202020202", "Tech Solutions EIRL", 340000.00, 61200.00, "202605", "01", "activa", "tenant-acme"),
    ("E010000000105", "303030303", "Farmacia Del Pueblo", 45000.00, 0.00, "202605", "01", "activa", "tenant-acme"),
    ("E040000000106", "101010101", "Suplidora Nacional SRL", 15000.00, 2700.00, "202606", "04", "activa", "tenant-acme"),
    ("E010000000107", "404040404", "Constructora Rivera SA", 890000.00, 160200.00, "202607", "01", "activa", "tenant-acme"),
    ("E150000000108", "000000001", "Ministerio de Hacienda", 250000.00, 45000.00, "202607", "15", "activa", "tenant-acme"),
    # tenant-global (7 facturas)
    ("E010000000201", "505050505", "Import Export Global", 1200000.00, 216000.00, "202606", "01", "activa", "tenant-global"),
    ("E010000000202", "606060606", "Logística Caribeña SA", 78000.00, 14040.00, "202606", "01", "activa", "tenant-global"),
    ("E140000000203", "707070707", "Zona Franca Industrial", 540000.00, 0.00, "202606", "14", "activa", "tenant-global"),
    ("E010000000204", "505050505", "Import Export Global", 320000.00, 57600.00, "202605", "01", "pagada", "tenant-global"),
    ("E030000000205", "606060606", "Logística Caribeña SA", 5000.00, 900.00, "202605", "03", "activa", "tenant-global"),
    ("E010000000206", "808080808", "Consultoría Fiscal RD", 95000.00, 17100.00, "202607", "01", "activa", "tenant-global"),
    ("E020000000207", "000000000", "Consumidor Final", 8500.00, 1530.00, "202607", "02", "activa", "tenant-global"),
    # tenant-caribe (5 facturas)
    ("E010000000301", "909090909", "Hotel Caribe Resort", 450000.00, 81000.00, "202606", "01", "activa", "tenant-caribe"),
    ("E010000000302", "111111111", "Alimentos del Cibao", 67000.00, 12060.00, "202606", "01", "activa", "tenant-caribe"),
    ("E110000000303", "000000002", "Juan Pérez (Informal)", 25000.00, 4500.00, "202605", "11", "activa", "tenant-caribe"),
    ("E010000000304", "909090909", "Hotel Caribe Resort", 180000.00, 32400.00, "202605", "01", "pagada", "tenant-caribe"),
    ("E020000000305", "000000000", "Consumidor Final", 3200.00, 576.00, "202607", "02", "activa", "tenant-caribe"),
]


async def seed():
    await init_db()
    try:
        async with get_conn() as conn:
            # Upsert tenants
            for tid, name in TENANTS:
                await conn.execute(
                    "INSERT INTO tenants (id, name) VALUES (%s, %s) "
                    "ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name",
                    [tid, name],
                )

            # Insert facturas (skip if NCF already exists)
            for f in FACTURAS_SEED:
                await conn.execute(
                    "INSERT INTO facturas (ncf, rnc, razon_social, monto, itbis, "
                    "periodo, tipo_ncf, estado, tenant_id) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
                    "ON CONFLICT DO NOTHING",
                    list(f),
                )

            await conn.commit()

            # Verify
            count = await conn.execute("SELECT COUNT(*) FROM facturas")
            n_facturas = (await count.fetchone())[0]
            count = await conn.execute("SELECT COUNT(*) FROM tenants")
            n_tenants = (await count.fetchone())[0]

            print(f"Seed complete: {n_tenants} tenants, {n_facturas} facturas")

            # Show summary by tenant
            summary = await conn.execute(
                "SELECT tenant_id, COUNT(*), SUM(monto), SUM(itbis) "
                "FROM facturas GROUP BY tenant_id ORDER BY tenant_id"
            )
            for row in await summary.fetchall():
                print(f"  {row[0]}: {row[1]} facturas, monto={row[2]:,.2f}, itbis={row[3]:,.2f}")
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(seed())
