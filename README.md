# News Sentiment Pipeline (Airflow)

A daily ETL pipeline that pulls headlines from RSS feeds, scores their
sentiment, and stores the results in Postgres — orchestrated end-to-end
with Apache Airflow, running entirely on Docker with no paid services.

## Architecture

```
RSS Feeds  --->  fetch()  --->  analyze()  --->  load()  --->  Postgres
(BBC, NPR..)     Airflow task   Airflow task    Airflow task   (sentiment_data)
```

- **Orchestration:** Apache Airflow 2.9 (LocalExecutor), TaskFlow API
- **Extraction:** `feedparser` reading public RSS feeds
- **Sentiment scoring:** `TextBlob` (polarity + subjectivity -> label)
- **Storage:** Postgres (separate container from Airflow's own metadata DB)
- **Infra:** Docker Compose — everything runs locally, $0 cost

## Project structure

```
.
├── dags/
│   └── news_sentiment_dag.py   # the Airflow DAG (fetch -> analyze -> load -> transform)
├── scripts/
│   ├── fetch_news.py           # RSS extraction (with per-feed timeout)
│   ├── analyze_sentiment.py    # sentiment scoring
│   └── db_utils.py             # Postgres write helper
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/
│       │   ├── sources.yml
│       │   └── stg_news_sentiment.sql
│       └── marts/
│           ├── mart_sentiment_by_source.sql
│           └── mart_daily_sentiment_trend.sql
├── dashboard/
│   ├── app.py                  # Streamlit dashboard
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yaml         # Airflow + 2 Postgres + dashboard containers
├── Dockerfile                  # custom Airflow image with our Python deps + dbt baked in
├── init_db.sql                 # creates the news_sentiment table
├── requirements.txt
└── .env.example
```

## The dbt layer

After `load` writes raw rows into `news_sentiment`, the DAG's `transform`
task runs `dbt run`, which builds:

- **`stg_news_sentiment`** (view) — a lightly cleaned pass over the raw table
- **`mart_sentiment_by_source`** (table) — article counts and average
  polarity/subjectivity per source and label
- **`mart_daily_sentiment_trend`** (table) — daily counts per source and
  label, ready for a trend chart

This is the same "raw → staging → mart" layering used in real dbt
projects, just small enough to read end-to-end in a few minutes.

## Running it

1. Copy the env file and set your UID (Linux/macOS):
   ```bash
   cp .env.example .env
   echo "AIRFLOW_UID=$(id -u)" > .env
   ```
   On Windows, just leave `.env.example`'s default (`50000`) as `.env`.

2. Start everything:
   ```bash
   docker compose build
   docker compose up airflow-init
   docker compose up -d
   ```

3. Open the Airflow UI at [http://localhost:8081](http://localhost:8081)
   (user: `airflow`, password: `airflow`) and unpause the
   `news_sentiment_pipeline` DAG, or trigger it manually.

4. Open the dashboard at [http://localhost:8501](http://localhost:8501)
   to see sentiment breakdowns, a polarity histogram, and the latest
   headlines table. It refreshes from Postgres every 60 seconds.

5. Or inspect the results directly via SQL:
   ```bash
   docker compose exec sentiment-postgres psql -U sentiment -d sentiment_data \
     -c "SELECT source, sentiment_label, COUNT(*) FROM news_sentiment GROUP BY 1,2;"
   ```
   Or query the dbt marts once `transform` has run at least once:
   ```bash
   docker compose exec sentiment-postgres psql -U sentiment -d sentiment_data \
     -c "SELECT * FROM mart_sentiment_by_source;"
   ```

## Why this project

Demonstrates a full, small-scale data engineering loop: extraction from
an external source, a transformation step (NLP scoring), idempotent
loading (duplicates skipped via `ON CONFLICT`), and scheduling/monitoring
through Airflow — without needing any cloud account or paid API key.

## Possible extensions

- Swap TextBlob for a HuggingFace sentiment model for better accuracy
- Add `dbt test` (e.g. `not_null`, `accepted_values` on `sentiment_label`) for data quality
- Add more RSS sources (Al Jazeera, The Guardian, DW) for broader coverage
- Add Slack/email alerting on DAG failure via Airflow callbacks
- Deploy the dashboard somewhere public (Streamlit Community Cloud, Render) for a live portfolio link
