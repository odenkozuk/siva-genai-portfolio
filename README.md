# Kandula Siva Nagaraju — GenAI Portfolio

**Generative AI Developer** with 3+ years at Cognizant, specializing in RAG pipelines, multi-agent orchestration, LangChain middleware, and Azure AI services. This repository showcases end-to-end GenAI projects built for enterprise use cases.

📧 kandulasiva4571@gmail.com &nbsp;|&nbsp; 📍 India &nbsp;|&nbsp;

---

## Skills

| Category | Technologies |
|----------|-------------|
| **Frameworks** | Neuro-SAN, LangChain, LangGraph, CrewAI, LangSmith, Arize Phoenix |
| **GenAI & ML** | LLMs, RAG, Prompt Engineering, Model Fine-Tuning, Ollama, NLP |
| **Cloud** | Azure OpenAI, Azure AI Search, Azure Form Recognizer, AKS, Docker, Kubernetes |
| **Databases** | Azure SQL, Redis, Pinecone, Weaviate, FAISS |
| **Programming** | Python, .NET, HTML |
| **Dev Tools** | Claude Code (CLI), VS Code, Jupyter Notebook, CI/CD |
| **AI/ML Ops** | LLMOps, Tracing, Observability, Computer Vision, Facial Recognition |

---

## Certifications

| Certificate | Issuer | Date |
|-------------|--------|------|
| Introduction to Model Context Protocol | Anthropic | Mar 10, 2026 |
| Claude Code in Action | Anthropic | Mar 3, 2026 |

---

## Projects

### 01 — RAG Chatbot (Azure AI Search + OpenAI)
> Reduced L0 IT support ticket volume by **20%**

Retrieval-Augmented Generation chatbot using Azure AI Search for semantic vector retrieval and GPT-4o for grounded answer generation. Surfaces accurate KB answers instantly, eliminating unnecessary ticket creation.

**Stack:** LangChain · Azure AI Search · Azure OpenAI · Python

[View Project](./01_rag_chatbot_azure)

---

### 02 — NeuroSAN Multi-Agent Orchestration Framework
> Achieved **85% efficiency and accuracy gain** over manual workflows

Multi-agent orchestration system built with Neuro-SAN. A Main Orchestrator Agent coordinates 7 specialized sub-agents — ServiceNow, CAB, SEAT, FAQ, Approval, Analytics, and Notification — through HOCON-configured routing.

**Stack:** Neuro-SAN · Azure OpenAI · HOCON · ServiceNow REST API · Python

[View Project](./02_neurosan_multi_agent_orchestration)

---

### 03 — LangChain Middleware Pipelines
> Controlled, explainable AI workflows with human approval gates

Enterprise middleware layer featuring map-reduce summarization chains, Human-in-the-Loop (HITL) approval checkpoints via LangGraph, and an auditable agent-tool integration with full callback logging.

**Stack:** LangChain · LangGraph · Azure OpenAI · LangSmith · Python

[View Project](./03_langchain_middleware_pipelines)

---

### 04 — Observability & Feedback Evaluation System
> Improved response accuracy by **10%** through continuous evaluation loops

LLM-as-judge hallucination detection system with batch evaluation, accuracy metrics, and LangSmith feedback logging. Every production response is scored for groundedness and tracked against source context.

**Stack:** LangSmith · Arize Phoenix · Azure OpenAI · OpenTelemetry · Python

[View Project](./04_observability_feedback_system)

---

### 05 — LLM Fine-Tuning (Mistral-7B & LLaMA-3-8B with LoRA/QLoRA)
> Domain-adapted enterprise LLMs using parameter-efficient fine-tuning

QLoRA fine-tuning of Mistral-7B and LLaMA-3-8B for enterprise RAG use cases. Runs on 16GB VRAM using 4-bit NF4 quantization and LoRA adapters — no full GPU cluster needed.

**Stack:** Hugging Face Transformers · PEFT · TRL · bitsandbytes · Python

[View Project](./05_llm_finetuning_mistral_llama)

---

### 06 — AI Microservices on Azure Kubernetes Service (AKS)
> Handles **100K+ daily requests** with auto-scaling and event-driven processing

Containerized FastAPI microservice for AI request processing deployed on AKS with Horizontal Pod Autoscaling (3–20 replicas). Async Azure Queue integration for downstream event processing and audit logging.

**Stack:** FastAPI · Docker · AKS · Azure Storage Queue · Azure OpenAI · Python

[View Project](./06_aks_microservices_azure)

---

### 07 — Revenue Data Extraction Pipeline
> Reduced manual extraction effort by **60%**

End-to-end intelligent pipeline for extracting 20+ structured revenue and contract fields from PDF documents. PyMuPDF handles text and table extraction; a two-stage LangChain chain (extract → validate) produces clean JSON/CSV output via Azure OpenAI in JSON mode.

**Stack:** PyMuPDF · LangChain · Azure OpenAI · Pydantic · Azure Blob Storage · Python

[View Project](./07_revenue_data_extraction)

---

### 08 — ID Card Photo Validation Pipeline
> Reduced manual review effort by **~70%**, improved onboarding compliance

Automated employee ID photo compliance checker using Azure Face API (face detection, head pose, blur) and Azure Computer Vision. Validates background brightness, dimensions, aspect ratio, and face orientation. Batch processes directories and outputs a CSV compliance report.

**Stack:** Azure Face API · Azure Computer Vision · Pillow · Python

[View Project](./08_id_card_photo_validation)

---

## Repository Structure

```
genai-portfolio/
├── 01_rag_chatbot_azure/
├── 02_neurosan_multi_agent_orchestration/
├── 03_langchain_middleware_pipelines/
├── 04_observability_feedback_system/
├── 05_llm_finetuning_mistral_llama/
├── 06_aks_microservices_azure/
├── 07_revenue_data_extraction/
└── 08_id_card_photo_validation/
```

Each project folder contains:
- `src/` — source code
- `requirements.txt` — Python dependencies
- `.env.example` — environment variable template
- `README.md` — project-specific documentation

---

## Getting Started

Each project is independently runnable. General steps:

```bash
# 1. Navigate to a project
cd 07_revenue_data_extraction

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Azure credentials

# 5. Run
python src/pipeline.py
```

---

## Experience

| Role | Company | Period |
|------|---------|--------|
| Associate Developer | Cognizant Technology Solutions | Jul 2025 – Present |
| Programmer Analyst | Cognizant Technology Solutions | Dec 2023 – Jul 2025 |
| Programmer Analyst Trainee | Cognizant Technology Solutions | Dec 2022 – Dec 2023 |
| Intern | Cognizant Technology Solutions | Jun 2022 – Dec 2022 |

---

## Education

**B.Tech** — Vasireddy Venkatadri Institute of Technology, Namburu (2018–2022)
