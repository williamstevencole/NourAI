#!/usr/bin/env python3
"""
Script de Evaluación del Sistema RAG usando RAGAS

RAGAS (RAG Assessment) es el framework estándar de la industria para evaluar sistemas RAG.

Métricas implementadas:
1. RETRIEVAL:
   - Context Precision: ¿Los contextos relevantes están en top positions?
   - Context Recall: ¿Se recuperaron todos los contextos necesarios?

2. GENERATION:
   - Faithfulness: ¿La respuesta está basada en el contexto sin inventar?
   - Answer Relevancy: ¿La respuesta es relevante a la pregunta?
   - Answer Correctness: Precisión factual comparada con ground truth

3. SISTEMA:
   - Latency: Tiempo de respuesta
   - Coverage: % de consultas exitosas

Uso:
    python evaluate_ragas.py
    python evaluate_ragas.py --verbose
"""

import json
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.query_data import query_rag
from langchain_community.vectorstores import Chroma
from config import CHROMA_PATH, TOP_K
from utils.embedding_function import get_embedding_function

# RAGAS imports
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
    answer_correctness,
)

# Librerías para BLEU y ROUGE
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

# RAGAS con OpenAI imports
import os
from openai import OpenAI
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


def calculate_bleu(generated: str, reference: str) -> dict:
    """
    Calcula BLEU score usando NLTK.

    Returns:
        Dict con BLEU-1, BLEU-2, BLEU-3, BLEU-4 y promedio
    """
    # Tokenizar
    gen_tokens = generated.lower().split()
    ref_tokens = [reference.lower().split()]  # NLTK espera lista de referencias

    # Smoothing function para evitar 0s
    smoothing = SmoothingFunction().method1

    # Calcular BLEU para diferentes n-gramas
    bleu_1 = sentence_bleu(ref_tokens, gen_tokens, weights=(1, 0, 0, 0), smoothing_function=smoothing)
    bleu_2 = sentence_bleu(ref_tokens, gen_tokens, weights=(0.5, 0.5, 0, 0), smoothing_function=smoothing)
    bleu_3 = sentence_bleu(ref_tokens, gen_tokens, weights=(0.33, 0.33, 0.33, 0), smoothing_function=smoothing)
    bleu_4 = sentence_bleu(ref_tokens, gen_tokens, weights=(0.25, 0.25, 0.25, 0.25), smoothing_function=smoothing)

    bleu_avg = (bleu_1 + bleu_2 + bleu_3 + bleu_4) / 4

    return {
        'bleu_1': bleu_1,
        'bleu_2': bleu_2,
        'bleu_3': bleu_3,
        'bleu_4': bleu_4,
        'bleu_avg': bleu_avg
    }


def calculate_rouge(generated: str, reference: str) -> dict:
    """
    Calcula ROUGE scores usando rouge-score.

    Returns:
        Dict con ROUGE-1, ROUGE-2, ROUGE-L (precision, recall, f1)
    """
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference, generated)

    return {
        'rouge_1_precision': scores['rouge1'].precision,
        'rouge_1_recall': scores['rouge1'].recall,
        'rouge_1_f1': scores['rouge1'].fmeasure,
        'rouge_2_precision': scores['rouge2'].precision,
        'rouge_2_recall': scores['rouge2'].recall,
        'rouge_2_f1': scores['rouge2'].fmeasure,
        'rouge_l_precision': scores['rougeL'].precision,
        'rouge_l_recall': scores['rougeL'].recall,
        'rouge_l_f1': scores['rougeL'].fmeasure,
    }


def configure_ragas_with_openai():
    """
    Configura RAGAS para usar OpenAI con la nueva API.

    Requiere variable de entorno OPENAI_API_KEY configurada.
    """

    print("\n🔧 Configurando RAGAS para usar OpenAI...")

    # Verificar que existe la API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError(
            "❌ OPENAI_API_KEY no encontrada.\n"
            "Por favor configura la variable de entorno:\n"
            "export OPENAI_API_KEY='tu-api-key-aqui'"
        )

    print("   ✅ OpenAI API Key encontrada")
    print("   📊 RAGAS usará modelos de OpenAI para evaluación")
    print("   💰 Costo estimado: $0.10-0.30 USD para 5 casos\n")

    # Configurar LLM de OpenAI
    openai_llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=api_key,
        temperature=0
    )

    # Configurar embeddings de OpenAI
    openai_embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_key
    )

    # Wrap para RAGAS (aunque deprecated, es necesario para compatibilidad)
    ragas_llm = LangchainLLMWrapper(openai_llm)
    ragas_embeddings = LangchainEmbeddingsWrapper(openai_embeddings)

    return ragas_llm, ragas_embeddings


