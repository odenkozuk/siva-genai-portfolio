# RAG Chatbot — Azure AI Search + Azure OpenAI

A Retrieval-Augmented Generation (RAG) chatbot built on Azure AI Search and Azure OpenAI. Deployed to reduce L0 IT support ticket volume by **20%** by surfacing accurate knowledge base answers instantly.

---

## Overview

Traditional helpdesk systems rely on keyword search, which returns irrelevant or outdated results. This RAG chatbot embeds enterprise knowledge base articles into Azure AI Search and uses GPT-4o to synthesize grounded, accurate answers — eliminating unnecessary ticket creation.

---

## Architecture

```
User Query
    │
    ▼
Azure OpenAI Embeddings (text-embedding-ada-002)
    │
    ▼
Azure AI Search (Vector + Semantic Retrieval)
    │  Top-5 relevant documents
    ▼
Azure OpenAI GPT-4o (Answer generation with context)
    │
    ▼
Grounded Answer + Source Citations
```

---

## Features

- Semantic vector search over enterprise knowledge base
- GPT-4o answer generation grounded strictly in retrieved context
- Source document citations returned with every answer
- LangChain `RetrievalQA` chain with custom system prompt
- Configurable retrieval depth (`k` value)
- Document indexing utility for bulk KB uploads

---

## Project Structure

```
01_rag_chatbot_azure/
├── src/
│   ├── rag_pipeline.py       # Main RAG chain: retriever + LLM
│   └── config.py             # Environment variable loader
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
# Edit .env with your Azure credentials
```

| Variable | Description |
|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI resource endpoint |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | Chat model deployment name (e.g. `gpt-4o`) |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Embedding model deployment name |
| `AZURE_SEARCH_ENDPOINT` | Azure AI Search endpoint |
| `AZURE_SEARCH_API_KEY` | Azure AI Search admin key |
| `AZURE_SEARCH_INDEX_NAME` | Name of the search index |

### 3. Index your knowledge base

```python
from src.rag_pipeline import index_documents

documents = [
    {"content": "To reset your VPN, ...", "source": "kb-001", "title": "VPN Reset Guide"},
    {"content": "Password reset steps ...", "source": "kb-002", "title": "Password Reset"},
]
index_documents(documents)
```

### 4. Run the chatbot

```bash
python src/rag_pipeline.py
```

---

## Usage

```python
from src.rag_pipeline import chat

response = chat("How do I connect to the corporate VPN?")
print(response["answer"])
print(response["sources"])
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Azure OpenAI GPT-4o |
| Embeddings | Azure OpenAI text-embedding-ada-002 |
| Vector Store | Azure AI Search |
| Orchestration | LangChain RetrievalQA |
| Language | Python 3.12 |

---

## Results

- **20% reduction** in L0 support ticket volume after deployment
- Sub-2 second average response time
- Source citations with every answer for auditability
