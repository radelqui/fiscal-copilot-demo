"""Tests for bedrock_agent observability (token/cost extraction)."""
import pytest
from unittest.mock import patch, MagicMock
from app.bedrock_agent import _invoke_bedrock, _estimate_cost


def test_estimate_cost_sonnet():
    cost = _estimate_cost(1000, 500)
    expected = (1000 / 1000) * 0.003 + (500 / 1000) * 0.015
    assert cost == round(expected, 6)


def test_estimate_cost_zero():
    assert _estimate_cost(0, 0) == 0.0


def _make_trace_event(input_tokens: int, output_tokens: int):
    """Build a mock trace event with modelInvocationOutput usage."""
    return {
        "trace": {
            "trace": {
                "orchestrationTrace": {
                    "modelInvocationOutput": {
                        "metadata": {
                            "usage": {
                                "inputTokens": input_tokens,
                                "outputTokens": output_tokens,
                            }
                        }
                    }
                }
            }
        }
    }


def _make_chunk_event(text: str):
    return {"chunk": {"bytes": text.encode("utf-8")}}


def _make_tool_event(function_name: str, params: list[dict] | None = None):
    return {
        "trace": {
            "trace": {
                "orchestrationTrace": {
                    "invocationInput": {
                        "actionGroupInvocationInput": {
                            "function": function_name,
                            "parameters": params or [],
                        }
                    }
                }
            }
        }
    }


@pytest.mark.asyncio
async def test_invoke_bedrock_extracts_usage():
    """Test that _invoke_bedrock extracts tokens from trace events."""
    mock_events = [
        _make_trace_event(100, 50),
        _make_tool_event("calcular_itbis", [{"name": "monto", "value": "100000"}]),
        _make_trace_event(200, 80),
        _make_chunk_event("El ITBIS es 18,000"),
    ]

    mock_client = MagicMock()
    mock_client.invoke_agent.return_value = {"completion": mock_events}

    with patch("app.bedrock_agent.boto3") as mock_boto3, \
         patch("app.bedrock_agent._agent_config", {"AGENT_ID": "TEST", "ALIAS_ID": "TEST"}):
        mock_boto3.client.return_value = mock_client
        result = await _invoke_bedrock("test query")

    assert result["input_tokens"] == 300  # 100 + 200
    assert result["output_tokens"] == 130  # 50 + 80
    assert result["cost_usd"] > 0
    assert result["provider"] == "bedrock"
    assert len(result["tools_used"]) == 1
    assert result["tools_used"][0]["tool_name"] == "calcular_itbis"


@pytest.mark.asyncio
async def test_invoke_bedrock_no_trace_events():
    """Test graceful handling when no trace events have usage."""
    mock_events = [
        _make_chunk_event("Hello world"),
    ]

    mock_client = MagicMock()
    mock_client.invoke_agent.return_value = {"completion": mock_events}

    with patch("app.bedrock_agent.boto3") as mock_boto3, \
         patch("app.bedrock_agent._agent_config", {"AGENT_ID": "TEST", "ALIAS_ID": "TEST"}):
        mock_boto3.client.return_value = mock_client
        result = await _invoke_bedrock("test query")

    assert result["input_tokens"] == 0
    assert result["output_tokens"] == 0
    assert result["cost_usd"] == 0.0
    assert result["response"] == "Hello world"
