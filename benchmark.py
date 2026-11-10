import sqlite3


DB_PATH = "data/researchpulse.db"


def get_benchmark_summary():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                provider,
                model,
                precision,
                COUNT(*) AS runs,
                AVG(latency) AS avg_latency,
                AVG(total_tokens) AS avg_tokens,
                AVG(cost) AS avg_cost
            FROM benchmark_results
            WHERE status = 'success'
            GROUP BY provider, model, precision
        """)

        return cursor.fetchall()

def get_quality_summary():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                b.provider,
                b.model,
                COUNT(q.id) AS evaluations,
                AVG(q.faithfulness),
                AVG(q.coverage),
                AVG(q.conciseness),
                AVG(q.usefulness),
                AVG(q.overall_score)
            FROM quality_evaluations q
            JOIN benchmark_results b
                ON q.benchmark_id = b.id
            GROUP BY b.provider, b.model
        """)

        return cursor.fetchall()

def get_evaluation_comparison():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                q.evaluator,
                b.provider,
                b.model,

                COUNT(q.id) AS evaluations,

                AVG(q.faithfulness),
                AVG(q.coverage),
                AVG(q.conciseness),
                AVG(q.usefulness),
                AVG(q.overall_score)

            FROM quality_evaluations q

            JOIN benchmark_results b
                ON q.benchmark_id = b.id
                
            WHERE q.evaluator LIKE '%_v2'

            GROUP BY
                q.evaluator,
                b.provider,
                b.model

            ORDER BY
                q.evaluator,
                b.provider
        """)

        return cursor.fetchall()