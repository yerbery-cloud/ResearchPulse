import json
import sqlite3


DB_PATH = "data/researchpulse.db"


def save_to_database(articles):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT,
                published TEXT,
                link TEXT,
                summary TEXT,
                source TEXT,
                score INTEGER,
                tags TEXT
            )
        """)

        for article in articles:
            cursor.execute("""
                INSERT OR IGNORE INTO articles
                (id, title, published, link, summary, source, score, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article["id"],
                article["title"],
                article["published"],
                article["link"],
                article["summary"],
                article["source"],
                article["score"],
                json.dumps(article["tags"], ensure_ascii=False)
            ))

        conn.commit()


def get_top_articles(limit=5):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT title, score, link
            FROM articles
            ORDER BY score DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()


def search_articles(keyword, limit=10):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        pattern = f"%{keyword}%"

        cursor.execute("""
            SELECT title, score, link
            FROM articles
            WHERE title LIKE ?
               OR summary LIKE ?
            ORDER BY score DESC
            LIMIT ?
        """, (pattern, pattern, limit))

        return cursor.fetchall()