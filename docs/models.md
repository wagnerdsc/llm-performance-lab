# Models

Models are discovered recursively: `models/**/*.gguf`

## Expected Layout

```
models/
└── Qwen2.5-3B-Instruct/
    ├── Qwen2.5-3B-Instruct-F16.gguf
    ├── Qwen2.5-3B-Instruct-Q4_K_M.gguf
    └── ...
```

## Extracted Metadata

For each GGUF file, the framework extracts:

- **path**: Relative path from `models_dir`
- **family**: Parent directory name
- **quantization**: Parsed from filename (Q4_K_M, F16, etc.)
- **size_gib / size_gb**: File size

## Adding a Model

1. Place `.gguf` files under `models/<family>/`
2. Run `python run.py --list` or `python scripts/00_check_data.py` to verify discovery
3. No code changes required

See [adding_models.md](adding_models.md) for detailed instructions.
