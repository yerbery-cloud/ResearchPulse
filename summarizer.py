import os
import re
import time

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


deepseek_client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL")
)

minimax_client = OpenAI(
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url=os.getenv("MINIMAX_BASE_URL")
)


deepseek_model = os.getenv("LLM_MODEL")
minimax_model = os.getenv("MINIMAX_MODEL")


cache_hit_price = float(
    os.getenv("DEEPSEEK_CACHE_HIT_PRICE", "0")
)

cache_miss_price = float(
    os.getenv("DEEPSEEK_CACHE_MISS_PRICE", "0")
)

output_price = float(
    os.getenv("DEEPSEEK_OUTPUT_PRICE", "0")
)

def clean_output(text):
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL
    )

    return text.strip()

def summarize_article(title, abstract, provider="deepseek"):
    if not abstract:
        return {
            "summary": "No abstract available.",
            "model": None,
            "latency": 0.0,
            "status": "skipped",
            "error": None,
            "prompt_tokens": 0,
            "cache_hit_tokens": 0,
            "cache_miss_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cost": None
        }

    if provider == "deepseek":
        client = deepseek_client
        model = deepseek_model

    elif provider == "minimax":
        client = minimax_client
        model = minimax_model

    else:
        raise ValueError(f"Unknown provider: {provider}")

    prompt = f"""
You are a research paper assistant.

Title:
{title}

Abstract:
{abstract}

Summarize using exactly:

Problem:
Method:
Result:
Why it matters:

Keep the response concise.
Do not include reasoning or thinking process.
"""

    start_time = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        latency = time.perf_counter() - start_time

        usage = response.usage

        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0
        total_tokens = usage.total_tokens if usage else 0

        cache_hit_tokens = 0
        cache_miss_tokens = prompt_tokens

        
        summary = clean_output(
            response.choices[0].message.content
        )

        # DeepSeek：按 token 估算成本
        if provider == "deepseek":

            cache_hit_tokens = getattr(
                usage,
                "prompt_cache_hit_tokens",
                0
            )

            cache_miss_tokens = getattr(
                usage,
                "prompt_cache_miss_tokens",
                prompt_tokens
            )

            cost = (
                cache_hit_tokens / 1_000_000 * cache_hit_price
                + cache_miss_tokens / 1_000_000 * cache_miss_price
                + completion_tokens / 1_000_000 * output_price
            )

        # MiniMax：你现在是订阅制，不能写成 ¥0
        else:
            cost = None

        return {
        "summary": summary,
        "model": model,
        "latency": round(latency, 3),
        "status": "success",
        "error": None,
        "prompt_tokens": prompt_tokens,
        "cache_hit_tokens": cache_hit_tokens,
        "cache_miss_tokens": cache_miss_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cost": (
            round(cost, 6)
            if cost is not None
            else None
        )
}

    except Exception as e:
        latency = time.perf_counter() - start_time

        return {
        "summary": None,
        "model": model,
        "latency": round(latency, 3),
        "status": "failed",
        "error": str(e),
        "prompt_tokens": 0,
        "cache_hit_tokens": 0,
        "cache_miss_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "cost": None
}