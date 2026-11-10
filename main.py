import json

from collector import collect_articles
from database import save_to_database, get_top_articles, search_articles
from summarizer import summarize_article
from database import(
    save_to_database,
    get_articles_without_summary,
    get_top_articles,
    search_articles,
    update_ai_summary,
    save_benchmark_result,
)
from benchmark import (
    get_benchmark_summary,
    get_quality_summary,
)
def main():

    articles, raw_count = collect_articles(limit=10)

    with open("data/articles.json", "w", encoding="utf-8") as f:
        json.dump(
            articles,
            f,
            ensure_ascii=False,
            indent=2
        )

    save_to_database(articles)

    pending_articles = get_articles_without_summary(limit = 1)

    print("\n=== Generating Summaries ===")

    for article_id, title, abstract in pending_articles:
        result = summarize_article(title, abstract)

        update_ai_summary(
            article_id,
            result
        )
        save_benchmark_result(
            article_id,
            result,
            provider="DeepSeek",
            precision="API"
        )

        if result["status"] == "success":
            print(f"Summarized: {title}")
            print(
                f"Model: {result['model']} | "
                f"Latency: {result['latency']}s | "
                f"Tokens: {result['total_tokens']} | "
                f"Cost: ¥{result['cost']:.6f}"
            )
        else:
            print(f"Failed: {title}")
            print(f"Error: {result['error']}")

    print()
    print(f"Raw articles: {raw_count}")
    print(f"Relevant articles: {len(articles)}")


    top_articles = get_top_articles(5)

    print("\n=== Top Articles ===")

    for title, score, link in top_articles:
        print(f"[{score}] {title}")
        print(link)
        print()


    # Benchmark 统计
    benchmark_summary = get_benchmark_summary()

    print("\n=== Benchmark Summary ===")

    for (
        provider,
        model,
        precision,
        runs,
        avg_latency,
        avg_tokens,
        avg_cost
    ) in benchmark_summary:

        if avg_cost is None:
            cost_text = "subscription"
        else:
            cost_text = f"¥{avg_cost:.6f}"

        print(
            f"{provider} | {model} | {precision}\n"
            f"Runs: {runs} | "
            f"Latency: {avg_latency:.3f}s | "
            f"Tokens: {avg_tokens:.1f} | "
            f"Cost: {cost_text}\n"
        )

    quality_summary = get_quality_summary()

    print("\n=== Quality Summary ===")

    for (
        provider,
        model,
        evaluations,
        faithfulness,
        coverage,
        conciseness,
        usefulness,
        overall
    ) in quality_summary:

        print(
            f"{provider} | {model}\n"
            f"Evaluations: {evaluations} | "
            f"Faithfulness: {faithfulness:.2f} | "
            f"Coverage: {coverage:.2f} | "
            f"Conciseness: {conciseness:.2f} | "
            f"Usefulness: {usefulness:.2f} | "
            f"Overall: {overall:.2f}\n"
        )
    # 搜索
    keyword = input("Search keyword: ")

    results = search_articles(keyword)

    print(f"\n=== Search Results: {keyword} ===")

    for title, score, link in results:
        print(f"[{score}] {title}")
        print(link)
        print()

if __name__ == "__main__":
    main()