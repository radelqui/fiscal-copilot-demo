from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    mock_mode: bool


@router.get("/health", response_model=HealthResponse)
async def health():
    import os
    return HealthResponse(
        status="ok",
        version="0.1.0",
        mock_mode=os.environ.get("USE_MOCK_AGENT", "0") == "1",
    )
