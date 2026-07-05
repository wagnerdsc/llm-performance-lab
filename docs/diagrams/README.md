# Architecture Diagrams

Visual documentation for the **LLM Performance Lab** pipeline. All diagrams are written in [Mermaid](https://mermaid.js.org/) (`.mmd`) and render natively on GitHub.

## Diagram Index

| File | Description |
|------|-------------|
| [architecture.mmd](architecture.mmd) | End-to-end framework: CLI → BenchmarkRunner → llama.cpp → results & reports |
| [quality_pipeline.mmd](quality_pipeline.mmd) | Quality benchmark flow: datasets → evaluators → llama-cli → CSV → reports |
| [resume_logic.mmd](resume_logic.mmd) | Incremental CSV resume: key lookup, skip vs infer, append |
| [data_layout.mmd](data_layout.mmd) | Directory layout: models, datasets, results, reports, figures |
| [benchmark_types.mmd](benchmark_types.mmd) | Evaluator types, example datasets, and metrics |

## How to View

### GitHub (recommended)

Push the repository and open any `.mmd` file in the browser. GitHub renders Mermaid blocks automatically when the file is embedded in Markdown:

````markdown
```mermaid
flowchart LR
    A --> B
```
````

For standalone `.mmd` files, copy the contents into a Markdown file wrapped in a ` ```mermaid ` fence, or use one of the options below.

### VS Code / Cursor

1. Install the [Markdown Preview Mermaid Support](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid) extension, **or**
2. Install [Mermaid Preview](https://marketplace.visualstudio.com/items?itemName=vstirbu.vscode-mermaid-preview) for direct `.mmd` preview.

Then open a diagram file and run **Preview** (`Ctrl+Shift+V` / `Cmd+Shift+V`) or use the Mermaid Preview command palette action.

### Mermaid Live Editor

1. Go to [https://mermaid.live](https://mermaid.live)
2. Paste the contents of any `.mmd` file into the editor
3. Export as PNG or SVG if needed for papers or slides

### CLI (optional)

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i docs/diagrams/architecture.mmd -o docs/diagrams/architecture.png
```

## Editing Guidelines

- Keep node labels short; use `<br/>` for line breaks inside Mermaid nodes.
- Prefer `flowchart TB/LR` over deprecated `graph` syntax.
- Update diagrams when adding benchmarks, evaluators, or changing output paths.
- Link changes from [architecture.md](../architecture.md) and the root [README.md](../../README.md).

## Related Documentation

- [Architecture overview](../architecture.md)
- [Data layout](../data_layout.md)
- [Adding datasets](../adding_datasets.md)
- [Adding models](../adding_models.md)
