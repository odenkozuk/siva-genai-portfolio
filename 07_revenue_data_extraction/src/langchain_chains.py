"""
LangChain chains for structured revenue field extraction using Azure OpenAI.
Uses structured output (JSON mode) with Pydantic validation.
"""

import os
import json
from typing import Any
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from revenue_fields import RevenueFields, REVENUE_KEYWORDS

load_dotenv()


EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a financial data extraction specialist. Extract revenue and contract fields
from the provided document text with high precision.

Return a JSON object matching this schema exactly:
- contract_id: Contract/agreement identifier
- client_name: Client or customer name
- vendor_name: Vendor or service provider name
- contract_value: Total contract value with currency symbol
- annual_revenue: Annual revenue figure
- quarterly_revenue: Quarterly revenue figure
- monthly_revenue: Monthly revenue figure
- contract_start_date: Start date (YYYY-MM-DD if possible)
- contract_end_date: End date (YYYY-MM-DD if possible)
- payment_terms: Payment terms (NET-30, milestone, etc.)
- currency: Currency code (USD, EUR, INR, etc.)
- revenue_type: recurring / one-time / milestone
- billing_frequency: monthly / quarterly / annual
- discount: Discount amount or percentage
- tax_rate: Tax rate or GST/VAT details
- net_revenue: Net revenue after deductions
- project_name: Project or engagement name
- cost_center: Cost center or department code
- purchase_order: PO number
- confidence_score: Your confidence in extraction (0.0 to 1.0)
- source_page: Page number where primary data was found (integer or null)
- extraction_notes: Any caveats or ambiguities

Use null for fields not found in the document. Do NOT hallucinate values."""),
    ("human", """Extract revenue fields from the following document text:

{document_text}

Return ONLY valid JSON, no markdown, no explanation."""),
])

VALIDATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a financial data validator. Review the extracted revenue fields and:
1. Check for inconsistencies (e.g. net > gross, end before start)
2. Normalize date formats to YYYY-MM-DD
3. Normalize currency amounts (remove commas, standardize symbols)
4. Adjust confidence_score based on data quality
5. Add validation notes to extraction_notes

Return the corrected JSON with all original fields."""),
    ("human", """Validate and correct these extracted revenue fields:

{extracted_json}

Return ONLY valid JSON."""),
])


def build_llm() -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        api_version="2024-02-01",
        temperature=0,
        model_kwargs={"response_format": {"type": "json_object"}},
    )


def build_extraction_chain():
    """Chain: document text -> extracted revenue fields JSON."""
    llm = build_llm()
    parser = JsonOutputParser(pydantic_object=RevenueFields)
    return EXTRACTION_PROMPT | llm | parser


def build_validation_chain():
    """Chain: raw extracted JSON -> validated/normalized JSON."""
    llm = build_llm()
    parser = JsonOutputParser(pydantic_object=RevenueFields)
    return VALIDATION_PROMPT | llm | parser


def extract_revenue_fields(document_text: str) -> RevenueFields:
    """Extract revenue fields from document text using the extraction chain."""
    chain = build_extraction_chain()
    raw_result = chain.invoke({"document_text": document_text[:8000]})
    return RevenueFields(**raw_result)


def extract_and_validate(document_text: str) -> RevenueFields:
    """Full pipeline: extract then validate revenue fields."""
    extraction_chain = build_extraction_chain()
    validation_chain = build_validation_chain()

    extracted = extraction_chain.invoke({"document_text": document_text[:8000]})
    validated = validation_chain.invoke({"extracted_json": json.dumps(extracted, indent=2)})
    return RevenueFields(**validated)


def extract_from_chunks(document_text: str, chunk_size: int = 4000) -> list[RevenueFields]:
    """Extract revenue fields from long documents by splitting into chunks."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=200)
    chunks = splitter.split_text(document_text)

    all_results = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1}/{len(chunks)}...")
        result = extract_revenue_fields(chunk)
        result.extraction_notes = f"Chunk {i + 1} of {len(chunks)}. {result.extraction_notes or ''}"
        all_results.append(result)

    return all_results


def merge_chunk_results(results: list[RevenueFields]) -> RevenueFields:
    """Merge extracted fields from multiple chunks, keeping non-null values."""
    merged: dict[str, Any] = {}
    for result in results:
        for field_name, value in result.model_dump().items():
            if value is not None and field_name not in ("confidence_score", "extraction_notes", "source_page"):
                if field_name not in merged:
                    merged[field_name] = value

    confidence_scores = [r.confidence_score for r in results if r.confidence_score > 0]
    merged["confidence_score"] = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    merged["extraction_notes"] = f"Merged from {len(results)} chunks."
    return RevenueFields(**merged)


if __name__ == "__main__":
    sample_text = """
    SERVICE AGREEMENT - CONTRACT ID: MSA-2024-0892

    Client: Acme Corporation
    Vendor: TechSolutions India Pvt Ltd
    Project: Digital Transformation Initiative

    Total Contract Value: USD 1,200,000
    Annual Revenue: $400,000
    Billing Frequency: Quarterly ($100,000 per quarter)
    Payment Terms: NET-30 from invoice date

    Contract Period: January 1, 2024 to December 31, 2026
    Purchase Order: PO-ACME-2024-0056
    Cost Center: DT-INNOVATION-2024

    Tax: 18% GST applicable on all invoices
    Discount: 5% loyalty discount applied
    Net Revenue after discount: $1,140,000

    Revenue Type: Recurring
    Currency: USD
    """
    result = extract_and_validate(sample_text)
    print("Extracted Revenue Fields:")
    print(result.model_dump_json(indent=2))
