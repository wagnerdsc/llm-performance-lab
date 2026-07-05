# Adding Models

## Step 1: Download or convert to GGUF

Use llama.cpp conversion tools or download pre-quantized models from Hugging Face.

## Step 2: Place in models directory

```bash
mkdir -p models/MyModel-7B
cp /path/to/MyModel-7B-Q4_K_M.gguf models/MyModel-7B/
```

## Step 3: Verify discovery

```bash
python scripts/00_check_data.py
# or
python run.py --list  # after benchmarks registered
```

## Step 4: Run benchmarks

```bash
python run.py --benchmark quality --limit-models 1 --limit-items 5
python run.py --benchmark throughput --model-glob '*Q4_K_M*'
```

## Tips

- Use descriptive filenames with quantization suffix (e.g. `-Q4_K_M.gguf`)
- Group quantizations of the same base model in one subdirectory
- F16 models are large — use `--timeout 900` on CPU
