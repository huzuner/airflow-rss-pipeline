"""Streamlit dashboard for the news sentiment pipeline.

Reads directly from the sentiment-postgres database that the Airflow
DAG writes to, and shows a few simple views: overall breakdown by
source/sentiment, a trend over time, and the latest headlines.
"""
import os

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="News Sentiment Dashboard", layout="wide")

DB_CONFIG = {
    "host": os.environ.get("SENTIMENT_DB_HOST", "sentiment-postgres"),
    "port": os.environ.get("SENTIMENT_DB_PORT", "5432"),
    "dbname": os.environ.get("SENTIMENT_DB_NAME", "sentiment_data"),
    "user": os.environ.get("SENTIMENT_DB_USER", "sentiment"),
    "password": os.environ.get("SENTIMENT_DB_PASSWORD", "sentiment"),
}


@st.cache_resource
def get_engine():
    url = (
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    )
    return create_engine(url)


@st.cache_data(ttl=60)
def load_data() -> pd.DataFrame:
    engine = get_engine()
    query = """
        SELECT source, title, link, published_at, sentiment_polarity,
               sentiment_subjectivity, sentiment_label, fetched_at
        FROM news_sentiment
        ORDER BY fetched_at DESC
    """
    return pd.read_sql(query, engine)


st.title("📰 News Sentiment Dashboard")
st.caption("Data collected daily by an Airflow pipeline: RSS feeds → sentiment scoring → Postgres")

df = load_data()

if df.empty:
    st.warning("No data yet. Trigger the Airflow DAG at least once, then refresh this page.")
    st.stop()

# --- Top-line metrics ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total articles", len(df))
col2.metric("Sources", df["source"].nunique())
col3.metric("Positive %", f"{(df['sentiment_label'] == 'positive').mean() * 100:.0f}%")
col4.metric("Negative %", f"{(df['sentiment_label'] == 'negative').mean() * 100:.0f}%")

st.divider()

# --- Sidebar filters ---
sources = st.sidebar.multiselect("Filter by source", options=sorted(df["source"].unique()), default=list(df["source"].unique()))
filtered = df[df["source"].isin(sources)]

# --- Breakdown by source and sentiment ---
left, right = st.columns(2)

with left:
    st.subheader("Sentiment by source")
    counts = filtered.groupby(["source", "sentiment_label"]).size().reset_index(name="count")
    fig = px.bar(
        counts, x="source", y="count", color="sentiment_label",
        barmode="group",
        color_discrete_map={"positive": "#2ca02c", "neutral": "#7f7f7f", "negative": "#d62728"},
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Overall sentiment mix")
    label_counts = filtered["sentiment_label"].value_counts().reset_index()
    label_counts.columns = ["sentiment_label", "count"]
    fig2 = px.pie(
        label_counts, names="sentiment_label", values="count",
        color="sentiment_label",
        color_discrete_map={"positive": "#2ca02c", "neutral": "#7f7f7f", "negative": "#d62728"},
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Polarity distribution ---
st.subheader("Polarity distribution")
fig3 = px.histogram(filtered, x="sentiment_polarity", nbins=20, color="source")
st.plotly_chart(fig3, use_container_width=True)

# --- Latest headlines table ---
st.subheader("Latest headlines")
display_df = filtered[["source", "title", "sentiment_label", "sentiment_polarity", "published_at"]].head(50)
st.dataframe(display_df, use_container_width=True, hide_index=True)
