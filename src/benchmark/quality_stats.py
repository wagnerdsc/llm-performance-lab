"""Quality benchmark run statistics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QualityRunStats:
    """Counters for a single quality benchmark run."""

    inferences_run: int = 0
    responses_received: int = 0
    records_added: int = 0
    items_skipped: int = 0
    rows_before: int = 0
    rows_after: int = 0
