"""
Hallucination Monitor and Feedback Evaluation System.
Uses LangSmith + Arize Phoenix for tracing, evaluation and accuracy improvement.
"""

import os
import json
from typing import Any
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from langsmith import Client
from langsmith.evaluation import evaluate, LangChainStringEvaluator

load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "observability-eval")


HALLUCINATION_EVAL_PROMPT = PromptTemplate(
    input_variables=["question", "answer", "context"],
    template="""You are an AI evaluator. Assess whether the answer is grounded in the provided context.

Question: {question}
Context: {context}
Answer: {answer}

Evaluation criteria:
1. Is every claim in the answer supported by the context?
2. Does the answer avoid adding information not present in the context?
3. Is the answer factually consistent with the context?

Respond with JSON:
{{"grounded": true/false, "score": 0.0-1.0, "issues": ["list of hallucinations if any"]}}

JSON Response:""",
)


def build_llm(temperature: float = 0) -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        api_version="2024-02-01",
        temperature=temperature,
    )


def evaluate_hallucination(question: str, answer: str, context: str) -> dict[str, Any]:
    """Evaluate whether an LLM answer is grounded in the context."""
    llm = build_llm()
    chain = HALLUCINATION_EVAL_PROMPT | llm
    result = chain.invoke({"question": question, "answer": answer, "context": context})
    try:
        return json.loads(result.content)
    except json.JSONDecodeError:
        return {"grounded": False, "score": 0.0, "issues": ["Could not parse evaluation response"]}


def batch_evaluate(qa_pairs: list[dict]) -> list[dict]:
    """Evaluate a batch of question-answer-context triplets."""
    results = []
    for pair in qa_pairs:
        evaluation = evaluate_hallucination(
            question=pair["question"],
            answer=pair["answer"],
            context=pair["context"],
        )
        results.append({
            "question": pair["question"],
            "answer": pair["answer"][:100] + "...",
            "grounded": evaluation.get("grounded"),
            "score": evaluation.get("score"),
            "issues": evaluation.get("issues", []),
        })
    return results


def compute_accuracy_metrics(evaluations: list[dict]) -> dict:
    """Compute aggregate accuracy metrics from evaluations."""
    if not evaluations:
        return {}
    total = len(evaluations)
    grounded_count = sum(1 for e in evaluations if e.get("grounded"))
    avg_score = sum(e.get("score", 0) for e in evaluations) / total
    hallucinated = [e for e in evaluations if not e.get("grounded")]
    return {
        "total_evaluated": total,
        "grounded_responses": grounded_count,
        "hallucinated_responses": total - grounded_count,
        "accuracy_rate": round(grounded_count / total, 3),
        "average_score": round(avg_score, 3),
        "common_issues": [issue for e in hallucinated for issue in e.get("issues", [])],
    }


if __name__ == "__main__":
    test_pairs = [
        {
            "question": "What is the company's revenue in Q3?",
            "context": "Q3 revenue was $4.2M, exceeding the target by 5%.",
            "answer": "The company's Q3 revenue was $4.2M, which was 5% above target.",
        },
        {
            "question": "Who is the CEO?",
            "context": "Q3 revenue was $4.2M, exceeding the target by 5%.",
            "answer": "The CEO is John Smith.",
        },
    ]
    results = batch_evaluate(test_pairs)
    metrics = compute_accuracy_metrics(results)
    print("Evaluation Results:")
    for r in results:
        print(f"  Q: {r['question'][:50]} | Grounded: {r['grounded']} | Score: {r['score']}")
    print(f"\nMetrics: {json.dumps(metrics, indent=2)}")
