"""Matplotlib plot generation."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.reports._io import safe_read_csv
from src.visualization.heatmap import plot_accuracy_heatmap
from src.visualization.radar import plot_model_radar


def generate_all_plots(results_dir: Path, figures_dir: Path) -> list[Path]:
    """Generate all standard figures from result CSVs."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    quality_csv = results_dir / "quality" / "quality_resultados.csv"
    df = safe_read_csv(quality_csv)
    if df is not None and "acertou" in df.columns:
        df["acertou"] = df["acertou"].astype(str).str.lower().isin(["true", "1"])

        if "modelo" in df.columns:
            acc_model = df.groupby("modelo")["acertou"].mean()
            fig, ax = plt.subplots(figsize=(10, 4))
            acc_model.plot.bar(ax=ax, color="steelblue")
            ax.set_title("Accuracy by Model")
            ax.set_ylabel("Accuracy")
            ax.set_ylim(0, 1)
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            p = figures_dir / "accuracy_by_model.png"
            fig.savefig(p, dpi=150)
            plt.close(fig)
            generated.append(p)

        acc_ds = df.groupby("dataset")["acertou"].mean().sort_values()
        fig, ax = plt.subplots(figsize=(10, max(4, len(acc_ds) * 0.3)))
        acc_ds.plot.barh(ax=ax, color="coral")
        ax.set_title("Accuracy by Dataset")
        ax.set_xlabel("Accuracy")
        plt.tight_layout()
        p = figures_dir / "accuracy_by_dataset.png"
        fig.savefig(p, dpi=150)
        plt.close(fig)
        generated.append(p)

        generated.extend(plot_accuracy_heatmap(df, figures_dir))
        generated.extend(plot_model_radar(df, figures_dir))

    bench_csv = results_dir / "benchmark" / "benchmark_resultados.csv"
    if safe_read_csv(bench_csv) is not None and df is not None:
        _plot_latency_vs_accuracy(results_dir, figures_dir, generated)

    return generated


def _plot_latency_vs_accuracy(results_dir: Path, figures_dir: Path, generated: list[Path]) -> None:
    q = safe_read_csv(results_dir / "quality" / "quality_resultados.csv")
    if q is None or "acertou" not in q.columns:
        return
    q["acertou"] = q["acertou"].astype(str).str.lower().isin(["true", "1"])
    acc = q.groupby("modelo")["acertou"].mean()
    lat = q.groupby("modelo")["tempo_s"].mean()
    merged = pd.DataFrame({"accuracy": acc, "latency": lat}).dropna()
    if merged.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(merged["latency"], merged["accuracy"], s=80)
    for name, row in merged.iterrows():
        ax.annotate(name.split("/")[-1][:20], (row["latency"], row["accuracy"]), fontsize=7)
    ax.set_xlabel("Mean Latency (s)")
    ax.set_ylabel("Accuracy")
    ax.set_title("Latency vs Accuracy")
    plt.tight_layout()
    p = figures_dir / "latency_vs_accuracy.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    generated.append(p)
