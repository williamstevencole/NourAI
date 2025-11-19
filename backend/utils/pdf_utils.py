import pdfplumber
from pathlib import Path
from .document_index_utils import load_documents_index, find_document_by_path

def load_pdf(pdf_path: Path) -> str:
    """Load text and tables from a PDF."""
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        text += " | ".join([str(cell) if cell else "" for cell in row]) + "\n"

    return text


def get_default_metadata(pdf_path: Path) -> dict:
    """Get default metadata when no index entry is found."""
    return {
        "title": pdf_path.stem,
        "organization": "Organización no especificada",
        "organization_acronym": "",
        "year": None,
        "author": "Autor no especificado",
        "link": None
    }


def extract_document_metadata(pdf_path: Path, documents_index: dict = None) -> dict:
    """Extract metadata from documents_index.json based on file path."""
    if documents_index is None:
        documents_index = load_documents_index()

    path_str = str(pdf_path)
    if "data/" in path_str:
        relative_path = "data/" + path_str.split("data/")[1]
    else:
        relative_path = f"data/{pdf_path.name}"

    doc_info = find_document_by_path(relative_path, documents_index)

    if doc_info:
        return {
            "title": doc_info["title"],
            "organization": doc_info["organization"],
            "organization_acronym": doc_info.get("organization_acronym", ""),
            "year": doc_info.get("year"),
            "author": doc_info.get("author"),
            "link": doc_info.get("link")
        }

    return get_default_metadata(pdf_path)


def load_pdfs_from_directory(directory: Path) -> list[dict]:
    """
    Load all PDFs from a directory with metadata extraction from documents_index.json.
    """
    documents = []

    # Load documents index once for all PDFs
    documents_index = load_documents_index()

    # Recursively find all PDFs in directory and subdirectories
    pdf_files = list(directory.rglob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF files")

    for pdf_path in pdf_files:
        try:
            print(f"Loading: {pdf_path.name}")
            text = load_pdf(pdf_path)
            metadata = extract_document_metadata(pdf_path, documents_index)

            documents.append({
                "content": text,
                "source": str(pdf_path),
                "filename": pdf_path.name,
                "title": metadata["title"],
                "organization": metadata["organization"],
                "organization_acronym": metadata["organization_acronym"],
                "year": metadata["year"],
                "author": metadata["author"],
                "link": metadata["link"]
            })

        except Exception as e:
            print(f"Error loading {pdf_path.name}: {e}")

    print(f"Successfully loaded {len(documents)} PDFs")
    return documents
