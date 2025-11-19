import argparse
import sys
from pathlib import Path

# Add parent directory to path to import config when running script on terminal
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama

from config import CHROMA_PATH, LLM_MODEL, TOP_K, SIMILARITY_THRESHOLD, SYSTEM_PROMPT, PROMPT_TEMPLATE
from utils.embedding_function import get_embedding_function


def build_clinical_context(clinical_data: dict) -> str:
    """Build patient clinical context from provided data."""
    if not clinical_data:
        return ""

    print(f"\n[DEBUG] Clinical data received: {clinical_data}")

    parts = []

    if clinical_data.get("age"):
        parts.append(f"Edad: {clinical_data['age']} años")
    if clinical_data.get("gender"):
        parts.append(f"Sexo: {clinical_data['gender']}")

    if clinical_data.get("weight") and clinical_data.get("height"):
        height_m = clinical_data['height'] / 100
        bmi = clinical_data['weight'] / (height_m ** 2)
        parts.append(f"IMC: {bmi:.1f}")

    if clinical_data.get("conditions"):
        parts.append(f"Condiciones: {', '.join(clinical_data['conditions'])}")
    if clinical_data.get("allergies"):
        parts.append(f"Alergias: {', '.join(clinical_data['allergies'])}")
    if clinical_data.get("medications"):
        parts.append(f"Medicamentos: {', '.join(clinical_data['medications'])}")

    if clinical_data.get("diet_type"):
        parts.append(f"Tipo de dieta: {clinical_data['diet_type']}")
    if clinical_data.get("activity_level"):
        parts.append(f"Nivel de actividad: {clinical_data['activity_level']}")

    if not parts:
        return ""

    return f"\n\nINFORMACIÓN DEL PACIENTE:\n" + "\n".join(parts) + "\n"


def _expand_diet_query(query_text: str) -> str:
    """Expand generic diet questions with additional keywords."""
    generic_keywords = ["dieta", "alimentación", "plan de comidas", "que comer", "qué comer"]

    if any(keyword in query_text.lower() for keyword in generic_keywords):
        return f"{query_text} nutrición saludable alimentos recomendados plan alimenticio"

    return query_text


def _filter_by_similarity(results: list) -> list:
    """Filter search results by similarity threshold."""
    filtered = []
    for doc, distance in results:
        similarity = 1 / (1 + distance)
        if similarity >= SIMILARITY_THRESHOLD:
            filtered.append((doc, similarity))
    return filtered


def _extract_source_info(doc, score: float) -> dict:
    """Extract source metadata from a document."""
    return {
        "title": doc.metadata.get("title", doc.metadata.get("filename", "Unknown")),
        "organization": doc.metadata.get("organization", "Organización no especificada"),
        "organization_acronym": doc.metadata.get("organization_acronym", ""),
        "year": doc.metadata.get("year"),
        "author": doc.metadata.get("author", "Autor no especificado"),
        "link": doc.metadata.get("link"),
        "similarity": f"{score*100:.1f}%"
    }


def query_rag(query_text: str, top_k: int = TOP_K, clinical_data: dict = None) -> dict:
    """
    Query the RAG system and get an answer with sources.
    """
    # Load the vector database
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function()
    )

    # Search the database
    search_query = _expand_diet_query(query_text)
    results = db.similarity_search_with_score(search_query, k=top_k)

    if not results:
        return {
            "answer": "No encontré información relevante en la base de datos.",
            "sources": []
        }

    # Filter by similarity threshold
    filtered_results = _filter_by_similarity(results)

    if not filtered_results:
        return {
            "answer": "No encontré documentos con suficiente relevancia. Intenta reformular tu pregunta.",
            "sources": []
        }

    # Build context from documents
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in filtered_results])

    clinical_context = build_clinical_context(clinical_data)
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    full_prompt = f"{SYSTEM_PROMPT}{clinical_context}\n\n{prompt}"

    model = Ollama(model=LLM_MODEL)
    response_text = model.invoke(full_prompt)


    sources = [_extract_source_info(doc, score) for doc, score in filtered_results]

    return {
        "answer": response_text,
        "sources": sources
    }


def main():
    parser = argparse.ArgumentParser(description="Query the RAG system")
    parser.add_argument("query", type=str, help="Your question")
    parser.add_argument("--top-k", type=int, default=TOP_K,
                        help="Number of documents to retrieve")
    args = parser.parse_args()

    result = query_rag(args.query, top_k=args.top_k)

    print("\n" + "=" * 80)
    print("RESPUESTA:")
    print("=" * 80)
    print(result["answer"])
    print("\n" + "=" * 80)
    print(f"FUENTES ({len(result['sources'])}):")
    print("=" * 80)
    for i, source in enumerate(result["sources"], 1):
        print(f"{i}. {source['title']}")
        print(f"   Organización: {source['organization']}")
        if source.get('year'):
            print(f"   Año: {source['year']}")
        print(f"   Autor: {source['author']}")
        if source.get('link'):
            print(f"   Link: {source['link']}")
        print(f"   Similitud: {source['similarity']}")
        print()
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
