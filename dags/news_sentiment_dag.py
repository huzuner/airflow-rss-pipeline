"""
News Sentiment Pipeline
========================
Daily DAG that:
  1. Pulls fresh articles from a handful of RSS feeds
  2. Scores each headline's sentiment (positive / negative / neutral)
  3. Loads the results into Postgres, skipping duplicates

This uses Airflow's TaskFlow API (@dag / @task), the modern, Pythonic
way to write DAGs instead of manually wiring PythonOperator instances.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator

# Make our scripts/ folder importable inside the Airflow containers
import sys
sys.path.append("/opt/airflow/scripts")

default_args = {
    "owner": "you",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="news_sentiment_pipeline",
    description="Fetch RSS news, score sentiment, load into Postgres",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["sentiment", "portfolio", "etl"],
)
def news_sentiment_pipeline():

    @task
    def fetch():
        from fetch_news import fetch_articles
        return fetch_articles()

    @task
    def analyze(articles: list[dict]):
        from analyze_sentiment import analyze_articles
        return analyze_articles(articles)

    @task
    def load(scored_articles: list[dict]):
        from db_utils import save_articles
        inserted = save_articles(scored_articles)
        print(f"Inserted {inserted} new rows (duplicates skipped).")
        return inserted

    # Task dependencies are implicit here because each function's output
    # is passed as the next function's input (TaskFlow wires the XComs for you)
    raw_articles = fetch()
    scored_articles = analyze(raw_articles)
    rows_loaded = load(scored_articles)

    transform = BashOperator(
        task_id="transform",
        bash_command="""
            set -euo pipefail

            cd /opt/airflow/dbt

            dbt deps
            dbt run \
                --profiles-dir . \
                --project-dir .
        """,
    )

    rows_loaded >> transform


news_sentiment_pipeline()