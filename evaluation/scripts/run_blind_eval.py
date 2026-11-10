from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import random

from database import (
    get_blind_eval_pairs,
    save_quality_evaluation,
)

from evaluation.evaluator import calculate_quality_score


def get_score(name):
    while True:
        try:
            score = float(input(f"{name} (0-10): "))

            if 0 <= score <= 10:
                return score

            print("请输入 0 到 10 之间的分数。")

        except ValueError:
            print("请输入数字。")


def evaluate_summary(label, summary):
    print(f"\n--- Summary {label} ---")
    print(summary)

    print(f"\nEvaluate Summary {label}")

    faithfulness = get_score("Faithfulness")
    coverage = get_score("Coverage")
    conciseness = get_score("Conciseness")
    usefulness = get_score("Usefulness")

    overall = calculate_quality_score(
        faithfulness,
        coverage,
        conciseness,
        usefulness,
    )

    notes = input("Notes (optional): ")

    return {
        "faithfulness": faithfulness,
        "coverage": coverage,
        "conciseness": conciseness,
        "usefulness": usefulness,
        "overall": overall,
        "notes": notes,
    }


pairs = get_blind_eval_pairs(limit=3)

if not pairs:
    print("No papers available for blind evaluation.")
    exit()


reveals = []


for index, row in enumerate(pairs, start=1):

    (
        title,
        abstract,

        deepseek_id,
        deepseek_provider,
        deepseek_model,
        deepseek_summary,

        minimax_id,
        minimax_provider,
        minimax_model,
        minimax_summary,
    ) = row

    candidates = [
        {
            "benchmark_id": deepseek_id,
            "provider": deepseek_provider,
            "model": deepseek_model,
            "summary": deepseek_summary,
        },
        {
            "benchmark_id": minimax_id,
            "provider": minimax_provider,
            "model": minimax_model,
            "summary": minimax_summary,
        },
    ]

    random.shuffle(candidates)

    print("\n" + "=" * 70)
    print(f"Paper {index}/{len(pairs)}")
    print(title)

    print("\n--- Original Abstract ---")
    print(abstract)

    labels = ["A", "B"]

    for label, candidate in zip(labels, candidates):

        scores = evaluate_summary(
            label,
            candidate["summary"]
        )

        save_quality_evaluation(
            benchmark_id=candidate["benchmark_id"],
            faithfulness=scores["faithfulness"],
            coverage=scores["coverage"],
            conciseness=scores["conciseness"],
            usefulness=scores["usefulness"],
            overall_score=scores["overall"],
            evaluator="human_blind_v2",
            notes=scores["notes"],
        )

        candidate["label"] = label
        candidate["overall"] = scores["overall"]

    reveals.append(
        (
            title,
            candidates[0],
            candidates[1],
        )
    )


print("\n" + "=" * 70)
print("Blind Evaluation Finished")
print("=" * 70)

for title, first, second in reveals:

    print(f"\n{title}")

    print(
        f"Summary {first['label']} "
        f"= {first['provider']} / {first['model']} "
        f"(score {first['overall']})"
    )

    print(
        f"Summary {second['label']} "
        f"= {second['provider']} / {second['model']} "
        f"(score {second['overall']})"
    )