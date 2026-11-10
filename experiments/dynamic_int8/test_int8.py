
import os

os.environ["HF_HUB_OFFLINE"] = "1"

import gc

import psutil
import torch

import local_summarizer as local


# Copy the exact title and abstract from local_benchmark.py.
title = "Efficient LLM Inference with Quantization"

abstract = """
Large language models require substantial memory and computation
during inference. This work proposes a low-bit quantization method
to reduce memory usage while preserving model accuracy.
Experiments show that memory consumption can be significantly
reduced with only minor degradation in model quality.
"""


print("\n=== INT8 Smoke Test ===")
print(f"Model: {local.MODEL_NAME}")
print(f"Quantization engine: {torch.backends.quantized.engine}")

process = psutil.Process()

rss_before = process.memory_info().rss / (1024 ** 2)

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
    raise RuntimeError(
        "No Linear layers were quantized. Stop and inspect the model."
    )

rss_after = process.memory_info().rss / (1024 ** 2)

print(f"RSS before quantization: {rss_before:.1f} MiB")
print(f"RSS after quantization: {rss_after:.1f} MiB")

print("\nGenerating summary...")

result = local.summarize_local(title, abstract)

print("\n=== INT8 Result ===")
print(result["summary"])

print(f"\nLatency: {result['latency']} s")

if "generated_tokens" in result:
    print(f"Generated tokens: {result['generated_tokens']}")

if "tokens_per_second" in result:
    print(f"Tokens/s: {result['tokens_per_second']}")

print(
    f"RSS after generation: "
    f"{process.memory_info().rss / (1024 ** 2):.1f} MiB"
)
