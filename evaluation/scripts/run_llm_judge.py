from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database import (
    get_human_blind_pairs,
    quality_evaluation_exists,
    save_quality_evaluation,
)

from evaluation.evaluator import calculate_quality_score
from evaluation.judge import judge_summary


pairs = get_human_blind_pairs(limit=3)

judges = [
    "deepseek",
    "minimax",
]


if not pairs:
    print("No human-blind benchmark pairs found.")
    exit()


for index, (
    title,
    abstract,
    deepseek_id,
    deepseek_summary,
    minimax_id,
    minimax_summary,
) in enumerate(pairs, start=1):

    print("\n" + "=" * 70)
    print(f"Paper {index}/{len(pairs)}")
    print(title)

    candidates = [
        (
            deepseek_id,
            deepseek_summary
        ),
        (
            minimax_id,
            minimax_summary
        ),
    ]

    for judge_provider in judges:

        evaluator_name = f"llm_judge_{judge_provider}_v2"

        print(f"\nJudge: {judge_provider}")

        for benchmark_id, summary in candidates:

            if quality_evaluation_exists(
                benchmark_id,
                evaluator_name
            ):
                print(
                    f"Benchmark {benchmark_id}: "
                    f"already evaluated, skipping."
                )
                continue

            try:
                scores = judge_summary(
                    abstract,
                    summary,
                    provider=judge_provider
                )

                overall = calculate_quality_score(
                    scores["faithfulness"],
                    scores["coverage"],
                    scores["conciseness"],
                    scores["usefulness"]
                )

                save_quality_evaluation(
                    benchmark_id=benchmark_id,
                    faithfulness=scores["faithfulness"],
                    coverage=scores["coverage"],
                    conciseness=scores["conciseness"],
                    usefulness=scores["usefulness"],
                    overall_score=overall,
                    evaluator=evaluator_name,
                    notes=scores.get("notes", "")
                )

                print(
                    f"Benchmark {benchmark_id}: "
                    f"{overall}"
                )

            except Exception as e:
                print(
                    f"Benchmark {benchmark_id} failed: {e}"
                )