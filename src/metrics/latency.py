"""Latency metrics."""

from __future__ import annotations


def compute_latency(latency_s: float) -> dict[str, float]:
    return {"latency_s": latency_s, "latency_ms": latency_s * 1000}
