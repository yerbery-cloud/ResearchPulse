import feedparser

from config import rss_sources
from filter import calculate_score, get_tags


def collect_articles(limit=10):
    articles = []
    seen_ids = set()

    raw_count = 0

    for url in rss_sources:
        feed = feedparser.parse(url)

        print(f"Reading: {feed.feed.title}")

        for entry in feed.entries[:limit]:
            raw_count += 1

            article_id = entry.get(
                "id",
                entry.get("link", "")
            )

            if article_id in seen_ids:
                continue

            seen_ids.add(article_id)

            title = entry.get("title", "").strip()
            summary = entry.get("summary", "").strip()

            score = calculate_score(title, summary)

            if score == 0:
                continue

            tags = get_tags(title, summary)

            article = {
                "id": article_id,
                "title": title,
                "published": entry.get("published", "Unknown"),
                "link": entry.get("link", ""),
                "summary": summary,
                "source": feed.feed.get("title", "Unknown"),
                "score": score,
                "tags": tags,
            }

            articles.append(article)

    articles.sort(
        key=lambda article: article["score"],
        reverse=True
    )

    return articles, raw_count