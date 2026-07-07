import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.auth import validate_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/demo", tags=["verificar-aws"])


@router.get("/{token}/verificar-aws")
async def verificar_aws(token: str):
    """Read AWS resource states in real-time via boto3."""
    if not await validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired demo token")

    results = {}
    timestamp = datetime.now(timezone.utc).isoformat()

    # Agent
    try:
        import boto3
        client = boto3.client("bedrock-agent", region_name="eu-central-1")
        agent = client.get_agent(agentId="2BOPZRAI7X")["agent"]
        results["agent"] = {
            "name": agent.get("agentName", "unknown"),
            "status": agent.get("agentStatus", "unknown"),
            "foundation_model": agent.get("foundationModel", "unknown"),
            "updated_at": str(agent.get("updatedAt", "")),
            "ok": agent.get("agentStatus") == "PREPARED",
        }
    except Exception as e:
        results["agent"] = {"status": f"error: {e}", "ok": False}

    # Knowledge Base
    try:
        import boto3
        client = boto3.client("bedrock-agent", region_name="eu-central-1")
        kb = client.get_knowledge_base(knowledgeBaseId="5I5RDNA2V1")["knowledgeBase"]
        results["knowledge_base"] = {
            "name": kb.get("name", "unknown"),
            "status": kb.get("status", "unknown"),
            "ok": kb.get("status") == "ACTIVE",
        }
    except Exception as e:
        results["knowledge_base"] = {"status": f"error: {e}", "ok": False}

    # Guardrail
    try:
        import boto3
        client = boto3.client("bedrock", region_name="eu-central-1")
        g = client.get_guardrail(guardrailIdentifier="xgn38kcg6hrq")
        results["guardrail"] = {
            "name": g.get("name", "unknown"),
            "status": g.get("status", "unknown"),
            "version": g.get("version", "unknown"),
            "ok": g.get("status") == "READY",
        }
    except Exception as e:
        results["guardrail"] = {"status": f"error: {e}", "ok": False}

    # Lambda
    try:
        import boto3
        client = boto3.client("lambda", region_name="eu-central-1")
        fn = client.get_function(FunctionName="fiscal-copilot-tools")
        config = fn.get("Configuration", {})
        results["lambda"] = {
            "function_name": config.get("FunctionName", "unknown"),
            "runtime": config.get("Runtime", "unknown"),
            "state": config.get("State", "unknown"),
            "last_modified": config.get("LastModified", "unknown"),
            "ok": config.get("State") == "Active",
        }
    except Exception as e:
        results["lambda"] = {"status": f"error: {e}", "ok": False}

    all_ok = all(r.get("ok", False) for r in results.values())

    return JSONResponse(content={
        "status": "all_ok" if all_ok else "partial_error",
        "timestamp": timestamp,
        "note": "Consultado en tiempo real desde la API de AWS Bedrock — NO hardcodeado",
        "resources": results,
    })
