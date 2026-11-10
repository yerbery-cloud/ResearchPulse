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
                tags TEXT,
                ai_summary TEXT,
                ai_model TEXT,
                ai_latency REAL,
                ai_status TEXT,
                ai_error TEXT,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                ai_cost REAL
            )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS benchmark_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            article_id TEXT,

            provider TEXT,
            model TEXT,
            precision TEXT,

            latency REAL,

            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER,

            cost REAL,

            status TEXT,
            error TEXT,

            output_summary TEXT
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
        cursor.execute("""
    CREATE TABLE IF NOT EXISTS quality_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        benchmark_id INTEGER,

        faithfulness REAL,
        coverage REAL,
        conciseness REAL,
        usefulness REAL,

        overall_score REAL,

        evaluator TEXT,
        notes TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (benchmark_id)
            REFERENCES benchmark_results(id)
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


def get_articles_without_summary(limit=5):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title, summary
            FROM articles
            WHERE ai_summary IS NULL
            ORDER BY score DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()

def update_ai_summary(article_id, result):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE articles
            SET ai_summary = ?,
                ai_model = ?,
                ai_latency = ?,
                ai_status = ?,
                ai_error = ?,
                prompt_tokens = ?,
                cache_hit_tokens = ?,
                cache_miss_tokens = ?,
                completion_tokens = ?,
                total_tokens = ?,
                ai_cost = ?
            WHERE id = ?
        """, (
            result["summary"],
            result["model"],
            result["latency"],
            result["status"],
            result["error"],
            result["prompt_tokens"],
            result.get("cache_hit_tokens", 0),
            result.get("cache_miss_tokens", 0),
            result["completion_tokens"],
            result["total_tokens"],
            result["cost"],
            article_id
        ))

        conn.commit()

def save_benchmark_result(
        article_id,
        result,
        provider,
        precision="API"
):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO benchmark_results (
                article_id,
                provider,
                model,
                precision,
                latency,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                cost,
                status,
                error,
                output_summary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,(
            article_id,
            provider,
            result["model"],
            precision,
            result["latency"],
            result["prompt_tokens"],
            result["completion_tokens"],
            result["total_tokens"],
            result["cost"],
            result["status"],
            result["error"],
            result["summary"]
        )

        )

        conn.commit()

def save_quality_evaluation(
    benchmark_id,
    faithfulness,
    coverage,
    conciseness,
    usefulness,
    overall_score,
    evaluator="human",
    notes=""
):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO quality_evaluations (
                benchmark_id,
                faithfulness,
                coverage,
                conciseness,
                usefulness,
                overall_score,
                evaluator,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            benchmark_id,
            faithfulness,
            coverage,
            conciseness,
            usefulness,
            overall_score,
            evaluator,
            notes
        ))

        conn.commit()

def get_unevaluated_benchmarks(limit=6):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                b.id,
                a.title,
                a.summary,
                b.provider,
                b.model,
                b.output_summary
            FROM benchmark_results b
            JOIN articles a
                ON b.article_id = a.id
            LEFT JOIN quality_evaluations q
                ON b.id = q.benchmark_id
            WHERE b.status = 'success'
              AND b.output_summary IS NOT NULL
              AND q.id IS NULL
            ORDER BY b.id ASC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()

def get_blind_eval_pairs(limit=3):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                a.title,
                a.summary,

                d.id,
                d.provider,
                d.model,
                d.output_summary,

                m.id,
                m.provider,
                m.model,
                m.output_summary

            FROM articles a

            JOIN benchmark_results d
                ON d.article_id = a.id
                AND d.provider = 'deepseek'
                AND d.status = 'success'
                AND d.output_summary IS NOT NULL

            JOIN benchmark_results m
                ON m.article_id = a.id
                AND m.provider = 'minimax'
                AND m.status = 'success'
                AND m.output_summary IS NOT NULL

            WHERE d.id = (
                SELECT MAX(d2.id)
                FROM benchmark_results d2
                WHERE d2.article_id = a.id
                  AND d2.provider = 'deepseek'
                  AND d2.status = 'success'
                  AND d2.output_summary IS NOT NULL
            )

            AND m.id = (
                SELECT MAX(m2.id)
                FROM benchmark_results m2
                WHERE m2.article_id = a.id
                  AND m2.provider = 'minimax'
                  AND m2.status = 'success'
                  AND m2.output_summary IS NOT NULL
            )

            AND NOT EXISTS (
                SELECT 1
                FROM quality_evaluations q
                WHERE q.benchmark_id = d.id
                  AND q.evaluator = 'human_blind_v2'
            )

            AND NOT EXISTS (
                SELECT 1
                FROM quality_evaluations q
                WHERE q.benchmark_id = m.id
                  AND q.evaluator = 'human_blind_v2'
            )

            ORDER BY a.score DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()

def get_human_blind_pairs(limit=3):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                a.title,
                a.summary,

                d.id,
                d.output_summary,

                m.id,
                m.output_summary

            FROM articles a

            JOIN benchmark_results d
                ON d.article_id = a.id
                AND d.provider = 'deepseek'

            JOIN benchmark_results m
                ON m.article_id = a.id
                AND m.provider = 'minimax'

            WHERE EXISTS (
                SELECT 1
                FROM quality_evaluations q
                WHERE q.benchmark_id = d.id
                  AND q.evaluator = 'human_blind_v2'
            )

            AND EXISTS (
                SELECT 1
                FROM quality_evaluations q
                WHERE q.benchmark_id = m.id
                  AND q.evaluator = 'human_blind_v2'
            )

            ORDER BY a.score DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()

def quality_evaluation_exists(benchmark_id, evaluator):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 1
            FROM quality_evaluations
            WHERE benchmark_id = ?
              AND evaluator = ?
            LIMIT 1
        """, (
            benchmark_id,
            evaluator
        ))

        return cursor.fetchone() is not None