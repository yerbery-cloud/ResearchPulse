import feedparser
import time
import requests

from config import rss_sources
from filter import calculate_score, get_tags

def fetch_feed(url, retries=3, timeout=15):
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers={
                    "User-Agent": "ResearchPulse/0.1"
                }
            )

            response.raise_for_status()

            return feedparser.parse(response.content)

        except requests.RequestException as e:
            print(
                f"Attempt {attempt}/{retries} failed: "
                f"{url}\nReason: {e}"
            )

            if attempt < retries:
                time.sleep(2 * attempt)

    return None


def collect_articles(limit=10):
    articles = []
    seen_ids = set()

    raw_count = 0

    for url in rss_sources:
        feed = fetch_feed(url)

        if feed is None:
            print(f"Skip: {url}\n")
            continue

        if feed.bozo:
            print(f"Warning: failed to parse {url}")
            print(f"Reason: {feed.bozo_exception}")

        feed_title = feed.feed.get("title", url)
        print(f"Reading: {feed_title}")

        if not feed.entries:
            print(f"Warning: no entries found from {url}")
            continue

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