def load_test_cases() -> List[dict]:
    """Carga los casos de prueba del dataset."""
    dataset_path = Path(__file__).parent / "dataset.json"

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset no encontrado: {dataset_path}")

    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data['test_cases']


def get_retrieved_contexts(query: str, top_k: int = TOP_K) -> List[str]:
    """
    Obtiene los contextos (documentos) recuperados por el RAG.

    Returns:
        Lista de strings, cada uno es el contenido de un documento recuperado
    """
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function()
    )

    results = db.similarity_search_with_score(query, k=top_k)

    if not results:
        return []

    # RAGAS espera una lista de strings (cada doc es un string)
    contexts = [doc.page_content for doc, _ in results]
    return contexts


def extract_doc_ids_from_sources(sources: List[dict]) -> List[str]:
    """
    Extrae IDs de documentos de las fuentes retornadas por el RAG.
    """
    doc_index_path = Path(__file__).parent.parent / "documents_index.json"

    if not doc_index_path.exists():
        return [source.get('title', f"doc_{i}") for i, source in enumerate(sources)]

    with open(doc_index_path, 'r', encoding='utf-8') as f:
        doc_index = json.load(f)

    # Crear mapeo de título a ID
    title_to_id = {}
    for org_name, org_data in doc_index.get('organizations', {}).items():
        for doc in org_data.get('documents', []):
            title = doc.get('title', '')
            doc_id = doc.get('id', '')
            if title and doc_id:
                title_to_id[title.lower()] = doc_id

    # Mapear fuentes a IDs
    doc_ids = []
    for source in sources:
        title = source.get('title', '').lower()
        doc_id = title_to_id.get(title)

        if not doc_id:
            # Buscar coincidencia parcial
            for t, did in title_to_id.items():
                if title in t or t in title:
                    doc_id = did
                    break

        if doc_id:
            doc_ids.append(doc_id)
        else:
            doc_ids.append(source.get('title', f"unknown_{len(doc_ids)}"))

    return doc_ids


def calculate_manual_precision_recall(retrieved_docs: List[str], relevant_docs: List[str]) -> dict:
    """
    Calcula Precision y Recall manualmente (RAGAS no las tiene directamente).
    """
    retrieved_set = set(retrieved_docs)
    relevant_set = set(relevant_docs)

    if len(retrieved_set) == 0:
        precision = 0.0
    else:
        precision = len(retrieved_set & relevant_set) / len(retrieved_set)

    if len(relevant_set) == 0:
        recall = 0.0
    else:
        recall = len(retrieved_set & relevant_set) / len(relevant_set)

    return {
        'precision': precision,
        'recall': recall
    }


