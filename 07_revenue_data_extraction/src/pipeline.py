"""
End-to-end Revenue Data Extraction Pipeline.
Orchestrates: PDF ingestion → text extraction (PyMuPDF) → LangChain chains → Azure OpenAI → structured output.
"""

import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

from pdf_extractor import extract_pdf, extract_text_by_keywords, DocumentContent
from langchain_chains import extract_and_validate, extract_from_chunks, merge_chunk_results
from revenue_fields import RevenueFields, REVENUE_KEYWORDS

load_dotenv()

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./data/output"))
PDF_INPUT_DIR = Path(os.getenv("PDF_INPUT_DIR", "./data/input"))
BLOB_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER_NAME", "revenue-docs")
CHUNK_THRESHOLD = 3000  # Characters: above this, use chunked extraction


def download_from_blob(local_dir: Path) -> list[Path]:
    """Download PDFs from Azure Blob Storage to local directory."""
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        print("No blob connection string — skipping download, using local files.")
        return []

    local_dir.mkdir(parents=True, exist_ok=True)
    blob_service = BlobServiceClient.from_connection_string(conn_str)
    container_client = blob_service.get_container_client(BLOB_CONTAINER)

    downloaded = []
    for blob in container_client.list_blobs():
        if blob.name.endswith(".pdf"):
            local_path = local_dir / Path(blob.name).name
            with open(local_path, "wb") as f:
                data = container_client.download_blob(blob.name).readall()
                f.write(data)
            downloaded.append(local_path)
            print(f"Downloaded: {blob.name}")

    return downloaded


def process_single_pdf(pdf_path: Path) -> RevenueFields | None:
    """Full extraction pipeline for a single PDF."""
    print(f"\nProcessing: {pdf_path.name}")

    doc_content: DocumentContent = extract_pdf(pdf_path)
    print(f"  Pages: {doc_content.total_pages} | Tables: {len(doc_content.all_tables)}")

    keyword_snippets = extract_text_by_keywords(doc_content, REVENUE_KEYWORDS[:10])
    print(f"  Revenue keyword hits: {len(keyword_snippets)}")

    full_text = doc_content.full_text
    if len(full_text) > CHUNK_THRESHOLD:
        print(f"  Long document ({len(full_text)} chars) — using chunked extraction")
        chunk_results = extract_from_chunks(full_text)
        result = merge_chunk_results(chunk_results)
    else:
        result = extract_and_validate(full_text)

    result.source_page = 1
    return result


def save_results(results: list[dict], output_dir: Path) -> Path:
    """Save extracted results as JSON and CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = output_dir / f"revenue_extraction_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nJSON saved: {json_path}")

    if results:
        df = pd.DataFrame(results)
        csv_path = output_dir / f"revenue_extraction_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        print(f"CSV saved: {csv_path}")

    return json_path


def run_pipeline(input_dir: Path | None = None) -> list[dict]:
    """Main pipeline entrypoint: extract revenue fields from all PDFs."""
    input_dir = input_dir or PDF_INPUT_DIR
    input_dir.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    blob_files = download_from_blob(input_dir)
    local_pdfs = list(input_dir.glob("*.pdf"))
    all_pdfs = list({f.name: f for f in local_pdfs + blob_files}.values())

    if not all_pdfs:
        print(f"No PDF files found in {input_dir}")
        return []

    print(f"Found {len(all_pdfs)} PDF(s) to process")
    all_results = []

    for pdf_path in all_pdfs:
        result = process_single_pdf(pdf_path)
        if result:
            result_dict = result.model_dump()
            result_dict["source_file"] = pdf_path.name
            result_dict["processed_at"] = datetime.utcnow().isoformat()
            all_results.append(result_dict)
            print(f"  Extracted: contract_value={result.contract_value} | confidence={result.confidence_score:.2f}")

    save_results(all_results, OUTPUT_DIR)
    print(f"\nPipeline complete. Processed {len(all_results)} document(s).")
    return all_results


if __name__ == "__main__":
    results = run_pipeline()
    if results:
        print("\nSample result:")
        print(json.dumps(results[0], indent=2))
