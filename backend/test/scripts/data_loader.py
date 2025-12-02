import json
from pathlib import Path
from typing import List


def load_test_cases() -> List[dict]:
    """Load test cases from dataset.json."""
    dataset_path = Path(__file__).parent.parent / "dataset.json"

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data['test_cases']


def extract_doc_ids_from_sources(sources: List[dict]) -> List[str]:
    """Extract document IDs from RAG sources using documents_index.json."""
    doc_index_path = Path(__file__).parent.parent.parent / "documents_index.json"

    if not doc_index_path.exists():
        return [source.get('title', f"doc_{i}") for i, source in enumerate(sources)]

    with open(doc_index_path, 'r', encoding='utf-8') as f:
        doc_index = json.load(f)

    # Map title to ID
    title_to_id = {}
    for org_name, org_data in doc_index.get('organizations', {}).items():
        for doc in org_data.get('documents', []):
            title = doc.get('title', '')
            doc_id = doc.get('id', '')
            if title and doc_id:
                title_to_id[title.lower()] = doc_id

    # Match sources to IDs
    doc_ids = []
    for source in sources:
        title = source.get('title', '').lower()
        doc_id = title_to_id.get(title)

        # Partial match if exact not found
        if not doc_id:
            for t, did in title_to_id.items():
                if title in t or t in title:
                    doc_id = did
                    break

        if doc_id:
            doc_ids.append(doc_id)
        else:
            doc_ids.append(source.get('title', f"unknown_{len(doc_ids)}"))

    return doc_ids
