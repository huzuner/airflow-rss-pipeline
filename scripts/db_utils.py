"""Small helper around psycopg2 for writing scored articles to Postgres."""
from __future__ import annotations

import os
import psycopg2
from psycopg2.extras import execute_values

DB_CONFIG = {
    "host": os.environ.get("SENTIMENT_DB_HOST", "sentiment-postgres"),
    "port": os.environ.get("SENTIMENT_DB_PORT", "5432"),
    "dbname": os.environ.get("SENTIMENT_DB_NAME", "sentiment_data"),
    "user": os.environ.get("SENTIMENT_DB_USER", "sentiment"),
    "password": os.environ.get("SENTIMENT_DB_PASSWORD", "sentiment"),
}

INSERT_QUERY = """
    INSERT INTO news_sentiment
        (source, title, link, published_at, sentiment_polarity, sentiment_subjectivity, sentiment_label)
    VALUES %s
    ON CONFLICT (link) DO NOTHING
"""


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def save_articles(articles: list[dict]) -> int:
    """Bulk insert, skipping articles whose link already exists. Returns rows inserted."""
    if not articles:
        return 0

    rows = [
        (
            a["source"],
            a["title"],
            a["link"],
            a["published_at"],
            a["sentiment_polarity"],
            a["sentiment_subjectivity"],
            a["sentiment_label"],
        )
        for a in articles
    ]

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            execute_values(cur, INSERT_QUERY, rows)
            inserted = cur.rowcount
        conn.commit()
        return inserted
    finally:
        conn.close()