def run_evaluation(test_cases: List[dict], verbose: bool = False) -> dict:
    """
    Ejecuta la evaluación completa usando RAGAS.

    Returns:
        Diccionario con resultados agregados y detallados
    """
    # Configurar RAGAS con OpenAI
    ragas_llm, ragas_embeddings = configure_ragas_with_openai()

    # Preparar datos para RAGAS
    questions = []
    answers = []
    contexts_list = []
    ground_truths = []

    # Métricas adicionales
    latencies = []
    retrieved_docs_list = []
    relevant_docs_list = []
    test_ids = []
    categories = []
    difficulties = []
    bleu_scores_list = []
    rouge_scores_list = []
    success_count = 0

    print("\n" + "="*80)
    print("EJECUTANDO EVALUACIÓN CON RAGAS + OPENAI")
    print("="*80)

    for i, test_case in enumerate(test_cases, 1):
        test_id = test_case['id']
        query = test_case['query']
        expected_answer = test_case['expected_answer']
        relevant_docs = test_case['relevant_docs']
        clinical_data = test_case.get('clinical_data')

        print(f"\n[{i}/{len(test_cases)}] Evaluando: {test_id}")
        if verbose:
            print(f"   Pregunta: {query[:80]}...")

        # Medir latency
        start_time = time.time()

        try:
            # Ejecutar RAG
            result = query_rag(
                query_text=query,
                top_k=TOP_K,
                clinical_data=clinical_data
            )

            generated_answer = result['answer']
            sources = result['sources']

            # Obtener contextos recuperados
            contexts = get_retrieved_contexts(query, TOP_K)

            # Extraer IDs de documentos
            retrieved_docs = extract_doc_ids_from_sources(sources)

            # Calcular latency
            latency = time.time() - start_time

            # Calcular BLEU y ROUGE
            bleu_scores = calculate_bleu(generated_answer, expected_answer)
            rouge_scores = calculate_rouge(generated_answer, expected_answer)

            # Agregar a listas para RAGAS
            questions.append(query)
            answers.append(generated_answer)
            contexts_list.append(contexts)
            ground_truths.append(expected_answer)

            # Métricas adicionales
            latencies.append(latency)
            retrieved_docs_list.append(retrieved_docs)
            relevant_docs_list.append(relevant_docs)
            test_ids.append(test_id)
            categories.append(test_case.get('category', 'unknown'))
            difficulties.append(test_case.get('difficulty', 'medium'))
            bleu_scores_list.append(bleu_scores)
            rouge_scores_list.append(rouge_scores)

            success_count += 1

            print(f"   ✅ Completado en {latency:.2f}s")

            if verbose:
                print(f"   Respuesta: {generated_answer[:100]}...")
                print(f"   Docs recuperados: {len(retrieved_docs)}")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            continue

    # Calcular coverage
    total_cases = len(test_cases)
    coverage = (success_count / total_cases) * 100 if total_cases > 0 else 0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    print(f"\n{'='*80}")
    print(f"Casos exitosos: {success_count}/{total_cases} ({coverage:.1f}%)")
    print(f"Latency promedio: {avg_latency:.2f}s")
    print(f"{'='*80}\n")

    # Crear dataset para RAGAS
    print("📊 Calculando métricas RAGAS con OpenAI...")
    print("   (Esto puede tardar 2-5 minutos)\n")

    ragas_dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts_list,
        "ground_truth": ground_truths,
    })

    # Evaluar con RAGAS usando OpenAI
    ragas_results = evaluate(
        ragas_dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_recall,
            context_precision,
            answer_correctness,
        ],
        llm=ragas_llm,
        embeddings=ragas_embeddings,
    )

    print("\n✅ Evaluación RAGAS completada!")

    # Calcular Precision y Recall manuales
    precision_recall_list = []
    for retrieved, relevant in zip(retrieved_docs_list, relevant_docs_list):
        pr = calculate_manual_precision_recall(retrieved, relevant)
        precision_recall_list.append(pr)

    avg_precision = sum(pr['precision'] for pr in precision_recall_list) / len(precision_recall_list) if precision_recall_list else 0
    avg_recall = sum(pr['recall'] for pr in precision_recall_list) / len(precision_recall_list) if precision_recall_list else 0

    # Calcular promedios de BLEU
    avg_bleu = {}
    if bleu_scores_list:
        bleu_keys = bleu_scores_list[0].keys()
        for key in bleu_keys:
            avg_bleu[key] = sum(scores[key] for scores in bleu_scores_list) / len(bleu_scores_list)

    # Calcular promedios de ROUGE
    avg_rouge = {}
    if rouge_scores_list:
        rouge_keys = rouge_scores_list[0].keys()
        for key in rouge_keys:
            avg_rouge[key] = sum(scores[key] for scores in rouge_scores_list) / len(rouge_scores_list)

    # Procesar resultados de RAGAS
    # Convertir EvaluationResult a diccionario
    ragas_dict = ragas_results.to_pandas().to_dict('list')

    def safe_mean(values):
        """Calcula el promedio de una lista de valores, manejando NaN y errores"""
        if isinstance(values, (int, float)):
            return float(values)
        if isinstance(values, list):
            valid_values = [v for v in values if v is not None and str(v).lower() != 'nan']
            return sum(valid_values) / len(valid_values) if valid_values else 0.0
        return 0.0

    # Compilar resultados
    results = {
        'metadata': {
            'evaluation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_test_cases': total_cases,
            'successful_cases': success_count,
            'failed_cases': total_cases - success_count,
            'coverage_percentage': round(coverage, 2),
            'average_latency_seconds': round(avg_latency, 3),
        },
        'ragas_metrics': {
            'faithfulness': safe_mean(ragas_dict.get('faithfulness', [0])),
            'answer_relevancy': safe_mean(ragas_dict.get('answer_relevancy', [0])),
            'context_recall': safe_mean(ragas_dict.get('context_recall', [0])),
            'context_precision': safe_mean(ragas_dict.get('context_precision', [0])),
            'answer_correctness': safe_mean(ragas_dict.get('answer_correctness', [0])),
        },
        'additional_metrics': {
            'precision': round(avg_precision, 3),
            'recall': round(avg_recall, 3),
            'bleu': {k: round(v, 3) for k, v in avg_bleu.items()} if avg_bleu else {},
            'rouge': {k: round(v, 3) for k, v in avg_rouge.items()} if avg_rouge else {},
        },
        'detailed_results': []
    }

    # Agregar resultados detallados por caso
    for i in range(len(questions)):
        results['detailed_results'].append({
            'test_id': test_ids[i],
            'category': categories[i],
            'difficulty': difficulties[i],
            'question': questions[i],
            'answer': answers[i],
            'ground_truth': ground_truths[i],
            'latency_seconds': latencies[i],
            'retrieved_docs': retrieved_docs_list[i],
            'relevant_docs': relevant_docs_list[i],
            'precision': precision_recall_list[i]['precision'],
            'recall': precision_recall_list[i]['recall'],
        })

    return results


