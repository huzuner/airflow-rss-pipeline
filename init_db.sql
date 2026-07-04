CREATE TABLE IF NOT EXISTS news_sentiment (
    id SERIAL PRIMARY KEY,
    source VARCHAR(150) NOT NULL,
    title TEXT NOT NULL,
    link TEXT UNIQUE NOT NULL,
    published_at TIMESTAMP,
    sentiment_polarity FLOAT,
    sentiment_subjectivity FLOAT,
    sentiment_label VARCHAR(20),
    fetched_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_news_sentiment_source ON news_sentiment (source);
CREATE INDEX IF NOT EXISTS idx_news_sentiment_label ON news_sentiment (sentiment_label);
