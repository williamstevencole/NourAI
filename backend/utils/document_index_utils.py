import json
from pathlib import Path
from typing import Optional

def load_documents_index(index_path: str = "documents_index.json") -> dict:
    """
    Load the documents index JSON file.
    """
    full_path = Path(__file__).parent.parent / index_path

    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_document_by_path(location_in_pc: str, documents_index: Optional[dict] = None) -> Optional[dict]:
    """
    Find a document in the index by its location_in_pc path.
    """
    if documents_index is None:
        documents_index = load_documents_index()

    search_path = location_in_pc.replace("data/pdfs/", "data/").replace("\\", "/")

    for org_key, org_data in documents_index.get("organizations", {}).items():
        for doc in org_data.get("documents", []):
            doc_path = doc.get("location_in_pc", "").replace("\\", "/")

            if doc_path == search_path or doc_path.endswith(search_path.split("/")[-1]):
                return {
                    "id": doc.get("id"),
                    "title": doc.get("title"),
                    "year": doc.get("year"),
                    "organization": org_data.get("full_name"),
                    "organization_acronym": org_data.get("acronym"),
                    "link": doc.get("link"),
                    "author": doc.get("author"),
                    "format": doc.get("format"),
                    "pages": doc.get("pages"),
                    "location_in_pc": doc.get("location_in_pc")
                }

    return None


def get_citation_info(location_in_pc: str) -> dict:
    """
    Get formatted citation information for a document.
    """
    doc_info = find_document_by_path(location_in_pc)

    if doc_info:
        return {
            "title": doc_info["title"],
            "organization": doc_info["organization"],
            "organization_acronym": doc_info["organization_acronym"],
            "year": doc_info["year"],
            "author": doc_info["author"],
            "link": doc_info["link"]
        }
    else:
        filename = Path(location_in_pc).name
        return {
            "title": filename,
            "organization": "Organización no especificada",
            "organization_acronym": "N/A",
            "year": None,
            "author": "Autor no especificado",
            "link": None
        }
