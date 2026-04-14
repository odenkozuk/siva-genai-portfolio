"""
Feedback Evaluation System with LangSmith tracing and Phoenix observability.
Captures user feedback and improves response quality over time.
"""

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

langsmith_client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))


def log_feedback(
    run_id: str,
    score: float,
    comment: str = "",
    user_id: str = "anonymous",
) -> dict:
    """Log user feedback for a specific LLM run to LangSmith."""
    feedback_id = str(uuid.uuid4())
    try:
        langsmith_client.create_feedback(
            run_id=run_id,
            key="user_rating",
            score=score,
            comment=comment,
            source_info={"user_id": user_id},
        )
        return {
            "feedback_id": feedback_id,
            "run_id": run_id,
            "score": score,
            "logged_at": datetime.utcnow().isoformat(),
            "status": "logged",
        }
    except Exception as e:
        return {"feedback_id": feedback_id, "status": "error", "error": str(e)}


def get_run_metrics(project_name: str, limit: int = 100) -> dict:
    """Retrieve aggregate metrics for a LangSmith project."""
    try:
        runs = list(langsmith_client.list_runs(
            project_name=project_name,
            limit=limit,
        ))
        total = len(runs)
        if total == 0:
            return {"total_runs": 0}

        total_tokens = sum(
            (r.total_tokens or 0) for r in runs
        )
        error_runs = [r for r in runs if r.error]
        return {
            "total_runs": total,
            "error_rate": round(len(error_runs) / total, 3),
            "total_tokens": total_tokens,
            "avg_tokens_per_run": round(total_tokens / total),
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("Feedback Evaluator initialized.")
    print("Connect to LangSmith to track runs and log feedback.")
    print("Set LANGSMITH_API_KEY and LANGSMITH_PROJECT in your .env file.")