def print_summary_report(results: dict):
    """Imprime reporte resumido de la evaluación."""
    print("\n" + "="*80)
    print("REPORTE FINAL DE EVALUACIÓN - NUTRI-RAG MVP (RAGAS)")
    print("="*80)

    metadata = results['metadata']
    ragas = results['ragas_metrics']
    additional = results['additional_metrics']

    print(f"\n📋 RESUMEN GENERAL:")
    print(f"   Total de casos: {metadata['total_test_cases']}")
    print(f"   Casos exitosos: {metadata['successful_cases']}")
    print(f"   Coverage: {metadata['coverage_percentage']}%")
    print(f"   Latency promedio: {metadata['average_latency_seconds']}s")

    print(f"\n📊 MÉTRICAS RAGAS (Escala 0-1):")
    print(f"   Faithfulness (Fidelidad): {ragas['faithfulness']:.3f}")
    print(f"     └─ ¿La respuesta se basa en el contexto sin inventar?")
    print(f"   Answer Relevancy (Relevancia): {ragas['answer_relevancy']:.3f}")
    print(f"     └─ ¿La respuesta es relevante a la pregunta?")
    print(f"   Context Recall (Recall de Contexto): {ragas['context_recall']:.3f}")
    print(f"     └─ ¿Se recuperaron todos los contextos necesarios?")
    print(f"   Context Precision (Precisión de Contexto): {ragas['context_precision']:.3f}")
    print(f"     └─ ¿Los contextos relevantes están en top positions?")
    print(f"   Answer Correctness (Precisión de Respuesta): {ragas['answer_correctness']:.3f}")
    print(f"     └─ ¿La respuesta es factualmente correcta?")

    print(f"\n📈 MÉTRICAS DE RECUPERACIÓN:")
    print(f"   Precision@{TOP_K}: {additional['precision']:.3f} ({additional['precision']*100:.1f}%)")
    print(f"   Recall@{TOP_K}: {additional['recall']:.3f} ({additional['recall']*100:.1f}%)")

    # BLEU scores
    bleu = additional.get('bleu', {})
    if bleu:
        print(f"\n📝 MÉTRICAS BLEU (Precisión de N-gramas):")
        print(f"   BLEU-1: {bleu.get('bleu_1', 0):.3f}")
        print(f"   BLEU-2: {bleu.get('bleu_2', 0):.3f}")
        print(f"   BLEU-3: {bleu.get('bleu_3', 0):.3f}")
        print(f"   BLEU-4: {bleu.get('bleu_4', 0):.3f}")
        print(f"   BLEU Promedio: {bleu.get('bleu_avg', 0):.3f} ({bleu.get('bleu_avg', 0)*100:.1f}%)")

    # ROUGE scores
    rouge = additional.get('rouge', {})
    if rouge:
        print(f"\n📊 MÉTRICAS ROUGE (Similitud de Texto):")
        print(f"   ROUGE-1 F1: {rouge.get('rouge_1_f1', 0):.3f} ({rouge.get('rouge_1_f1', 0)*100:.1f}%)")
        print(f"   ROUGE-2 F1: {rouge.get('rouge_2_f1', 0):.3f} ({rouge.get('rouge_2_f1', 0)*100:.1f}%)")
        print(f"   ROUGE-L F1: {rouge.get('rouge_l_f1', 0):.3f} ({rouge.get('rouge_l_f1', 0)*100:.1f}%)")

    # Calcular promedio general
    avg_score = sum(ragas.values()) / len(ragas)
    print(f"\n⭐ PUNTAJE PROMEDIO RAGAS: {avg_score:.3f} ({avg_score*100:.1f}%)")

    # Interpretación
    print(f"\n💡 INTERPRETACIÓN:")
    if avg_score >= 0.7:
        print("   ✅ EXCELENTE - El sistema muestra un rendimiento muy sólido")
    elif avg_score >= 0.5:
        print("   ⚠️  BUENO - El sistema funciona bien pero tiene margen de mejora")
    else:
        print("   ❌ NECESITA MEJORA - Considerar optimizaciones significativas")

    print("\n" + "="*80)


