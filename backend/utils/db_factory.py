"""Vector Database Factory - Provider selection for Chroma and Pinecone."""

import hashlib
import shutil
from pathlib import Path
from typing import List, Tuple

from langchain_core.documents import Document

from config import (
    VECTOR_DB_PROVIDER,
    CHROMA_PATH,
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    EMBEDDING_DIMENSION,
)
from utils.embedding_function import get_embedding_function


# Pinecone globals for lazy initialization
_pinecone_client = None
_pinecone_index = None


def _get_pinecone_client():
    global _pinecone_client
    if _pinecone_client is None:
        from pinecone import Pinecone
        _pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
    return _pinecone_client


def _get_pinecone_index():
    global _pinecone_index
    if _pinecone_index is None:
        from pinecone import ServerlessSpec
        pc = _get_pinecone_client()
        existing = [idx.name for idx in pc.list_indexes()]

        if PINECONE_INDEX_NAME not in existing:
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print(f"Created Pinecone index: {PINECONE_INDEX_NAME}")
        else:
            print(f"Using existing Pinecone index: {PINECONE_INDEX_NAME}")

        _pinecone_index = pc.Index(PINECONE_INDEX_NAME)
    return _pinecone_index


def _generate_chunk_id(doc: Document) -> str:
    content = f"{doc.metadata.get('filename', '')}_{doc.metadata.get('chunk_index', 0)}_{doc.page_content[:100]}"
    return hashlib.md5(content.encode()).hexdigest()


def add_documents(chunks: List[Document]) -> None:
    """Add documents to the configured vector database."""
    if VECTOR_DB_PROVIDER == "pinecone":
        _add_to_pinecone(chunks)
    else:
        _add_to_chroma(chunks)


def _add_to_chroma(chunks: List[Document]) -> None:
    from langchain_community.vectorstores import Chroma
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function()
    )
    batch_size = 5000
    total = len(chunks)
    for i in range(0, total, batch_size):
        batch = chunks[i:i + batch_size]
        db.add_documents(batch)
        print(f"Added batch {i // batch_size + 1}/{(total + batch_size - 1) // batch_size}")
    print(f"Total documents in Chroma: {db._collection.count()}")


def _add_to_pinecone(chunks: List[Document]) -> None:
    index = _get_pinecone_index()
    embedding_fn = get_embedding_function()

    batch_size = 100
    total = len(chunks)

    for i in range(0, total, batch_size):
        batch = chunks[i:i + batch_size]
        texts = [chunk.page_content for chunk in batch]
        embeddings = embedding_fn.embed_documents(texts)

        vectors = []
        for chunk, embedding in zip(batch, embeddings):
            chunk_id = _generate_chunk_id(chunk)
            metadata = {
                "text": chunk.page_content[:1000],
                "source": str(chunk.metadata.get("source", "")),
                "filename": str(chunk.metadata.get("filename", "")),
                "title": str(chunk.metadata.get("title", "")),
                "organization": str(chunk.metadata.get("organization", "")),
                "organization_acronym": str(chunk.metadata.get("organization_acronym", "")),
                "year": chunk.metadata.get("year") or 0,
                "author": str(chunk.metadata.get("author", "")),
                "link": str(chunk.metadata.get("link", "") or ""),
                "chunk_index": chunk.metadata.get("chunk_index", 0)
            }
            vectors.append((chunk_id, embedding, metadata))

        index.upsert(vectors=vectors)
        print(f"Uploaded batch {i // batch_size + 1}/{(total + batch_size - 1) // batch_size}")

    stats = index.describe_index_stats()
    print(f"Total vectors in Pinecone: {stats['total_vector_count']}")


def clear_database() -> None:
    """Clear the configured vector database."""
    if VECTOR_DB_PROVIDER == "pinecone":
        try:
            index = _get_pinecone_index()
            index.delete(delete_all=True)
            print("Pinecone index cleared")
        except Exception as e:
            print(f"Error clearing Pinecone: {e}")
    else:
        if Path(CHROMA_PATH).exists():
            shutil.rmtree(CHROMA_PATH)
            print("Chroma database cleared")


def query(query_text: str, top_k: int = 10) -> List[Tuple[Document, float]]:
    """Query the configured vector database."""
    if VECTOR_DB_PROVIDER == "pinecone":
        return _query_pinecone(query_text, top_k)
    else:
        return _query_chroma(query_text, top_k)


def _query_chroma(query_text: str, top_k: int) -> List[Tuple[Document, float]]:
    from langchain_community.vectorstores import Chroma
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function()
    )
    return db.similarity_search_with_score(query_text, k=top_k)


def _query_pinecone(query_text: str, top_k: int) -> List[Tuple[Document, float]]:
    index = _get_pinecone_index()
    embedding_fn = get_embedding_function()

    query_embedding = embedding_fn.embed_query(query_text)
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

    documents = []
    for match in results['matches']:
        doc = Document(
            page_content=match['metadata'].get('text', ''),
            metadata={
                "source": match['metadata'].get('source', ''),
                "filename": match['metadata'].get('filename', ''),
                "title": match['metadata'].get('title', ''),
                "organization": match['metadata'].get('organization', ''),
                "organization_acronym": match['metadata'].get('organization_acronym', ''),
                "year": match['metadata'].get('year'),
                "author": match['metadata'].get('author', ''),
                "link": match['metadata'].get('link', ''),
                "chunk_index": match['metadata'].get('chunk_index', 0)
            }
        )
        distance = 1 - match['score']
        documents.append((doc, distance))

    return documents
