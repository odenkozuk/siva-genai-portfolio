"""
PDF Data Extractor using PyMuPDF (fitz).
Extracts raw text, tables, and page-level content from revenue/contract PDFs.
"""

import fitz  # PyMuPDF
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class PageContent:
    page_number: int
    text: str
    tables: list[list[list[str]]] = field(default_factory=list)
    has_figures: bool = False


@dataclass
class DocumentContent:
    file_path: str
    total_pages: int
    pages: list[PageContent] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return "\n\n".join(f"[Page {p.page_number}]\n{p.text}" for p in self.pages)

    @property
    def all_tables(self) -> list[dict]:
        result = []
        for page in self.pages:
            for table in page.tables:
                result.append({"page": page.page_number, "rows": table})
        return result


def extract_tables_from_page(page: fitz.Page) -> list[list[list[str]]]:
    """Extract tables from a PDF page using PyMuPDF's find_tables."""
    tables = []
    try:
        tab_finder = page.find_tables()
        for tab in tab_finder.tables:
            rows = []
            for row in tab.extract():
                clean_row = [cell.strip() if cell else "" for cell in row]
                rows.append(clean_row)
            tables.append(rows)
    except Exception:
        pass
    return tables


def extract_pdf(file_path: str | Path) -> DocumentContent:
    """Extract full text and tables from a PDF file using PyMuPDF."""
    file_path = str(file_path)
    doc = fitz.open(file_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        tables = extract_tables_from_page(page)
        has_figures = len(page.get_images(full=True)) > 0
        pages.append(PageContent(
            page_number=page_num + 1,
            text=text.strip(),
            tables=tables,
            has_figures=has_figures,
        ))

    doc.close()
    return DocumentContent(file_path=file_path, total_pages=len(pages), pages=pages)


def extract_text_by_keywords(
    doc_content: DocumentContent,
    keywords: list[str],
    context_chars: int = 500,
) -> dict[str, list[str]]:
    """Find sections of text near revenue-related keywords."""
    full_text = doc_content.full_text
    results: dict[str, list[str]] = {}

    for keyword in keywords:
        keyword_lower = keyword.lower()
        text_lower = full_text.lower()
        matches = []
        start = 0
        while True:
            idx = text_lower.find(keyword_lower, start)
            if idx == -1:
                break
            snippet_start = max(0, idx - 100)
            snippet_end = min(len(full_text), idx + context_chars)
            matches.append(full_text[snippet_start:snippet_end].strip())
            start = idx + 1
        if matches:
            results[keyword] = matches

    return results


def batch_extract(input_dir: str | Path) -> list[DocumentContent]:
    """Extract content from all PDFs in a directory."""
    input_dir = Path(input_dir)
    pdf_files = list(input_dir.glob("*.pdf"))
    results = []
    for pdf_file in pdf_files:
        print(f"Extracting: {pdf_file.name}")
        content = extract_pdf(pdf_file)
        results.append(content)
    print(f"Extracted {len(results)} PDF(s) from {input_dir}")
    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        content = extract_pdf(sys.argv[1])
        print(f"Pages: {content.total_pages}")
        print(f"Tables found: {len(content.all_tables)}")
        print("\nFirst 500 chars of text:")
        print(content.full_text[:500])
    else:
        print("Usage: python pdf_extractor.py <path_to_pdf>")
