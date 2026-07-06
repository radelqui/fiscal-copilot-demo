import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import ask, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Fiscal Copilot",
    description="AI agent for Dominican tax compliance",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(ask.router)
