from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import sqlite3

from summarizer import summarize_article
from database import save_benchmark_result


DB_PATH = "data/researchpulse.db"


def get_test_articles(limit=5):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title, summary
            FROM articles
            WHERE summary IS NOT NULL
            ORDER BY score DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()

articles = get_test_articles(limit=5)

providers = [
    "deepseek",
    "minimax"
]

for index, (article_id, title, abstract) in enumerate(articles, start=1):

    print(f"\n{'=' * 60}")
    print(f"Paper {index}/{len(articles)}")
    print(title)
    print("=" * 60)

    for provider in providers:

        print(f"\nRunning {provider}...")

        result = summarize_article(
            title,
            abstract,
            provider=provider
        )

        save_benchmark_result(
            article_id,
            result,
            provider=provider,
            precision="API"
        )

        if result["status"] == "success":

            cost_text = (
                f"¥{result['cost']:.6f}"
                if result["cost"] is not None
                else "subscription"
            )

            print(
                f"Model: {result['model']} | "
                f"Latency: {result['latency']}s | "
                f"Tokens: {result['total_tokens']} | "
                f"Cost: {cost_text}"
            )

        else:
            print(f"Failed: {result['error']}")