def generate_readme(results: dict):
    """Genera README detallado con análisis completo."""
    readme_path = Path(__file__).parent / "EVALUATION_RESULTS.md"

    metadata = results['metadata']
    ragas = results['ragas_metrics']
    additional = results['additional_metrics']
    detailed = results['detailed_results']

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("# Evaluación del Sistema RAG - Nutri-RAG MVP\n\n")
        f.write(f"**Fecha:** {metadata['evaluation_date']}\n\n")
        f.write(f"**Framework:** RAGAS (RAG Assessment)\n\n")

        f.write("---\n\n")

        # Resumen ejecutivo
        f.write("## 📊 Resumen Ejecutivo\n\n")
        f.write(f"- **Total de casos:** {metadata['total_test_cases']}\n")
        f.write(f"- **Coverage:** {metadata['coverage_percentage']}%\n")
        f.write(f"- **Latency promedio:** {metadata['average_latency_seconds']}s\n")

        avg_score = sum(ragas.values()) / len(ragas)
        f.write(f"- **Puntaje RAGAS:** {avg_score:.3f}/1.0 ({avg_score*100:.1f}%)\n\n")

        # Interpretación general
        if avg_score >= 0.7:
            f.write("**Estado:** ✅ **EXCELENTE** - Sistema listo para uso educativo\n\n")
        elif avg_score >= 0.5:
            f.write("**Estado:** ⚠️ **BUENO** - Requiere optimizaciones menores\n\n")
        else:
            f.write("**Estado:** ❌ **NECESITA MEJORA** - Optimizaciones significativas requeridas\n\n")

        f.write("---\n\n")

        # Métricas RAGAS
        f.write("## 1. Métricas RAGAS\n\n")
        f.write("RAGAS (RAG Assessment) es el framework estándar de la industria para evaluar sistemas RAG.\n\n")

        f.write("### 1.1 Faithfulness (Fidelidad al Contexto)\n\n")
        f.write(f"**Puntaje:** {ragas['faithfulness']:.3f}\n\n")
        f.write("**Qué evalúa:** ¿La respuesta está basada únicamente en el contexto recuperado sin inventar información?\n\n")
        if ragas['faithfulness'] >= 0.7:
            f.write("✅ **Excelente** - El sistema no alucina, se basa fielmente en los documentos.\n\n")
        elif ragas['faithfulness'] >= 0.5:
            f.write("⚠️ **Aceptable** - Ocasionalmente agrega información externa.\n\n")
        else:
            f.write("❌ **Crítico** - El sistema frecuentemente inventa información.\n\n")

        f.write("### 1.2 Answer Relevancy (Relevancia de Respuesta)\n\n")
        f.write(f"**Puntaje:** {ragas['answer_relevancy']:.3f}\n\n")
        f.write("**Qué evalúa:** ¿La respuesta es directamente relevante a la pregunta realizada?\n\n")
        if ragas['answer_relevancy'] >= 0.7:
            f.write("✅ **Excelente** - Las respuestas son altamente relevantes.\n\n")
        elif ragas['answer_relevancy'] >= 0.5:
            f.write("⚠️ **Aceptable** - Las respuestas a veces se desvían del tema.\n\n")
        else:
            f.write("❌ **Pobre** - Las respuestas frecuentemente no responden la pregunta.\n\n")

        f.write("### 1.3 Context Recall (Recall de Contexto)\n\n")
        f.write(f"**Puntaje:** {ragas['context_recall']:.3f}\n\n")
        f.write("**Qué evalúa:** ¿El sistema recuperó todos los contextos necesarios para responder?\n\n")
        if ragas['context_recall'] >= 0.7:
            f.write("✅ **Excelente** - Recupera la mayoría de contextos relevantes.\n\n")
        elif ragas['context_recall'] >= 0.5:
            f.write("⚠️ **Aceptable** - A veces falta información importante.\n\n")
        else:
            f.write("❌ **Pobre** - Frecuentemente omite contextos relevantes.\n\n")

        f.write("### 1.4 Context Precision (Precisión de Contexto)\n\n")
        f.write(f"**Puntaje:** {ragas['context_precision']:.3f}\n\n")
        f.write("**Qué evalúa:** ¿Los contextos más relevantes aparecen en las primeras posiciones?\n\n")
        if ragas['context_precision'] >= 0.7:
            f.write("✅ **Excelente** - El ranking de documentos es muy efectivo.\n\n")
        elif ragas['context_precision'] >= 0.5:
            f.write("⚠️ **Aceptable** - El ranking podría mejorarse.\n\n")
        else:
            f.write("❌ **Pobre** - Documentos importantes aparecen en posiciones bajas.\n\n")

        f.write("### 1.5 Answer Correctness (Precisión de Respuesta)\n\n")
        f.write(f"**Puntaje:** {ragas['answer_correctness']:.3f}\n\n")
        f.write("**Qué evalúa:** ¿La respuesta es factualmente correcta comparada con el ground truth?\n\n")
        if ragas['answer_correctness'] >= 0.7:
            f.write("✅ **Excelente** - Las respuestas son muy precisas.\n\n")
        elif ragas['answer_correctness'] >= 0.5:
            f.write("⚠️ **Aceptable** - Hay precisión razonable con errores menores.\n\n")
        else:
            f.write("❌ **Pobre** - Las respuestas contienen errores significativos.\n\n")

        f.write("---\n\n")

        # Métricas adicionales
        f.write("## 2. Métricas Adicionales\n\n")
        f.write(f"### Precision@{TOP_K}: {additional['precision']:.3f}\n")
        f.write(f"Proporción de documentos recuperados que son relevantes.\n\n")
        f.write(f"### Recall@{TOP_K}: {additional['recall']:.3f}\n")
        f.write(f"Proporción de documentos relevantes que fueron recuperados.\n\n")

        f.write("---\n\n")

        # Métricas de sistema
        f.write("## 3. Métricas de Sistema\n\n")
        f.write(f"### Coverage: {metadata['coverage_percentage']}%\n")
        f.write(f"Porcentaje de consultas respondidas exitosamente.\n\n")
        f.write(f"### Latency Promedio: {metadata['average_latency_seconds']}s\n")
        if metadata['average_latency_seconds'] < 5:
            f.write("✅ Tiempo de respuesta excelente.\n\n")
        elif metadata['average_latency_seconds'] < 10:
            f.write("⚠️ Tiempo de respuesta aceptable.\n\n")
        else:
            f.write("❌ Tiempo de respuesta lento, considerar optimizaciones.\n\n")

        f.write("---\n\n")

        # Fortalezas
        f.write("## 4. Fortalezas del Sistema\n\n")
        strengths = []

        if ragas['faithfulness'] >= 0.7:
            strengths.append("✅ **Alta fidelidad:** El sistema no inventa información, se basa en fuentes confiables.")
        if ragas['answer_relevancy'] >= 0.7:
            strengths.append("✅ **Respuestas relevantes:** Las respuestas están directamente relacionadas con las preguntas.")
        if ragas['context_precision'] >= 0.6:
            strengths.append("✅ **Buen ranking:** Los documentos más relevantes aparecen primero.")
        if metadata['coverage_percentage'] == 100:
            strengths.append("✅ **Cobertura completa:** Responde todas las consultas sin errores.")
        if metadata['average_latency_seconds'] < 10:
            strengths.append("✅ **Rendimiento adecuado:** Tiempos de respuesta aceptables.")

        if strengths:
            for s in strengths:
                f.write(f"{s}\n\n")
        else:
            f.write("El sistema requiere optimizaciones generales.\n\n")

        f.write("---\n\n")

        # Limitaciones
        f.write("## 5. Limitaciones y Áreas de Mejora\n\n")
        limitations = []

        if ragas['faithfulness'] < 0.7:
            limitations.append("⚠️ **Fidelidad baja:** El sistema ocasionalmente inventa información. Revisar prompts y contextos.")
        if ragas['context_recall'] < 0.7:
            limitations.append("⚠️ **Recall limitado:** No siempre recupera todos los documentos relevantes. Aumentar k o mejorar embeddings.")
        if ragas['answer_correctness'] < 0.7:
            limitations.append("⚠️ **Precisión factual:** Las respuestas contienen errores. Mejorar calidad de documentos fuente.")
        if additional['precision'] < 0.6:
            limitations.append("⚠️ **Precisión de recuperación:** Muchos documentos irrelevantes. Optimizar similarity threshold.")
        if metadata['average_latency_seconds'] > 10:
            limitations.append("⚠️ **Latencia alta:** Considerar modelo LLM más rápido o caching.")

        if limitations:
            for l in limitations:
                f.write(f"{l}\n\n")
        else:
            f.write("No se identificaron limitaciones críticas.\n\n")

        f.write("---\n\n")

        # Resultados detallados
        f.write("## 6. Resultados Detallados por Caso\n\n")
        for i, detail in enumerate(detailed, 1):
            f.write(f"### Caso {i}: {detail['test_id']}\n\n")
            f.write(f"**Categoría:** {detail['category']}\n\n")
            f.write(f"**Pregunta:** {detail['question']}\n\n")
            f.write(f"**Métricas:**\n")
            f.write(f"- Precision: {detail['precision']:.3f}\n")
            f.write(f"- Recall: {detail['recall']:.3f}\n")
            f.write(f"- Latency: {detail['latency_seconds']:.2f}s\n\n")
            f.write("---\n\n")

        # Conclusiones
        f.write("## 7. Conclusiones y Recomendaciones\n\n")

        if avg_score >= 0.7:
            f.write("### Conclusión General\n\n")
            f.write("El sistema Nutri-RAG MVP demuestra un **rendimiento excelente** y está listo para uso en contextos educativos. ")
            f.write("Las métricas RAGAS indican alta fidelidad, relevancia y precisión en las respuestas generadas.\n\n")
        elif avg_score >= 0.5:
            f.write("### Conclusión General\n\n")
            f.write("El sistema Nutri-RAG MVP muestra un **rendimiento aceptable** con margen de mejora. ")
            f.write("Es funcional pero requiere optimizaciones antes de uso en producción.\n\n")
        else:
            f.write("### Conclusión General\n\n")
            f.write("El sistema Nutri-RAG MVP **requiere mejoras significativas**. ")
            f.write("Se recomienda revisar la configuración, documentos fuente y prompts del sistema.\n\n")

        f.write("### Recomendaciones\n\n")
        f.write("1. **Mejorar embeddings:** Experimentar con modelos más avanzados para mejor recuperación.\n")
        f.write("2. **Optimizar prompts:** Refinar el system prompt para mayor precisión y completitud.\n")
        f.write("3. **Ampliar dataset:** Agregar más casos de prueba, especialmente edge cases.\n")
        f.write("4. **Fine-tuning:** Considerar fine-tuning del LLM con datos de nutrición.\n")
        f.write("5. **Validación experta:** Complementar con revisión de nutricionistas profesionales.\n\n")

        f.write("---\n\n")
        f.write(f"*Reporte generado automáticamente usando RAGAS v{metadata['evaluation_date']}*\n")

    print(f"\n📄 README generado: {readme_path}")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Evalúa el sistema RAG usando RAGAS")
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verbose')
    args = parser.parse_args()

    try:
        # Cargar casos de prueba
        test_cases = load_test_cases()
        print(f"\n✅ {len(test_cases)} casos de prueba cargados")

        # Ejecutar evaluación
        results = run_evaluation(test_cases, verbose=args.verbose)

        # Guardar resultados JSON
        results_path = Path(__file__).parent / "results_ragas.json"
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultados guardados: {results_path}")

        # Imprimir reporte
        print_summary_report(results)

        # Generar README
        generate_readme(results)

        print("\n✅ Evaluación completada exitosamente!\n")

    except Exception as e:
        print(f"\n❌ Error durante la evaluación: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
