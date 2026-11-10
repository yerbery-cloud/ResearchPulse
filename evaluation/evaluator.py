WEIGHTS = {
    "faithfulness": 0.35,
    "coverage": 0.30,
    "usefulness": 0.20,
    "conciseness": 0.15,
}


def calculate_quality_score(
    faithfulness,
    coverage,
    conciseness,
    usefulness
):
    score = (
        faithfulness * 10 * WEIGHTS["faithfulness"]
        + coverage * 10 * WEIGHTS["coverage"]
        + usefulness * 10 * WEIGHTS["usefulness"]
        + conciseness * 10 * WEIGHTS["conciseness"]
    )

    return round(score, 2)