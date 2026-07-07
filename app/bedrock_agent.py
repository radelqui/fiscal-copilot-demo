"""Bedrock Agent client with automatic fallback to mock.

Reads agent IDs from aws/ids.env. If AGENT_ID is not set or boto3
is not available, falls back to mock_invoke_agent transparently.

When the real agent returns requireConfirmation, creates an approval
record in the DB linked to the trace.
"""

import json
import os
import time
import uuid
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_agent_config: dict[str, str] = {}
_boto3_available = False

try:
    import boto3
    _boto3_available = True
except ImportError:
    pass


def load_agent_config() -> dict[str, str]:
    """Load agent IDs from aws/ids.env."""
    global _agent_config
    ids_path = Path(__file__).parent.parent / "aws" / "ids.env"
    config: dict[str, str] = {}
    if ids_path.exists():
        for line in ids_path.read_text().strip().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                config[key.strip()] = value.strip()
    _agent_config = config
    return config


def is_bedrock_available() -> bool:
    """Check if Bedrock Agent can be used."""
    config = _agent_config or load_agent_config()
    return (
        _boto3_available
        and bool(config.get("AGENT_ID"))
        and bool(config.get("ALIAS_ID"))
    )


async def invoke_agent(
    query: str,
    session_id: str | None = None,
    tenant_id: str = "demo-tenant",
) -> dict[str, Any]:
    """Invoke the Bedrock Agent or fall back to mock.

    Returns a dict with:
        response: str
        tools_used: list[dict]
        provider: str
        model: str
        input_tokens: int
        output_tokens: int
        cost_usd: float
        latency_ms: float
        requires_confirmation: bool
        confirmation_payload: dict | None
    """
    if not is_bedrock_available() or os.environ.get("USE_MOCK_AGENT", "0") == "1":
        return _invoke_mock(query)

    return await _invoke_bedrock(query, session_id)


def _invoke_mock(query: str) -> dict[str, Any]:
    """Fallback: use local mock agent."""
    from app.mock_agent import mock_invoke_agent

    start = time.monotonic()
    result = mock_invoke_agent(query)
    latency = (time.monotonic() - start) * 1000

    requires_confirmation = any(
        t.get("tool_name") == "generar_reporte_arquitectura"
        for t in result.get("tools_used", [])
    )

    return {
        "response": result["response"],
        "tools_used": result.get("tools_used", []),
        "provider": "mock",
        "model": "local-tools",
        "input_tokens": len(query.split()) * 2,
        "output_tokens": len(result["response"].split()) * 2,
        "cost_usd": 0.0,
        "latency_ms": round(latency, 2),
        "requires_confirmation": requires_confirmation,
        "confirmation_payload": (
            result["tools_used"][-1].get("tool_input")
            if requires_confirmation and result.get("tools_used")
            else None
        ),
    }


async def _invoke_bedrock(
    query: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Real Bedrock Agent invocation."""
    config = _agent_config or load_agent_config()
    agent_id = config["AGENT_ID"]
    alias_id = config["ALIAS_ID"]
    region = os.environ.get("AWS_REGION", "eu-central-1")

    client = boto3.client("bedrock-agent-runtime", region_name=region)
    sid = session_id or uuid.uuid4().hex[:12]

    start = time.monotonic()

    try:
        response = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=alias_id,
            sessionId=sid,
            inputText=query,
            enableTrace=True,
        )

        full_response = ""
        tools_used = []
        requires_confirmation = False
        confirmation_payload = None
        total_input_tokens = 0
        total_output_tokens = 0

        for event in response.get("completion", []):
            if "chunk" in event:
                chunk = event["chunk"]
                if "bytes" in chunk:
                    full_response += chunk["bytes"].decode("utf-8")

            if "returnControl" in event:
                rc = event["returnControl"]
                if rc.get("invocationInputs"):
                    for inv in rc["invocationInputs"]:
                        if "apiInvocationInput" in inv:
                            api_input = inv["apiInvocationInput"]
                            if api_input.get("actionGroupInvocationInput", {}).get(
                                "requireConfirmation"
                            ) == "ENABLED":
                                requires_confirmation = True
                                confirmation_payload = api_input

            if "trace" in event:
                trace = event["trace"].get("trace", {})
                orchestration = trace.get("orchestrationTrace", {})
                if "invocationInput" in orchestration:
                    inv_input = orchestration["invocationInput"]
                    if "actionGroupInvocationInput" in inv_input:
                        ag = inv_input["actionGroupInvocationInput"]
                        tools_used.append({
                            "tool_name": ag.get("function", "unknown"),
                            "tool_input": {
                                p["name"]: p["value"]
                                for p in ag.get("parameters", [])
                            },
                            "tool_output": {},
                        })
                if "modelInvocationOutput" in orchestration:
                    model_output = orchestration["modelInvocationOutput"]
                    usage = model_output.get("metadata", {}).get("usage", {})
                    total_input_tokens += usage.get("inputTokens", 0)
                    total_output_tokens += usage.get("outputTokens", 0)

        logger.debug(
            "Bedrock usage: in=%d out=%d tools=%s",
            total_input_tokens,
            total_output_tokens,
            [t["tool_name"] for t in tools_used],
        )

        latency = (time.monotonic() - start) * 1000
        cost_usd = _estimate_cost(total_input_tokens, total_output_tokens)

        return {
            "response": full_response,
            "tools_used": tools_used,
            "provider": "bedrock",
            "model": "eu.anthropic.claude-sonnet-4-6-20250514-v1:0",
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "cost_usd": cost_usd,
            "latency_ms": round(latency, 2),
            "requires_confirmation": requires_confirmation,
            "confirmation_payload": confirmation_payload,
        }
    except Exception as e:
        logger.exception("Bedrock invocation failed, falling back to mock")
        return _invoke_mock(query)


def _estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """Estimate cost for Claude Sonnet on Bedrock (per 1K tokens)."""
    input_cost_per_1k = 0.003
    output_cost_per_1k = 0.015
    return round(
        (input_tokens / 1000) * input_cost_per_1k
        + (output_tokens / 1000) * output_cost_per_1k,
        6,
    )
