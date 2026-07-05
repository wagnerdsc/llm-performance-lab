"""Matplotlib plot generation."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.visualization.heatmap import plot_accuracy_heatmap
from src.visualization.radar import plot_model_radar


def generate_all_plots(results_dir: Path, figures_dir: Path) -> list[Path]:
    """Generate all standard figures from result CSVs."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    quality_csv = results_dir / "quality" / "quality_resultados.csv"
    if quality_csv.exists():
        df = pd.read_csv(quality_csv, encoding="utf-8", errors="replace")
        if "acertou" in df.columns:
            df["acertou"] = df["acertou"].astype(str).str.lower().isin(["true", "1"])

            # Accuracy by model
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

            # Accuracy by dataset
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
    if bench_csv.exists() and quality_csv.exists():
        _plot_latency_vs_accuracy(results_dir, figures_dir, generated)

    return generated


def _plot_latency_vs_accuracy(results_dir: Path, figures_dir: Path, generated: list[Path]) -> None:
    q = pd.read_csv(results_dir / "quality" / "quality_resultados.csv", encoding="utf-8", errors="replace")
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
