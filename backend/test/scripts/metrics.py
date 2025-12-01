from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from typing import List


def calculate_bleu(generated: str, reference: str) -> dict:
    """Calculate BLEU scores (1-4 and average)."""
    gen_tokens = generated.lower().split()
    ref_tokens = [reference.lower().split()]

    smoothing = SmoothingFunction().method1

    # BLEU n-grams: weights = (1, 0, 0, 0) for unigrams, etc.
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
    """Calculate ROUGE scores (precision, recall, F1)."""
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


def calculate_manual_precision_recall(retrieved_docs: List[str], relevant_docs: List[str]) -> dict:
    """
    Manual precision/recall calculation.
    Precision = |retrieved ∩ relevant| / |retrieved|
    Recall = |retrieved ∩ relevant| / |relevant|
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
