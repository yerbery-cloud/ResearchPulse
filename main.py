import json

from collector import collect_articles
from database import save_to_database, get_top_articles, search_articles


articles, raw_count = collect_articles(limit=10)

with open("data/articles.json", "w", encoding="utf-8") as f:
    json.dump(
        articles,
        f,
        ensure_ascii=False,
        indent=2
    )

save_to_database(articles)


print()
print(f"Raw articles: {raw_count}")
print(f"Relevant articles: {len(articles)}")


top_articles = get_top_articles(5)

print("\n=== Top Articles ===")

for title, score, link in top_articles:
    print(f"[{score}] {title}")
    print(link)
    print()


keyword = input("Search keyword: ")

results = search_articles(keyword)

print(f"\n=== Search Results: {keyword} ===")

for title, score, link in results:
    print(f"[{score}] {title}")
    print(link)
    print()