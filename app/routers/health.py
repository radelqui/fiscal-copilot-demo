import os

from fastapi import APIRouter

from app.db import get_conn
from app.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    db_connected = False
    db_tables = 0
    try:
        async with get_conn() as conn:
            row = await conn.execute(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
            result = await row.fetchone()
            db_tables = result[0] if result else 0
            db_connected = True
    except Exception:
        pass

    return HealthResponse(
        status="ok" if db_connected else "degraded",
        version="0.1.0",
        mock_mode=os.environ.get("USE_MOCK_AGENT", "0") == "1",
        db_connected=db_connected,
        db_tables=db_tables,
    )
