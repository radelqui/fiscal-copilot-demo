"""LLM Router — routes queries to different models for comparison.

Supported routes:
- bedrock-haiku: Claude Haiku 4.5 via Bedrock Converse
- bedrock-nova-micro: Amazon Nova Micro via Bedrock Converse
- openai-gpt4o-mini: GPT-4o-mini via OpenAI API
- bedrock-sonnet-4-6: Claude Sonnet 4.6 (PENDIENTE_HABILITACION)
"""

import json
import os
import time
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import boto3

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / "app" / "agent" / "system_prompt.py"


def _load_system_prompt() -> str:
    """Load the fiscal agent system prompt."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("system_prompt", SYSTEM_PROMPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SYSTEM_PROMPT


_system_prompt: str | None = None


def get_system_prompt() -> str:
    global _system_prompt
    if _system_prompt is None:
        _system_prompt = _load_system_prompt()
    return _system_prompt


@dataclass
class RouteResult:
    route: str
    response: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


PRICING = {
    "bedrock-haiku": {"input": 0.0008, "output": 0.004},
    "bedrock-nova-micro": {"input": 0.000035, "output": 0.00014},
    "openai-gpt4o-mini": {"input": 0.00015, "output": 0.0006},
    "bedrock-sonnet-4-6": {"input": 0.003, "output": 0.015},
}


def _estimate_cost(route: str, input_tokens: int, output_tokens: int) -> float:
    p = PRICING.get(route, {"input": 0, "output": 0})
    return round(
        (input_tokens / 1000) * p["input"]
        + (output_tokens / 1000) * p["output"],
        6,
    )


def _load_openai_key() -> str | None:
    """Load OpenAI API key from config file."""
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    cfg = Path.home() / ".env-demototal"
    if cfg.exists():
        for line in cfg.read_text().strip().split("\n"):
            if line.startswith("OPENAI_API_KEY="):
                key = line.split("=", 1)[1].strip()
                os.environ["OPENAI_API_KEY"] = key
                return key
    return None


def route_bedrock_haiku(query: str) -> RouteResult:
    """Route via Claude Haiku 4.5 on Bedrock Converse."""
    client = boto3.client("bedrock-runtime", region_name="eu-central-1")
    system_prompt = get_system_prompt()
    start = time.monotonic()
    try:
        r = client.converse(
            modelId="eu.anthropic.claude-haiku-4-5-20251001-v1:0",
            system=[{"text": system_prompt}],
            messages=[{"role": "user", "content": [{"text": query}]}],
            inferenceConfig={"maxTokens": 512, "temperature": 0.1},
        )
        latency = (time.monotonic() - start) * 1000
        response = r["output"]["message"]["content"][0]["text"]
        usage = r["usage"]
        return RouteResult(
            route="bedrock-haiku",
            response=response,
            input_tokens=usage["inputTokens"],
            output_tokens=usage["outputTokens"],
            cost_usd=_estimate_cost("bedrock-haiku", usage["inputTokens"], usage["outputTokens"]),
            latency_ms=round(latency, 2),
        )
    except Exception as e:
        latency = (time.monotonic() - start) * 1000
        return RouteResult(
            route="bedrock-haiku", response="", input_tokens=0, output_tokens=0,
            cost_usd=0.0, latency_ms=round(latency, 2), error=str(e),
        )


def route_bedrock_nova_micro(query: str) -> RouteResult:
    """Route via Amazon Nova Micro on Bedrock Converse."""
    client = boto3.client("bedrock-runtime", region_name="eu-central-1")
    system_prompt = get_system_prompt()
    start = time.monotonic()
    try:
        r = client.converse(
            modelId="eu.amazon.nova-micro-v1:0",
            system=[{"text": system_prompt}],
            messages=[{"role": "user", "content": [{"text": query}]}],
            inferenceConfig={"maxTokens": 512, "temperature": 0.1},
        )
        latency = (time.monotonic() - start) * 1000
        response = r["output"]["message"]["content"][0]["text"]
        usage = r["usage"]
        return RouteResult(
            route="bedrock-nova-micro",
            response=response,
            input_tokens=usage["inputTokens"],
            output_tokens=usage["outputTokens"],
            cost_usd=_estimate_cost("bedrock-nova-micro", usage["inputTokens"], usage["outputTokens"]),
            latency_ms=round(latency, 2),
        )
    except Exception as e:
        latency = (time.monotonic() - start) * 1000
        return RouteResult(
            route="bedrock-nova-micro", response="", input_tokens=0, output_tokens=0,
            cost_usd=0.0, latency_ms=round(latency, 2), error=str(e),
        )


def route_openai_gpt4o_mini(query: str) -> RouteResult:
    """Route via GPT-4o-mini on OpenAI with JSON schema strict output."""
    key = _load_openai_key()
    if not key:
        return RouteResult(
            route="openai-gpt4o-mini", response="", input_tokens=0, output_tokens=0,
            cost_usd=0.0, latency_ms=0.0, error="OPENAI_API_KEY not available",
        )

    import openai
    client = openai.OpenAI(api_key=key, base_url="https://api.openai.com/v1")
    system_prompt = get_system_prompt()
    start = time.monotonic()
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            max_tokens=512,
            temperature=0.1,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "fiscal_response",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "respuesta": {"type": "string"},
                            "herramienta_sugerida": {"type": "string"},
                            "confianza": {"type": "string"},
                        },
                        "required": ["respuesta", "herramienta_sugerida", "confianza"],
                        "additionalProperties": False,
                    },
                },
            },
        )
        latency = (time.monotonic() - start) * 1000
        content = r.choices[0].message.content
        try:
            parsed = json.loads(content)
            response_text = parsed.get("respuesta", content)
        except (json.JSONDecodeError, TypeError):
            response_text = content

        return RouteResult(
            route="openai-gpt4o-mini",
            response=response_text,
            input_tokens=r.usage.prompt_tokens,
            output_tokens=r.usage.completion_tokens,
            cost_usd=_estimate_cost("openai-gpt4o-mini", r.usage.prompt_tokens, r.usage.completion_tokens),
            latency_ms=round(latency, 2),
        )
    except Exception as e:
        latency = (time.monotonic() - start) * 1000
        return RouteResult(
            route="openai-gpt4o-mini", response="", input_tokens=0, output_tokens=0,
            cost_usd=0.0, latency_ms=round(latency, 2), error=str(e),
        )


def route_bedrock_sonnet_4_6(query: str) -> RouteResult:
    """Route via Claude Sonnet 4.6 on Bedrock — PENDIENTE_HABILITACION."""
    return RouteResult(
        route="bedrock-sonnet-4-6",
        response="",
        input_tokens=0,
        output_tokens=0,
        cost_usd=0.0,
        latency_ms=0.0,
        error="PENDIENTE_HABILITACION: modelo sonnet-4-6 requiere activacion Marketplace",
    )


ROUTES = {
    "bedrock-haiku": route_bedrock_haiku,
    "bedrock-nova-micro": route_bedrock_nova_micro,
    "openai-gpt4o-mini": route_openai_gpt4o_mini,
    "bedrock-sonnet-4-6": route_bedrock_sonnet_4_6,
}


def run_route(route_name: str, query: str) -> RouteResult:
    """Run a query through a named route."""
    fn = ROUTES.get(route_name)
    if fn is None:
        return RouteResult(
            route=route_name, response="", input_tokens=0, output_tokens=0,
            cost_usd=0.0, latency_ms=0.0, error=f"Unknown route: {route_name}",
        )
    return fn(query)


def available_routes() -> list[str]:
    """Return list of route names that are not PENDIENTE."""
    return [k for k in ROUTES if k != "bedrock-sonnet-4-6"]
