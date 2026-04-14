"""
Azure Blob Storage utilities for uploading/downloading revenue PDFs and results.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContentSettings

load_dotenv()


def get_blob_client() -> BlobServiceClient:
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING not set in environment.")
    return BlobServiceClient.from_connection_string(conn_str)


def upload_result(local_path: Path, blob_name: str | None = None) -> str:
    """Upload an extraction result file to Azure Blob Storage."""
    blob_service = get_blob_client()
    container = os.getenv("AZURE_BLOB_CONTAINER_NAME", "revenue-docs")
    blob_name = blob_name or f"results/{local_path.name}"

    with open(local_path, "rb") as data:
        content_type = "application/json" if local_path.suffix == ".json" else "text/csv"
        blob_service.get_blob_client(container=container, blob=blob_name).upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
    print(f"Uploaded {local_path.name} to blob: {blob_name}")
    return blob_name


def list_pdfs_in_blob() -> list[str]:
    """List all PDF files in the blob container."""
    blob_service = get_blob_client()
    container = os.getenv("AZURE_BLOB_CONTAINER_NAME", "revenue-docs")
    container_client = blob_service.get_container_client(container)
    return [blob.name for blob in container_client.list_blobs() if blob.name.endswith(".pdf")]
