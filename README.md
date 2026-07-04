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
│   └── news_sentiment_dag.py   # the Airflow DAG (fetch -> analyze -> load)
├── scripts/
│   ├── fetch_news.py           # RSS extraction
│   ├── analyze_sentiment.py    # sentiment scoring
│   └── db_utils.py             # Postgres write helper
├── docker-compose.yaml         # Airflow + two Postgres containers
├── init_db.sql                 # creates the news_sentiment table
├── requirements.txt            # for running scripts locally / IDE autocomplete
└── .env.example
```

## Running it

1. Copy the env file and set your UID (Linux/macOS):
   ```bash
   cp .env.example .env
   echo "AIRFLOW_UID=$(id -u)" > .env
   ```
   On Windows, just leave `.env.example`'s default (`50000`) as `.env`.

2. Start everything:
   ```bash
   docker compose up airflow-init
   docker compose up
   ```

3. Open the Airflow UI at [http://localhost:8080](http://localhost:8080)
   (user: `airflow`, password: `airflow`) and unpause the
   `news_sentiment_pipeline` DAG, or trigger it manually.

4. Inspect the results:
   ```bash
   docker exec -it sentiment-pipeline-sentiment-postgres-1 \
     psql -U sentiment -d sentiment_data -c "SELECT source, sentiment_label, COUNT(*) FROM news_sentiment GROUP BY 1,2;"
   ```

## Why this project

Demonstrates a full, small-scale data engineering loop: extraction from
an external source, a transformation step (NLP scoring), idempotent
loading (duplicates skipped via `ON CONFLICT`), and scheduling/monitoring
through Airflow — without needing any cloud account or paid API key.

## Possible extensions

- Swap TextBlob for a HuggingFace sentiment model for better accuracy
- Add a `dbt` layer on top of `news_sentiment` for aggregated marts
- Add a Great Expectations / Soda data-quality check task
- Visualize trends with a small Streamlit or Metabase dashboard
- Add Slack/email alerting on DAG failure via Airflow callbacks
