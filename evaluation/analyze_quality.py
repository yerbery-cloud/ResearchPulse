from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmark import get_evaluation_comparison


results = get_evaluation_comparison()


print("\n=== Quality Evaluation Comparison ===\n")


for (
    evaluator,
    provider,
    model,
    evaluations,
    faithfulness,
    coverage,
    conciseness,
    usefulness,
    overall,
) in results:

    print(f"{evaluator} | {provider} | {model}")

    print(
        f"Evaluations: {evaluations}\n"
        f"Faithfulness: {faithfulness:.2f}\n"
        f"Coverage: {coverage:.2f}\n"
        f"Conciseness: {conciseness:.2f}\n"
        f"Usefulness: {usefulness:.2f}\n"
        f"Overall: {overall:.2f}\n"
    )