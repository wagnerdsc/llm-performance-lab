"""Radar chart visualization."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_model_radar(df: pd.DataFrame, figures_dir: Path) -> list[Path]:
    """Plot radar chart for top datasets per model (if single model)."""
    models = df["modelo"].unique() if "modelo" in df.columns else []
    if len(models) != 1:
        return []
    by_ds = df.groupby("dataset")["acertou"].mean().sort_values(ascending=False).head(8)
    if len(by_ds) < 3:
        return []
    labels = [d.split("/")[-1][:12] for d in by_ds.index]
    values = by_ds.values.tolist()
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, "o-", linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=8)
    ax.set_ylim(0, 1)
    ax.set_title("Accuracy Radar")
    plt.tight_layout()
    path = figures_dir / "accuracy_radar.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return [path]
