# Experiment Notes

## PyTorch Dynamic INT8

Before adopting GGUF + llama.cpp, ResearchPulse tested PyTorch eager-mode dynamic INT8 quantization on Qwen2.5-0.5B-Instruct.

Two variants were evaluated:

1. Dynamic quantization of all eligible Linear layers.
2. Selective dynamic quantization excluding `lm_head`.

Although memory usage decreased, generated summaries showed substantial semantic degradation and off-topic content.

For this reason, PyTorch dynamic INT8 is retained as an experimental record but is not used as the final local quantization solution.

The project subsequently switched to:

- llama.cpp
- GGUF
- Q8_0
- Q4_K_M

These configurations produced significantly more reliable summary quality.