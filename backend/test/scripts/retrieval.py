import sys
from pathlib import Path
from typing import List
from langchain_community.vectorstores import Chroma

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import CHROMA_PATH
from utils.embedding_function import get_embedding_function


def get_retrieved_contexts(query: str, top_k: int) -> List[str]:
    """Get contexts (documents) retrieved by the RAG system."""
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function()
    )

    results = db.similarity_search_with_score(query, k=top_k)

    if not results:
        return []

    contexts = [doc.page_content for doc, _ in results]
    return contexts
