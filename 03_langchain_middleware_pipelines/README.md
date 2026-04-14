# LangChain Middleware Pipelines

Enterprise-grade LangChain middleware pipelines featuring summarization chains, Human-in-the-Loop (HITL) approval checkpoints, and auditable agent-tool integrations — enabling controlled, explainable AI workflows.

---

## Overview

Unrestricted LLM agents can take unintended actions and generate outputs that are hard to audit. This project implements a middleware layer that intercepts agent actions for human review, logs all LLM calls for compliance, and uses map-reduce summarization chains to handle long enterprise documents.

---

## Architecture

```
User Input
    │
    ▼
LangChain Agent (GPT-4o)
    │
    ▼
Audit Callback Handler  ←── logs all LLM calls + tool uses
    │
    ▼
HITL Checkpoint  ←── human approves/rejects proposed action
    │
    ├── Approved ──► Execute Action ──► Result
    └── Rejected ──► Notify User
```

---

## Features

### Summarization Chain (`summarization_chain.py`)
- **Map-reduce strategy** for long documents (>4000 tokens)
- Custom map prompt focuses on key facts, figures, and decisions
- Custom combine prompt produces executive summaries
- Batch summarization for multiple documents

### Human-in-the-Loop Pipeline (`hitl_pipeline.py`)
- LangGraph state machine with explicit approval node
- Agent proposes action → human approves/rejects → execute or abort
- Persistent checkpointing with `MemorySaver`
- Thread-based session management for multi-user support

### Middleware Agent (`middleware.py`)
- `AuditCallbackHandler` logs every LLM call and tool use
- Agent-tool integration with `search_knowledge_base` and `create_ticket` tools
- Full `AgentExecutor` with configurable iteration limits

---

## Project Structure

```
03_langchain_middleware_pipelines/
├── src/
│   ├── summarization_chain.py  # Map-reduce document summarization
│   ├── hitl_pipeline.py        # LangGraph HITL approval workflow
│   └── middleware.py           # Auditable agent-tool middleware
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
| `LANGSMITH_API_KEY` | LangSmith tracing key (optional) |
| `LANGSMITH_PROJECT` | LangSmith project name (optional) |

---

## Usage

### Document Summarization

```python
from src.summarization_chain import summarize_text

summary = summarize_text(long_document_text, chain_type="map_reduce")
print(summary)
```

### Human-in-the-Loop Workflow

```python
from src.hitl_pipeline import run_hitl

result = run_hitl("Send budget report to all department heads.")
# Console prints the proposed action and waits for: yes/no
```

### Middleware Agent

```python
from src.middleware import run_agent

response = run_agent("What is the expense reimbursement policy?")
# AuditCallbackHandler logs all LLM calls and tool uses to console
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Azure OpenAI GPT-4o |
| Orchestration | LangChain, LangGraph |
| State Machine | LangGraph StateGraph |
| Checkpointing | LangGraph MemorySaver |
| Tracing | LangSmith (optional) |
| Language | Python 3.12 |
