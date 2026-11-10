# ResearchPulse

ResearchPulse is an AI-powered research intelligence pipeline for collecting, filtering, summarizing, searching, and benchmarking academic content.

The project combines a practical research-paper workflow with local LLM inference and Efficient AI experiments, with a focus on inference efficiency, quantization, and reproducible benchmarking.

## Overview

ResearchPulse currently supports the following workflow:

```text
RSS / arXiv Sources
        ↓
Article Collection
        ↓
Cleaning & Deduplication
        ↓
Relevance Scoring
        ↓
SQLite Storage
        ↓
AI Summarization
        ↓
Search / Ranking
        ↓
Inference Benchmarking
```

The project also includes experiments on local LLM inference using:

- PyTorch FP32
- PyTorch Dynamic INT8
- llama.cpp
- GGUF Q8_0
- GGUF Q4_K_M

The current local model used for benchmarking is:

```text
Qwen2.5-0.5B-Instruct
```

---

## Features

### Research Pipeline

- RSS-based research article collection
- Article cleaning and deduplication
- Relevance scoring and ranking
- SQLite-based persistent storage
- Search over collected articles
- Top-article retrieval
- AI-generated paper summaries

### Cloud LLM Integration

ResearchPulse currently supports OpenAI-compatible APIs including:

- DeepSeek
- MiniMax

The system records benchmark metadata such as:

- Provider
- Model
- Precision
- Latency
- Token usage
- Cost
- Output summary
- Status

### Local LLM Inference

ResearchPulse supports local inference experiments using:

- Hugging Face Transformers
- PyTorch
- llama.cpp
- GGUF quantized models

### Quality Evaluation

The project includes experimental quality evaluation utilities for:

- Human evaluation
- Blind comparison
- LLM-as-a-judge evaluation

These components are retained as research experiments rather than the primary production pipeline.

---

## Efficient AI Benchmark

The local inference benchmark compares different inference configurations of Qwen2.5-0.5B-Instruct.

| Configuration | Runtime | Model Size | Prompt Processing | Text Generation | Quality |
|---|---|---:|---:|---:|---|
| FP32 | PyTorch | 1884.6 MiB* | — | 10.86 tok/s | Pass |
| Q8_0 | llama.cpp | 638.74 MiB | 222.11 ± 9.51 tok/s | 58.29 ± 6.25 tok/s | Pass |
| Q4_K_M | llama.cpp | 462.96 MiB | 184.91 ± 15.52 tok/s | 66.55 ± 3.00 tok/s | Pass |

\* The FP32 value represents estimated parameter memory and is not directly equivalent to GGUF file size.

### llama.cpp Benchmark Configuration

Q8_0 and Q4_K_M were benchmarked under the same configuration:

```text
CPU threads:       6
Prompt tokens:     128
Generated tokens:  100
Repetitions:       5
llama.cpp build:   b11946
```

A fixed paper summarization prompt was also used for qualitative validation.

Detailed benchmark data is available in:

```text
benchmarks/
```

---

## Experimental Findings

### PyTorch Dynamic INT8

Dynamic INT8 quantization was initially tested using PyTorch eager-mode quantization.

Although memory usage decreased, the generated summaries showed substantial semantic degradation and off-topic content.

Two variants were tested:

1. Dynamic quantization of eligible Linear layers
2. Selective quantization excluding `lm_head`

Neither produced sufficiently reliable summary quality.

The project therefore moved to:

```text
llama.cpp + GGUF
```

with Q8_0 and Q4_K_M quantization.

This produced much more stable summary quality while significantly reducing model size.

More details are available in:

```text
benchmarks/EXPERIMENT_NOTES.md
```

---

## Project Structure

```text
ResearchPulse/
├── benchmarks/
│   ├── prompts/
│   ├── results/
│   ├── scripts/
│   ├── README.md
│   └── EXPERIMENT_NOTES.md
│
├── evaluation/
│   ├── scripts/
│   ├── evaluator.py
│   ├── judge.py
│   └── analyze_quality.py
│
├── experiments/
│   └── dynamic_int8/
│
├── tests/
│
├── collector.py
├── config.py
├── database.py
├── filter.py
├── summarizer.py
├── local_summarizer.py
├── benchmark.py
├── main.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

Local runtime artifacts are intentionally excluded from Git:

```text
data/
models/
results/
.env
.venv/
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yerbery-cloud/ResearchPulse.git
cd ResearchPulse
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file:

```bash
cp .env.example .env
```

Then configure your API credentials in:

```text
.env
```

Example variables include:

```text
LLM_API_KEY
LLM_BASE_URL
LLM_MODEL

MINIMAX_API_KEY
MINIMAX_BASE_URL
MINIMAX_MODEL
```

---

## Running ResearchPulse

Run the main pipeline from the project root:

```bash
python main.py
```

The exact behavior depends on the current configuration and available API credentials.

---

## Benchmark Data

Reproducible benchmark artifacts are stored in:

```text
benchmarks/results/
```

The machine-readable summary is:

```text
benchmarks/results/benchmark_summary.csv
```

The fixed summarization prompt used for qualitative comparison is stored in:

```text
benchmarks/prompts/paper_summary_prompt.txt
```

---

## Current Status

Completed:

- Research article collection
- Cleaning and deduplication
- SQLite storage
- Relevance ranking
- Cloud LLM summarization
- Benchmark result storage
- Quality evaluation experiments
- PyTorch FP32 local inference
- PyTorch Dynamic INT8 experiments
- llama.cpp Q8_0 benchmark
- llama.cpp Q4_K_M benchmark

In progress:

- Unified benchmark visualization
- Web dashboard
- Better local inference integration
- Search and paper exploration interface

---

## Roadmap

Planned improvements include:

- Web-based research dashboard
- Benchmark visualization
- Vector search and embeddings
- Automatic local/cloud model selection
- More reproducible inference experiments
- Better profiling for latency and memory usage

---

## Project Motivation

ResearchPulse was built as both a practical research assistant and an Efficient AI / AI Systems learning project.

The project focuses not only on calling language models, but also on understanding the systems questions behind local inference:

- How does quantization affect model size?
- How does inference runtime affect throughput?
- What is the trade-off between compression and summary quality?
- How do different deployment backends behave on CPU hardware?
- How should inference experiments be measured reproducibly?

The goal is to gradually evolve ResearchPulse from a research-paper pipeline into a small but reproducible research intelligence and inference benchmarking system.