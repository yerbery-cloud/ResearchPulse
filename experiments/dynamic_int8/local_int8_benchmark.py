from statistics import mean, median

import gc
import torch
import local_summarizer as local

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

print("\nApplying dynamic INT8 quantization...")

local.model = torch.ao.quantization.quantize_dynamic(
    local.model,
    {torch.nn.Linear},
    dtype=torch.qint8,
    inplace=True,
)

local.model.eval()
gc.collect()

quantized_layers = sum(
    isinstance(module, torch.ao.nn.quantized.dynamic.Linear)
    for module in local.model.modules()
)

print(f"Quantized Linear layers: {quantized_layers}")

if quantized_layers == 0:
    raise RuntimeError("No Linear layers were quantized.")

print("\n=== INT8 Benchmark ===")
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
    result["precision"] = "INT8"
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
print(f"Precision: INT8")
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
