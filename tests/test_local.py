from local_summarizer import summarize_local


title = "Efficient LLM Inference with Quantization"

abstract = """
Large language models require substantial memory and computation
during inference. This work proposes a low-bit quantization method
to reduce memory usage while preserving model accuracy.
Experiments show that memory consumption can be significantly
reduced with only minor degradation in model quality.
"""


result = summarize_local(
    title,
    abstract
)


print("\n=== Local FP32 Result ===")

print(result["summary"])

print("\n=== Performance ===")

print(f"Model: {result['model']}")
print(f"Precision: {result['precision']}")
print(f"Latency: {result['latency']} s")
print(f"Generated tokens: {result['generated_tokens']}")
print(f"Tokens/s: {result['tokens_per_second']}")
print(f"Process RSS: {result['process_rss_mib']} MiB")
print(
    f"RSS change: "
    f"{result['process_rss_delta_mib']} MiB"
)
print(f"Model size: {result['model_size_mib']} MiB")