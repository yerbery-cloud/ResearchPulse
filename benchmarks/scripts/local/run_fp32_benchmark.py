from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
from statistics import mean, median

from local_summarizer import MODEL_NAME, summarize_local


title = "Efficient LLM Inference with Quantization"

abstract = """
Large language models require substantial memory and computation
during inference. This work proposes a low-bit quantization method
to reduce memory usage while preserving model accuracy.
Experiments show that memory consumption can be significantly
reduced with only minor degradation in model quality.
"""

WARMUP_RUNS = 1
MEASURED_RUNS = 5


print("\n=== FP32 Benchmark ===")
print(f"Model: {MODEL_NAME}")
print(f"Warm-up runs: {WARMUP_RUNS}")
print(f"Measured runs: {MEASURED_RUNS}")

# Warm-up: excluded from the statistics.
for _ in range(WARMUP_RUNS):
    summarize_local(title, abstract)

print("\nWarm-up completed.")

results = []

for i in range(1, MEASURED_RUNS + 1):
    result = summarize_local(title, abstract)
    results.append(result)

    print(
        f"Run {i}: "
        f"latency={result['latency']:.3f}s, "
        f"tokens={result['generated_tokens']}, "
        f"tokens/s={result['tokens_per_second']:.2f}, "
        f"RSS={result['process_rss_mib']:.1f} MiB"
    )

latencies = [r["latency"] for r in results]
throughputs = [r["tokens_per_second"] for r in results]
rss_values = [r["process_rss_mib"] for r in results]

print("\n=== Summary ===")
print(f"Model: {MODEL_NAME}")
print(f"Precision: FP32")
print(f"Runs: {len(results)}")

print(f"Mean latency: {mean(latencies):.3f}s")
print(f"Median latency: {median(latencies):.3f}s")
print(f"Min latency: {min(latencies):.3f}s")
print(f"Max latency: {max(latencies):.3f}s")

print(f"Median tokens/s: {median(throughputs):.2f}")
print(f"Median process RSS: {median(rss_values):.1f} MiB")
print(f"Model size: {results[-1]['model_size_mib']:.1f} MiB")

print("\n=== Sample Summary ===")
print(results[-1]["summary"])
