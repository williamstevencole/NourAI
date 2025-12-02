import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import TOP_K


def print_summary_report(results: dict):
    """Print evaluation summary to console."""
    print("\n" + "="*80)
    print("EVALUATION REPORT - NUTRI-RAG (RAGAS)")
    print("="*80)

    metadata = results['metadata']
    ragas = results['ragas_metrics']
    additional = results['additional_metrics']

    # General summary
    print(f"\nGENERAL SUMMARY:")
    print(f"   Total cases: {metadata['total_test_cases']}")
    print(f"   Successful: {metadata['successful_cases']}")
    print(f"   Coverage: {metadata['coverage_percentage']}%")
    print(f"   Avg latency: {metadata['average_latency_seconds']}s")

    # RAGAS metrics (0-1 scale)
    print(f"\nRAGAS METRICS (0-1 scale):")
    print(f"   Faithfulness: {ragas['faithfulness']:.3f}")
    print(f"      Does the answer stay faithful to the context?")
    print(f"   Answer Relevancy: {ragas['answer_relevancy']:.3f}")
    print(f"      Is the answer relevant to the question?")
    print(f"   Context Recall: {ragas['context_recall']:.3f}")
    print(f"      Were all necessary contexts retrieved?")
    print(f"   Context Precision: {ragas['context_precision']:.3f}")
    print(f"      Are relevant contexts ranked high?")
    print(f"   Answer Correctness: {ragas['answer_correctness']:.3f}")
    print(f"      Is the answer factually correct?")

    # Retrieval metrics
    print(f"\nRETRIEVAL METRICS:")
    print(f"   Precision@{TOP_K}: {additional['precision']:.3f} ({additional['precision']*100:.1f}%)")
    print(f"   Recall@{TOP_K}: {additional['recall']:.3f} ({additional['recall']*100:.1f}%)")

    # BLEU scores
    bleu = additional.get('bleu', {})
    if bleu:
        print(f"\nBLEU SCORES (n-gram precision):")
        print(f"   BLEU-1: {bleu.get('bleu_1', 0):.3f}")
        print(f"   BLEU-2: {bleu.get('bleu_2', 0):.3f}")
        print(f"   BLEU-3: {bleu.get('bleu_3', 0):.3f}")
        print(f"   BLEU-4: {bleu.get('bleu_4', 0):.3f}")
        print(f"   BLEU Avg: {bleu.get('bleu_avg', 0):.3f} ({bleu.get('bleu_avg', 0)*100:.1f}%)")

    # ROUGE scores
    rouge = additional.get('rouge', {})
    if rouge:
        print(f"\nROUGE SCORES (text similarity):")
        print(f"   ROUGE-1 F1: {rouge.get('rouge_1_f1', 0):.3f} ({rouge.get('rouge_1_f1', 0)*100:.1f}%)")
        print(f"   ROUGE-2 F1: {rouge.get('rouge_2_f1', 0):.3f} ({rouge.get('rouge_2_f1', 0)*100:.1f}%)")
        print(f"   ROUGE-L F1: {rouge.get('rouge_l_f1', 0):.3f} ({rouge.get('rouge_l_f1', 0)*100:.1f}%)")

    # Overall score
    avg_score = sum(ragas.values()) / len(ragas)
    print(f"\nAVERAGE RAGAS SCORE: {avg_score:.3f} ({avg_score*100:.1f}%)")

    # Interpretation
    print(f"\nINTERPRETATION:")
    if avg_score >= 0.7:
        print("   EXCELLENT - System shows very solid performance")
    elif avg_score >= 0.5:
        print("   GOOD - System works well but has room for improvement")
    else:
        print("   NEEDS IMPROVEMENT - Consider significant optimizations")

    print("\n" + "="*80)
