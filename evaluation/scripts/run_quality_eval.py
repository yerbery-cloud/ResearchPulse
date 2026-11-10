from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database import (
    get_unevaluated_benchmarks,
    save_quality_evaluation,
)

from evaluation.evaluator import calculate_quality_score


def get_score(name):
    while True:
        try:
            score = float(input(f"{name} (1-5): "))

            if 1 <= score <= 5:
                return score

            print("Please enter a score between 1 and 5.")

        except ValueError:
            print("Please enter a number.")


results = get_unevaluated_benchmarks(limit=6)


if not results:
    print("No benchmark results waiting for evaluation.")
    exit()


for (
    benchmark_id,
    title,
    abstract,
    provider,
    model,
    output_summary,
) in results:

    print("\n" + "=" * 70)

    print(f"Paper: {title}")
    print(f"Provider: {provider}")
    print(f"Model: {model}")

    print("\n--- Original Abstract ---")
    print(abstract)

    print("\n--- Generated Summary ---")
    print(output_summary)

    print("\n--- Evaluation ---")

    faithfulness = get_score("Faithfulness")
    coverage = get_score("Coverage")
    conciseness = get_score("Conciseness")
    usefulness = get_score("Usefulness")

    overall_score = calculate_quality_score(
        faithfulness,
        coverage,
        conciseness,
        usefulness
    )

    notes = input("Notes (optional): ")

    save_quality_evaluation(
        benchmark_id=benchmark_id,
        faithfulness=faithfulness,
        coverage=coverage,
        conciseness=conciseness,
        usefulness=usefulness,
        overall_score=overall_score,
        evaluator="human",
        notes=notes
    )

    print(f"\nSaved. Overall score: {overall_score}")