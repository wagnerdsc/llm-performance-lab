#!/usr/bin/env bash
# Compila llama.cpp com CUDA (se disponível) ou fallback CPU.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
LLAMA_DIR="${BASE_DIR}/cache/llama.cpp"
BUILD_DIR="${LLAMA_DIR}/build"

echo "=== LLM Performance Lab — Setup llama.cpp ==="
echo "Diretório base: ${BASE_DIR}"
echo "llama.cpp:      ${LLAMA_DIR}"

if [[ ! -d "${LLAMA_DIR}/.git" ]]; then
    echo "Clonando llama.cpp..."
    git clone --depth 1 https://github.com/ggerganov/llama.cpp.git "${LLAMA_DIR}"
else
    echo "Repositório llama.cpp já existe."
fi

mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

GPU_DISPONIVEL=false
if command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null; then
    GPU_DISPONIVEL=true
    echo "GPU detectada: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
else
    echo "Nenhuma GPU NVIDIA detectada."
fi

compilou=false

if [[ "${GPU_DISPONIVEL}" == "true" ]]; then
    echo "Tentando compilação com CUDA..."
    if cmake .. -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release && cmake --build . --config Release -j "$(nproc)"; then
        compilou=true
        echo "Compilação CUDA concluída."
    else
        echo "Compilação CUDA falhou. Tentando fallback CPU..."
        rm -rf "${BUILD_DIR:?}"/*
    fi
fi

if [[ "${compilou}" == "false" ]]; then
    echo "Compilando versão CPU..."
    cmake .. -DCMAKE_BUILD_TYPE=Release
    cmake --build . --config Release -j "$(nproc)"
    echo "Compilação CPU concluída."
fi

CLI="${BUILD_DIR}/bin/llama-cli"
BENCH="${BUILD_DIR}/bin/llama-bench"

echo ""
echo "=== Binários ==="
if [[ -x "${CLI}" ]]; then
    echo "LLAMA_CLI:   ${CLI}"
else
    echo "AVISO: llama-cli não encontrado em ${CLI}"
fi

if [[ -x "${BENCH}" ]]; then
    echo "LLAMA_BENCH: ${BENCH}"
else
    echo "AVISO: llama-bench não encontrado em ${BENCH}"
fi

echo ""
echo "Setup concluído."
