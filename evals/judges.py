"""LLM-as-Judge metrics for evaluating Fiscal Copilot responses.

Implements:
- Faithfulness (Ragas-style): Is the response grounded in the context/tools?
- Answer Relevancy (Ragas-style): Is the answer relevant to the question?
- Context Precision (Ragas-style): Is the provided context precise?
- GEval (DeepEval): General evaluation of response quality.

Judge model: Bedrock Haiku (fallback from OpenAI due to key issue).
"""

import json
import logging
from dataclasses import dataclass, asdict
from typing import Any

import boto3

logger = logging.getLogger(__name__)

JUDGE_MODEL = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"
JUDGE_REGION = "eu-central-1"


def _judge_call(prompt: str, max_tokens: int = 256) -> str:
    """Call the judge LLM and return the response text."""
    client = boto3.client("bedrock-runtime", region_name=JUDGE_REGION)
    r = client.converse(
        modelId=JUDGE_MODEL,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": 0.0},
    )
    return r["output"]["message"]["content"][0]["text"]


def _extract_score(text: str) -> float:
    """Extract a 0-1 score from judge response."""
    import re
    patterns = [
        r"(?:score|puntuacion|resultado)\s*[:=]\s*([\d.]+)",
        r"\b(0\.\d+|1\.0|0|1)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            val = float(match.group(1))
            if 0 <= val <= 1:
                return val
            if 1 < val <= 10:
                return val / 10
            if 10 < val <= 100:
                return val / 100
    return 0.5


@dataclass
class JudgeResult:
    metric: str
    score: float
    reasoning: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def faithfulness(question: str, answer: str, context: str) -> JudgeResult:
    """Ragas Faithfulness: Is the answer grounded in the context?

    Score 0-1: 1 = fully faithful, 0 = completely unfaithful.
    """
    prompt = f"""You are an evaluation judge. Score the FAITHFULNESS of the answer.

Faithfulness measures whether the answer is grounded in the provided context.
An answer is faithful if all claims can be verified from the context.

Question: {question}
Context: {context}
Answer: {answer}

Instructions:
1. List each claim in the answer.
2. Check if each claim is supported by the context.
3. Assign a score between 0.0 and 1.0.

Respond ONLY with a JSON object:
{{"claims": ["claim1", "claim2"], "supported": [true, false], "score": 0.8, "reasoning": "brief explanation"}}"""

    try:
        raw = _judge_call(prompt)
        try:
            data = json.loads(raw)
            score = float(data.get("score", 0.5))
            reasoning = data.get("reasoning", raw[:200])
        except (json.JSONDecodeError, TypeError):
            score = _extract_score(raw)
            reasoning = raw[:200]

        return JudgeResult(metric="faithfulness", score=min(max(score, 0), 1), reasoning=reasoning)
    except Exception as e:
        return JudgeResult(metric="faithfulness", score=0.0, reasoning=f"Judge error: {e}")


def answer_relevancy(question: str, answer: str) -> JudgeResult:
    """Ragas Answer Relevancy: Is the answer relevant to the question?

    Score 0-1: 1 = perfectly relevant, 0 = completely irrelevant.
    """
    prompt = f"""You are an evaluation judge. Score the ANSWER RELEVANCY.

Answer relevancy measures whether the answer addresses the question asked.
A relevant answer directly responds to the question without unnecessary tangents.

Question: {question}
Answer: {answer}

Instructions:
1. Does the answer address the question directly?
2. Is the information provided useful for the question?
3. Assign a score between 0.0 and 1.0.

Respond ONLY with a JSON object:
{{"score": 0.9, "reasoning": "brief explanation"}}"""

    try:
        raw = _judge_call(prompt)
        try:
            data = json.loads(raw)
            score = float(data.get("score", 0.5))
            reasoning = data.get("reasoning", raw[:200])
        except (json.JSONDecodeError, TypeError):
            score = _extract_score(raw)
            reasoning = raw[:200]

        return JudgeResult(metric="answer_relevancy", score=min(max(score, 0), 1), reasoning=reasoning)
    except Exception as e:
        return JudgeResult(metric="answer_relevancy", score=0.0, reasoning=f"Judge error: {e}")


def context_precision(question: str, answer: str, context: str, tools_used: list[str]) -> JudgeResult:
    """Ragas Context Precision: Is the retrieved context precise for the query?

    Score 0-1: 1 = context perfectly matches needs, 0 = context is irrelevant.
    """
    tools_str = ", ".join(tools_used) if tools_used else "ninguna"
    prompt = f"""You are an evaluation judge. Score the CONTEXT PRECISION.

Context precision measures whether the context (system instructions, tools) used
to generate the answer was appropriate and precise for the question.

Question: {question}
Tools used: {tools_str}
Context/System prompt: {context[:500]}
Answer: {answer}

Instructions:
1. Was the right tool selected (or correctly no tool)?
2. Is the context relevant to answering this specific question?
3. Assign a score between 0.0 and 1.0.

Respond ONLY with a JSON object:
{{"tool_appropriate": true, "context_relevant": true, "score": 0.9, "reasoning": "brief explanation"}}"""

    try:
        raw = _judge_call(prompt)
        try:
            data = json.loads(raw)
            score = float(data.get("score", 0.5))
            reasoning = data.get("reasoning", raw[:200])
        except (json.JSONDecodeError, TypeError):
            score = _extract_score(raw)
            reasoning = raw[:200]

        return JudgeResult(metric="context_precision", score=min(max(score, 0), 1), reasoning=reasoning)
    except Exception as e:
        return JudgeResult(metric="context_precision", score=0.0, reasoning=f"Judge error: {e}")


def geval_fiscal_correctness(question: str, answer: str) -> JudgeResult:
    """DeepEval GEval: domain-specific evaluation of fiscal correctness.

    Uses DeepEval's GEval metric with a custom fiscal correctness criteria.
    """
    try:
        from deepeval.metrics import GEval
        from deepeval.test_case import LLMTestCase, LLMTestCaseParams

        metric = GEval(
            name="Fiscal Correctness",
            criteria=(
                "Evaluate whether the response provides accurate Dominican Republic "
                "tax information. Check: correct ITBIS rate (18%), valid NCF format "
                "rules, correct fiscal calendar dates, and proper use of terminology. "
                "Penalize fabricated data, wrong rates, or non-Dominican tax advice."
            ),
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            threshold=0.7,
        )

        test_case = LLMTestCase(input=question, actual_output=answer)
        metric.measure(test_case)

        return JudgeResult(
            metric="geval_fiscal_correctness",
            score=metric.score if metric.score is not None else 0.0,
            reasoning=metric.reason or "No reasoning provided",
        )
    except Exception as e:
        logger.warning("DeepEval GEval failed, using Haiku fallback: %s", e)
        return _geval_fallback(question, answer)


def _geval_fallback(question: str, answer: str) -> JudgeResult:
    """Fallback GEval using Bedrock Haiku if DeepEval fails."""
    prompt = f"""You are an expert in Dominican Republic tax law (DGII, ITBIS, NCF).
Evaluate the fiscal correctness of this response.

Question: {question}
Answer: {answer}

Criteria:
- ITBIS rate should be 18%
- NCF format: letter (E/B) + 2-digit type code + 10-digit sequence = 13 chars
- Fiscal calendar dates should match DGII deadlines
- No fabricated data or rates

Respond ONLY with a JSON object:
{{"score": 0.9, "reasoning": "brief explanation of fiscal accuracy"}}"""

    try:
        raw = _judge_call(prompt)
        try:
            data = json.loads(raw)
            score = float(data.get("score", 0.5))
            reasoning = data.get("reasoning", raw[:200])
        except (json.JSONDecodeError, TypeError):
            score = _extract_score(raw)
            reasoning = raw[:200]

        return JudgeResult(metric="geval_fiscal_correctness", score=min(max(score, 0), 1), reasoning=reasoning)
    except Exception as e:
        return JudgeResult(metric="geval_fiscal_correctness", score=0.0, reasoning=f"Fallback judge error: {e}")


def evaluate_all_metrics(
    question: str,
    answer: str,
    context: str,
    tools_used: list[str],
) -> list[JudgeResult]:
    """Run all judge metrics on a single Q&A pair."""
    return [
        faithfulness(question, answer, context),
        answer_relevancy(question, answer),
        context_precision(question, answer, context, tools_used),
        geval_fiscal_correctness(question, answer),
    ]
