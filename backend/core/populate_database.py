import argparse
import shutil
from pathlib import Path
import sys

# Add parent directory to path to import config when running script on terminal
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

from config import PDF_DIR, CHROMA_PATH, CHUNK_SIZE, CHUNK_OVERLAP

from utils.pdf_utils import load_pdfs_from_directory
from utils.embedding_function import get_embedding_function


def create_chunk_metadata(document: dict, chunk_index: int) -> dict:
    """Build metadata for a document chunk."""
    return {
        "source": document["source"],
        "filename": document["filename"],
        "title": document.get("title", document["filename"]),
        "organization": document.get("organization", "Organización no especificada"),
        "organization_acronym": document.get("organization_acronym", ""),
        "year": document.get("year"),
        "author": document.get("author", "Autor no especificado"),
        "link": document.get("link"),
        "chunk_index": chunk_index
    }


def chunk_documents(documents: list[dict]) -> list[Document]:
    """Split all documents into chunks."""
    # Create text splitter once for all documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )

    all_chunks = []

    for doc in documents:
        text_chunks = text_splitter.split_text(doc["content"])

        for i, chunk_text in enumerate(text_chunks):
            chunk = Document(
                page_content=chunk_text,
                metadata=create_chunk_metadata(doc, i)
            )
            all_chunks.append(chunk)

        print(f"Created {len(text_chunks)} chunks from {doc['filename']}")

    return all_chunks


def add_to_chroma(chunks: list[Document]):
    """
    Add chunks to ChromaDB in batches.
    """

    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function()
    )

    batch_size = 5000
    total = len(chunks)

    for i in range(0, total, batch_size):
        batch = chunks[i:i + batch_size]
        #print(f"Adding batch {i // batch_size + 1} ({len(batch)} chunks)")
        db.add_documents(batch)

    #print(f"Total documents in database: {db._collection.count()}")


def clear_database():
    """Clear the ChromaDB database."""
    if Path(CHROMA_PATH).exists():
        shutil.rmtree(CHROMA_PATH)
        print("Database cleared")

def main():
    parser = argparse.ArgumentParser(description="Populate ChromaDB with PDFs")
    parser.add_argument("--reset", action="store_true", help="Clear database before populating")
    args = parser.parse_args()

    if args.reset:
        clear_database()

    documents = load_pdfs_from_directory(PDF_DIR)

    if not documents:
        print("No documents found!")
        return

    chunks = chunk_documents(documents)
    print(f"Total chunks: {len(chunks)}")

    add_to_chroma(chunks)

    print("\nDone!")


if __name__ == "__main__":
    main()
