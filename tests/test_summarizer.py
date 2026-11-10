from summarizer import summarize_article

title = "Efficient LLM Inference with Quantization"

abstract = """
Large language models require substantial memory and computation
during inference. This work proposes a low-bit quantization method
to reduce memory usage while preserving model accuracy.
"""

summary = summarize_article(title,abstract)

print(summary)