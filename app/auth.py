"""Demo token authentication, rate limiting, and cost cap.

Tokens are path-based: /demo/{token}/...
Rate limit: 60 req/hour per token (in-memory).
Cost cap: $2.00/day across all tokens.
"""

import os
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException

from app.db import get_conn

RATE_LIMIT_PER_HOUR = 60
DAILY_COST_CAP_USD = 2.0

_request_log: dict[str, list[float]] = defaultdict(list)


async def create_demo_tokens_table():
    """Create demo_tokens table if it doesn't exist."""
    async with get_conn() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS demo_tokens (
                token TEXT PRIMARY KEY,
                expires_at TIMESTAMPTZ NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        await conn.commit()


async def generate_token(days: int = 14) -> str:
    """Generate a new demo token with expiration."""
    token = uuid.uuid4().hex[:24]
    expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    async with get_conn() as conn:
        await conn.execute(
            "INSERT INTO demo_tokens (token, expires_at) VALUES (%s, %s) "
            "ON CONFLICT (token) DO UPDATE SET expires_at = EXCLUDED.expires_at",
            [token, expires_at],
        )
        await conn.commit()
    return token


async def validate_token(token: str) -> bool:
    """Check if token exists and is not expired."""
    async with get_conn() as conn:
        row = await conn.execute(
            "SELECT expires_at FROM demo_tokens WHERE token = %s",
            [token],
        )
        result = await row.fetchone()
        if not result:
            return False
        return result[0] > datetime.now(timezone.utc)


def check_rate_limit(token: str):
    """Check in-memory rate limit. Raises HTTPException if exceeded."""
    now = time.monotonic()
    hour_ago = now - 3600

    # Clean old entries
    _request_log[token] = [t for t in _request_log[token] if t > hour_ago]

    if len(_request_log[token]) >= RATE_LIMIT_PER_HOUR:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {RATE_LIMIT_PER_HOUR} requests per hour",
        )

    _request_log[token].append(now)


async def check_daily_cost_cap():
    """Check if daily cost cap is exceeded. Raises HTTPException if so."""
    async with get_conn() as conn:
        row = await conn.execute(
            "SELECT COALESCE(SUM(cost_usd), 0) FROM traces "
            "WHERE created_at >= CURRENT_DATE"
        )
        result = await row.fetchone()
        daily_cost = float(result[0]) if result else 0.0

        if daily_cost >= DAILY_COST_CAP_USD:
            raise HTTPException(
                status_code=429,
                detail="Daily demo cost limit reached. Try again tomorrow.",
            )

    return daily_cost


async def ensure_demo_token() -> str:
    """Ensure at least one demo token exists. Returns the token."""
    await create_demo_tokens_table()
    async with get_conn() as conn:
        row = await conn.execute(
            "SELECT token FROM demo_tokens WHERE expires_at > NOW() "
            "ORDER BY created_at DESC LIMIT 1"
        )
        result = await row.fetchone()
        if result:
            return result[0]

    return await generate_token()


def reset_rate_limits():
    """Reset all rate limit counters (for testing)."""
    _request_log.clear()


if __name__ == "__main__":
    import asyncio
    from app.db import init_db, close_db

    async def main():
        await init_db()
        token = await generate_token()
        print(f"Generated token: {token}")
        print(f"Demo URL: /demo/{token}")
        await close_db()

    asyncio.run(main())
