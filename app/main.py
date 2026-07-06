import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db, close_db
from app.routers import ask, health, approvals, traces, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="Fiscal Copilot",
    description="AI agent for Dominican tax compliance",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(ask.router)
app.include_router(approvals.router)
app.include_router(traces.router)
app.include_router(dashboard.router)
