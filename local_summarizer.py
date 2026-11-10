import time

import psutil
import torch

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)


MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"

# Lazy loading:
# importing this module will not immediately load the model.
tokenizer = None
model = None


def load_model():
    """
    Load the tokenizer and model only when they are actually needed.
    Subsequent calls reuse the already loaded objects.
    """
    global tokenizer, model

    if tokenizer is None:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    if model is None:
        print(f"Loading local model: {MODEL_NAME}")

        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float32,
            device_map="cpu",
        )

        model.eval()

    return tokenizer, model


def get_model_size_mib():
    """
    Estimate model parameter memory in MiB.
    """
    _, current_model = load_model()

    size = 0

    for param in current_model.parameters():
        size += param.numel() * param.element_size()

    return size / (1024 ** 2)


def summarize_local(title, abstract):
    current_tokenizer, current_model = load_model()

    messages = [
        {
            "role": "system",
            "content": (
                "You are a research paper summarizer. "
                "Use only facts explicitly stated in the provided title and abstract. "
                "Output exactly three bullet points:\n"
                "- Problem: the research problem.\n"
                "- Method: the proposed method.\n"
                "- Finding: the reported result, if any.\n"
                "Use at most 50 words in total. "
                "Do not repeat the title or abstract. "
                "Never invent numbers, percentages, experiments, or limitations. "
                "Do not infer results that are not explicitly reported. "
                "If a detail is missing, omit it. "
                "Do not add a separate limitations section."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Title: {title}\n\n"
                f"Abstract:\n{abstract}"
            ),
        },
    ]

    text = current_tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = current_tokenizer(
        text,
        return_tensors="pt",
    )

    process = psutil.Process()

    memory_before = (
        process.memory_info().rss / (1024 ** 2)
    )

    start_time = time.perf_counter()

    with torch.inference_mode():
        outputs = current_model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=False,
            repetition_penalty=1.08,
            no_repeat_ngram_size=4,
            eos_token_id=current_tokenizer.eos_token_id,
            pad_token_id=(
                current_tokenizer.pad_token_id
                if current_tokenizer.pad_token_id is not None
                else current_tokenizer.eos_token_id
            ),
        )

    latency = time.perf_counter() - start_time

    memory_after = (
        process.memory_info().rss / (1024 ** 2)
    )

    generated_tokens = outputs[0][
        inputs["input_ids"].shape[1]:
    ]

    summary = current_tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    ).strip()

    generated_token_count = int(
        generated_tokens.numel()
    )

    if generated_token_count >= 100:
        print(
            "Warning: generation reached the token limit; "
            "check whether the summary is truncated."
        )

    quantized_layers = sum(
        isinstance(
            module,
            torch.ao.nn.quantized.dynamic.Linear,
        )
        for module in current_model.modules()
    )

    precision = (
        "INT8"
        if quantized_layers > 0
        else "FP32"
    )

    return {
        "summary": summary,
        "model": MODEL_NAME,
        "precision": precision,
        "latency": round(latency, 3),
        "generated_tokens": generated_token_count,
        "tokens_per_second": (
            round(
                generated_token_count / latency,
                2,
            )
            if latency > 0
            else 0.0
        ),
        "process_rss_mib": round(
            memory_after,
            1,
        ),
        "process_rss_delta_mib": round(
            memory_after - memory_before,
            1,
        ),
        "model_size_mib": round(
            get_model_size_mib(),
            1,
        ),
    }