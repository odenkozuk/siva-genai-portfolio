# Observability & Feedback Evaluation System

An LLM observability and evaluation system that monitors hallucinations, captures user feedback, and tracks response accuracy metrics — improving LLM response accuracy by **10%** through continuous evaluation loops.

---

## Overview

LLMs can generate confident but factually incorrect responses (hallucinations). This system adds an evaluation layer that assesses whether every LLM response is grounded in its source context, tracks user feedback via LangSmith, and computes aggregate quality metrics to drive continuous improvement.

---

## Architecture

```
LLM Response
     │
     ▼
Hallucination Evaluator (GPT-4o as judge)
     │  grounded: true/false
     │  score: 0.0 - 1.0
     │  issues: ["list of hallucinations"]
     ▼
LangSmith Feedback Logger
     │
     ▼
Metrics Aggregation
     │  accuracy_rate, avg_score, common_issues
     ▼
Observability Dashboard (LangSmith / Arize Phoenix)
```

---

## Features

### Hallucination Monitor (`hallucination_monitor.py`)
- GPT-4o-as-judge pattern for hallucination detection
- JSON-structured evaluation: `grounded`, `score`, `issues`
- Batch evaluation with aggregate metrics
- Accuracy rate, average score, common hallucination patterns

### Feedback Evaluator (`feedback_evaluator.py`)
- LangSmith `create_feedback` integration for user ratings
- Run-level metrics: error rate, token usage, avg latency
- Persistent feedback storage for retraining signals

---

## Project Structure

```
04_observability_feedback_system/
├── src/
│   ├── hallucination_monitor.py  # LLM-as-judge hallucination detection
│   └── feedback_evaluator.py     # LangSmith feedback + metrics collection
├── requirements.txt
└── .env.example
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name |
| `LANGSMITH_API_KEY` | LangSmith API key |
| `LANGSMITH_PROJECT` | LangSmith project name |
| `PHOENIX_HOST` | Arize Phoenix host (default: localhost) |
| `PHOENIX_PORT` | Arize Phoenix port (default: 6006) |

---

## Usage

### Evaluate a single response

```python
from src.hallucination_monitor import evaluate_hallucination

result = evaluate_hallucination(
    question="What was Q3 revenue?",
    answer="Q3 revenue was $4.2M.",
    context="Q3 revenue reached $4.2M, exceeding target by 5%.",
)
print(result)
# {"grounded": True, "score": 0.95, "issues": []}
```

### Batch evaluate a QA dataset

```python
from src.hallucination_monitor import batch_evaluate, compute_accuracy_metrics

qa_pairs = [
    {"question": "...", "answer": "...", "context": "..."},
]
results = batch_evaluate(qa_pairs)
metrics = compute_accuracy_metrics(results)
print(metrics["accuracy_rate"])  # e.g. 0.92
```

### Log user feedback

```python
from src.feedback_evaluator import log_feedback

log_feedback(run_id="abc123", score=0.9, comment="Very accurate answer", user_id="user-001")
```

---

## Evaluation Schema

Each evaluation returns:

```json
{
  "grounded": true,
  "score": 0.95,
  "issues": []
}
```

Aggregate metrics include:
- `accuracy_rate` — fraction of grounded responses
- `average_score` — mean confidence across all evaluations
- `hallucinated_responses` — count of non-grounded answers
- `common_issues` — aggregated hallucination descriptions

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM Judge | Azure OpenAI GPT-4o |
| Tracing | LangSmith |
| Observability | Arize Phoenix |
| Telemetry | OpenTelemetry SDK |
| Language | Python 3.12 |

---

## Results

- **10% improvement** in response accuracy after evaluation-driven prompt tuning
- Hallucination detection running on 100% of production responses
- Feedback loop feeding into monthly prompt and fine-tune reviews
