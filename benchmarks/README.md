# ResearchPulse Benchmark

This directory contains reproducible local LLM inference benchmarks for ResearchPulse.

## Goal

The benchmark evaluates the trade-off between inference efficiency and summary quality under different local inference configurations.

Current experiments use:

- Model: Qwen2.5-0.5B-Instruct
- Hardware: CPU
- Task: research paper summarization
- Metrics: model size, latency, prompt processing speed, text generation speed, memory usage, and qualitative output quality

## Results

| Configuration | Runtime | Model Size | Prompt Processing | Text Generation | Quality |
|---|---|---:|---:|---:|---|
| FP32 | PyTorch | 1884.6 MiB* | — | 10.86 tok/s | Pass |
| Q8_0 | llama.cpp | 638.74 MiB | 222.11 ± 9.51 tok/s | 58.29 ± 6.25 tok/s | Pass |
| Q4_K_M | llama.cpp | 462.96 MiB | 184.91 ± 15.52 tok/s | 66.55 ± 3.00 tok/s | Pass |

\* The FP32 value is estimated parameter memory and is not directly equivalent to GGUF file size.

## llama.cpp Benchmark Settings

Q8_0 and Q4_K_M were tested with the same configuration:

- CPU threads: 6
- Prompt tokens: 128
- Generated tokens: 100
- Repetitions: 5
- llama.cpp build: b11946

## Directory Structure

```text
benchmarks/
├── README.md
├── prompts/
│   └── paper_summary_prompt.txt
├── results/
│   ├── benchmark_summary.csv
│   ├── fp32_baseline_v2.txt
│   ├── q8_benchmark.txt
│   ├── q8_quality.txt
│   ├── q4_benchmark.txt
│   └── q4_quality.txt
└── scripts/

```
## Notes

PyTorch FP32 and llama.cpp GGUF use different inference runtimes. Therefore, their raw throughput numbers should not be interpreted as a pure precision-only comparison.

Q8_0 and Q4_K_M provide a more controlled comparison because both use the same model family, runtime, hardware, thread count, and benchmark configuration.