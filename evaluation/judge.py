import json
import os
import re

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


def clean_json_output(text):
    # 去掉 MiniMax 可能产生的 think 内容
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL
    )

    # 去掉 ```json ... ```
    text = text.replace("```json", "")
    text = text.replace("```", "")

    # 只截取 JSON 对象
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("Judge did not return valid JSON.")

    return text[start:end + 1]


def judge_summary(abstract, summary, provider):
    if provider == "deepseek":
        client = deepseek_client
        model = deepseek_model

    elif provider == "minimax":
        client = minimax_client
        model = minimax_model

    else:
        raise ValueError(f"Unknown judge provider: {provider}")

    prompt = f"""
You are a strict evaluator of research paper summaries.

Original Abstract:
{abstract}

Candidate Summary:
{summary}

Evaluate the candidate on four dimensions from 0 to 10.

Scoring must be strict.

Faithfulness:
10 = fully supported by the abstract, no unsupported claims
8 = accurate with only very minor overstatement
6 = one noticeable distortion or unsupported inference
4 = important factual error
2 = multiple hallucinations
0 = seriously contradicts the abstract

Coverage:
10 = captures the core problem, method, and major results
8 = covers almost everything but misses a minor point
6 = misses one important component
4 = misses several important ideas
2 = captures very little
0 = fundamentally misses the paper

Conciseness:
10 = highly information-dense with virtually no redundancy
8 = concise with minor unnecessary wording
6 = somewhat verbose or repetitive
4 = clearly inefficient
2 = very verbose or poorly structured
0 = unusable

Usefulness:
10 = lets a researcher clearly understand what was done,
how it was done, what was found, and why it matters
8 = very useful but lacks a minor detail
6 = generally useful but requires reading the abstract
4 = limited usefulness
2 = barely useful
0 = useless

Important:
- Do NOT give 10 unless there is essentially nothing worth deducting.
- A good but imperfect summary should normally score around 7-9.
- Be willing to use the full 0-10 scale.
- Do not guess which model generated the summary.

Return ONLY valid JSON:

{{
  "faithfulness": 0,
  "coverage": 0,
  "conciseness": 0,
  "usefulness": 0,
  "notes": "brief explanation of the main strengths and weaknesses"
}}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    raw_text = response.choices[0].message.content

    cleaned = clean_json_output(raw_text)

    return json.loads(cleaned)