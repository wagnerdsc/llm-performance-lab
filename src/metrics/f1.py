"""Token-level F1 metric."""

from __future__ import annotations

from src.datasets._legacy import normalizar_txt


def token_f1(prediction: str, reference: str) -> float:
    pred_tokens = set(normalizar_txt(prediction).split())
    ref_tokens = set(normalizar_txt(reference).split())
    if not pred_tokens or not ref_tokens:
        return 0.0
    common = pred_tokens & ref_tokens
    if not common:
        return 0.0
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(ref_tokens)
    return 2 * precision * recall / (precision + recall)
