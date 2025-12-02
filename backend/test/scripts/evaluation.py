import sys
import time
from pathlib import Path
from typing import List
from datetime import datetime
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
    answer_correctness,
)

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.query_data import query_rag
from config import TOP_K
from ragas_config import configure_ragas_with_openai
from retrieval import get_retrieved_contexts
from data_loader import extract_doc_ids_from_sources
from metrics import calculate_bleu, calculate_rouge, calculate_manual_precision_recall


def run_evaluation(test_cases: List[dict], verbose: bool = False) -> dict:
    """Execute complete evaluation using RAGAS."""
    # RAGAS configuration
    ragas_llm, ragas_embeddings = configure_ragas_with_openai()

    # Data collection
    questions = []
    answers = []
    contexts_list = []
    ground_truths = []
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
    print("RAGAS EVALUATION")
    print("="*80)

    for i, test_case in enumerate(test_cases, 1):
        test_id = test_case['id']
        query = test_case['query']
        expected_answer = test_case['expected_answer']
        relevant_docs = test_case['relevant_docs']
        clinical_data = test_case.get('clinical_data')

        print(f"\n[{i}/{len(test_cases)}] {test_id}")
        if verbose:
            print(f"   Query: {query[:80]}...")

        start_time = time.time()

        try:
            # RAG execution
            result = query_rag(
                query_text=query,
                top_k=TOP_K,
                clinical_data=clinical_data
            )

            generated_answer = result['answer']
            sources = result['sources']
            contexts = get_retrieved_contexts(query, TOP_K)
            retrieved_docs = extract_doc_ids_from_sources(sources)
            latency = time.time() - start_time

            # Manual metrics
            bleu_scores = calculate_bleu(generated_answer, expected_answer)
            rouge_scores = calculate_rouge(generated_answer, expected_answer)

            # Store data for RAGAS
            questions.append(query)
            answers.append(generated_answer)
            contexts_list.append(contexts)
            ground_truths.append(expected_answer)
            latencies.append(latency)
            retrieved_docs_list.append(retrieved_docs)
            relevant_docs_list.append(relevant_docs)
            test_ids.append(test_id)
            categories.append(test_case.get('category', 'unknown'))
            difficulties.append(test_case.get('difficulty', 'medium'))
            bleu_scores_list.append(bleu_scores)
            rouge_scores_list.append(rouge_scores)
            success_count += 1

            print(f"   Completed in {latency:.2f}s")

            if verbose:
                print(f"   Answer: {generated_answer[:100]}...")
                print(f"   Retrieved docs: {len(retrieved_docs)}")

        except Exception as e:
            print(f"   Error: {str(e)}")
            continue

    # Coverage and latency
    total_cases = len(test_cases)
    coverage = (success_count / total_cases) * 100 if total_cases > 0 else 0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    print(f"\n{'='*80}")
    print(f"Success: {success_count}/{total_cases} ({coverage:.1f}%)")
    print(f"Avg latency: {avg_latency:.2f}s")
    print(f"{'='*80}\n")

    # RAGAS evaluation
    print("Running RAGAS metrics (may take 2-5 minutes)...\n")

    ragas_dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts_list,
        "ground_truth": ground_truths,
    })

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

    print("\nRAGAS evaluation completed\n")

    # Manual precision/recall
    precision_recall_list = []
    for retrieved, relevant in zip(retrieved_docs_list, relevant_docs_list):
        pr = calculate_manual_precision_recall(retrieved, relevant)
        precision_recall_list.append(pr)

    avg_precision = sum(pr['precision'] for pr in precision_recall_list) / len(precision_recall_list) if precision_recall_list else 0
    avg_recall = sum(pr['recall'] for pr in precision_recall_list) / len(precision_recall_list) if precision_recall_list else 0

    # BLEU/ROUGE averages
    avg_bleu = {}
    if bleu_scores_list:
        bleu_keys = bleu_scores_list[0].keys()
        for key in bleu_keys:
            avg_bleu[key] = sum(scores[key] for scores in bleu_scores_list) / len(bleu_scores_list)

    avg_rouge = {}
    if rouge_scores_list:
        rouge_keys = rouge_scores_list[0].keys()
        for key in rouge_keys:
            avg_rouge[key] = sum(scores[key] for scores in rouge_scores_list) / len(rouge_scores_list)

    # Process RAGAS results
    ragas_dict = ragas_results.to_pandas().to_dict('list')

    def safe_mean(values):
        """Calculate mean handling NaN values."""
        if isinstance(values, (int, float)):
            return float(values)
        if isinstance(values, list):
            valid_values = [v for v in values if v is not None and str(v).lower() != 'nan']
            return sum(valid_values) / len(valid_values) if valid_values else 0.0
        return 0.0

    # Compile results
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

    # Detailed results per case
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
