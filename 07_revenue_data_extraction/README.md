# Revenue Data Extraction Pipeline

End-to-end intelligent pipeline for automated extraction of revenue and contract fields from PDF documents — combining **PyMuPDF** for PDF parsing, **LangChain chains** for structured extraction, and **Azure OpenAI GPT-4o** for field identification. Reduced manual data extraction effort by **60%**.

---

## Overview

Finance and contracts teams manually extract revenue data (contract values, billing terms, PO numbers, payment schedules) from hundreds of PDF documents monthly. This pipeline automates the full process: ingest PDFs from Azure Blob Storage, extract raw text and tables with PyMuPDF, then use a two-stage LangChain chain (extract → validate) to produce structured JSON/CSV output.

---

## Architecture

```
Azure Blob Storage (PDF source)
     │  download_from_blob()
     ▼
PyMuPDF Text + Table Extraction
     │  extract_pdf() → DocumentContent
     │  extract_text_by_keywords() → revenue snippets
     ▼
LangChain Extraction Chain (Azure OpenAI GPT-4o, JSON mode)
     │  EXTRACTION_PROMPT → raw RevenueFields JSON
     ▼
LangChain Validation Chain (Azure OpenAI GPT-4o)
     │  VALIDATION_PROMPT → normalized + validated JSON
     ▼
Pydantic RevenueFields Model (20+ fields)
     │
     ├──► JSON output  (revenue_extraction_<timestamp>.json)
     └──► CSV output   (revenue_extraction_<timestamp>.csv)
```

Long documents (>3000 chars) are automatically split into chunks, each extracted separately, then merged into a single result.

---

## Extracted Revenue Fields

| Field | Description |
|-------|-------------|
| `contract_id` | Contract / agreement identifier |
| `client_name` | Client or customer name |
| `vendor_name` | Vendor or service provider |
| `contract_value` | Total contract value |
| `annual_revenue` | Annual revenue figure |
| `quarterly_revenue` | Quarterly revenue figure |
| `monthly_revenue` | Monthly revenue figure |
| `contract_start_date` | Contract start date (YYYY-MM-DD) |
| `contract_end_date` | Contract end date (YYYY-MM-DD) |
| `payment_terms` | NET-30, milestone, etc. |
| `currency` | USD, EUR, INR, etc. |
| `revenue_type` | recurring / one-time / milestone |
| `billing_frequency` | monthly / quarterly / annual |
| `discount` | Discount amount or percentage |
| `tax_rate` | GST/VAT rate |
| `net_revenue` | Net revenue after deductions |
| `project_name` | Project or engagement name |
| `cost_center` | Cost center / department code |
| `purchase_order` | PO number |
| `confidence_score` | Extraction confidence (0.0–1.0) |

---

## Project Structure

```
07_revenue_data_extraction/
├── src/
│   ├── pdf_extractor.py       # PyMuPDF: text, table, keyword extraction
│   ├── revenue_fields.py      # Pydantic schema for 20+ revenue fields
│   ├── langchain_chains.py    # Extraction + validation LangChain chains
│   ├── pipeline.py            # End-to-end orchestration pipeline
│   └── azure_blob_utils.py    # Azure Blob upload/download helpers
├── data/
│   ├── input/                 # Place input PDFs here
│   └── output/                # Extracted JSON + CSV saved here
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
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | Chat model deployment (e.g. `gpt-4o`) |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Blob Storage connection string |
| `AZURE_BLOB_CONTAINER_NAME` | Blob container holding source PDFs |
| `PDF_INPUT_DIR` | Local directory for input PDFs |
| `OUTPUT_DIR` | Local directory for output files |

---

## Usage

### Run the full pipeline

```bash
# Place PDFs in data/input/ and run:
python src/pipeline.py
```

Results are saved to `data/output/revenue_extraction_<timestamp>.json` and `.csv`.

### Extract from a single PDF

```python
from src.pdf_extractor import extract_pdf
from src.langchain_chains import extract_and_validate

doc = extract_pdf("data/input/contract.pdf")
fields = extract_and_validate(doc.full_text)
print(fields.model_dump_json(indent=2))
```

### Extract fields from text directly

```python
from src.langchain_chains import extract_and_validate

text = """
CONTRACT ID: MSA-2024-0892
Client: Acme Corporation
Total Contract Value: USD 1,200,000
Payment Terms: NET-30
Contract Period: Jan 1, 2024 to Dec 31, 2026
"""
result = extract_and_validate(text)
print(result.contract_value)   # USD 1,200,000
print(result.payment_terms)    # NET-30
print(result.confidence_score) # 0.92
```

### Extract tables from PDF

```python
from src.pdf_extractor import extract_pdf

doc = extract_pdf("data/input/invoice.pdf")
for table in doc.all_tables:
    print(f"Page {table['page']}:", table["rows"])
```

---

## LangChain Chain Design

### Chain 1: Extraction
```
EXTRACTION_PROMPT (system + user) → AzureChatOpenAI (JSON mode) → JsonOutputParser → RevenueFields
```
- Forces JSON output via `response_format: json_object`
- Prompts model to return `null` for missing fields (no hallucination)
- Processes first 8000 characters per chunk

### Chain 2: Validation
```
VALIDATION_PROMPT → AzureChatOpenAI → JsonOutputParser → RevenueFields
```
- Normalizes dates to YYYY-MM-DD
- Normalizes currency amounts
- Detects inconsistencies (net > gross, end before start)
- Adjusts `confidence_score` based on data quality

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| PDF Parsing | PyMuPDF (fitz) |
| LLM Orchestration | LangChain |
| LLM | Azure OpenAI GPT-4o (JSON mode) |
| Data Validation | Pydantic v2 |
| Blob Storage | Azure Blob Storage |
| Data Output | JSON + Pandas CSV |
| Language | Python 3.12 |

---

## Results

- **60% reduction** in manual revenue data extraction effort
- Extracts 20+ structured fields per document
- Handles multi-page contracts, invoices, and SOW documents
- Two-stage validation reduces field errors by normalizing dates and currency formats
