#!/usr/bin/env python3
"""Script para buscar información específica en ChromaDB"""
import sys
sys.path.append('/Users/williamstevencolepaz/Dev/nutri-rag/backend')

from langchain_community.vectorstores import Chroma
from config import CHROMA_PATH
from utils.embedding_function import get_embedding_function

# Initialize
embedding_function = get_embedding_function()
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

# Queries para encontrar documentos relevantes de tests 1,2,3 y nuevas preguntas
queries = {
    # Test 1 - más docs sobre diabetes
    "diabetes_2030": "diabetes 32.9 millones 2030 América Latina prevalencia",
    "diabetes_alimentos": "diabetes alimentos evitar azúcar carbohidratos glucémico",

    # Test 2 - más docs sobre medicamentos presión arterial
    "medicamentos_presion": "anticonceptivos AINEs corticosteroides presión arterial medicamentos",
    "sodio_hipertension": "sodio sal 5 gramos 2 gramos hipertensión",

    # Test 3 - más docs sobre prevención obesidad
    "prevencion_obesidad": "lactancia materna exclusiva azúcares televisión obesidad prevención",

    # Nuevas preguntas con datos específicos
    "hierro_gestantes": "hierro embarazadas 30 mg suplementación gestación",
    "actividad_fisica": "150 minutos actividad física semana moderada",
    "imc_clasificacion": "IMC 25 30 sobrepeso obesidad clasificación",
    "azucar_libre": "azúcar libre 10% energía OMS recomendación",
    "frutas_verduras_5": "5 porciones frutas verduras día 400 gramos",
    "agua_litros": "agua litros día hidratación 2 litros"
}

print("="*80)
print("BUSCANDO INFORMACIÓN ESPECÍFICA EN PDFS")
print("="*80)

for topic, query in queries.items():
    print(f"\n\n{'='*80}")
    print(f"TEMA: {topic}")
    print(f"QUERY: {query}")
    print(f"{'='*80}")

    results = db.similarity_search_with_score(query, k=5)

    for i, (doc, score) in enumerate(results, 1):
        source_path = doc.metadata.get('source', 'unknown')

        # Extract document identifier (folder/filename)
        if '/pdfs/' in source_path:
            parts = source_path.split('/pdfs/')[-1]
            if '/' in parts:
                folder = parts.split('/')[0]
                filename = parts.split('/')[-1].replace('.pdf', '')
                doc_id = f"{folder}/{filename}"
            else:
                doc_id = parts.replace('.pdf', '')
        else:
            doc_id = source_path

        print(f"\n[{i}] Score: {score:.3f}")
        print(f"    Doc ID: {doc_id}")
        print(f"    Content (primeros 500 chars):")
        content = doc.page_content.replace('\n', ' ').replace('  ', ' ')
        print(f"    {content[:500]}")
        print()
