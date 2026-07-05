"""Accuracy heatmap visualization."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def plot_accuracy_heatmap(df: pd.DataFrame, figures_dir: Path) -> list[Path]:
    """Plot model × dataset accuracy heatmap."""
    if "modelo" not in df.columns or "dataset" not in df.columns:
        return []
    pivot = df.pivot_table(index="dataset", columns="modelo", values="acertou", aggfunc="mean")
    if pivot.empty:
        return []
    fig, ax = plt.subplots(figsize=(max(8, pivot.shape[1] * 1.5), max(6, pivot.shape[0] * 0.3)))
    im = ax.imshow(pivot.values, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([c.split("/")[-1][:15] for c in pivot.columns], rotation=45, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([i.split("/")[-1][:25] for i in pivot.index], fontsize=7)
    ax.set_title("Accuracy Heatmap (Model × Dataset)")
    fig.colorbar(im, ax=ax, label="Accuracy")
    plt.tight_layout()
    path = figures_dir / "accuracy_heatmap.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return [path]
