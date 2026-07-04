"""Score sentiment for a list of article dicts.

TextBlob is used because it needs no model download and no API key -
good enough for a learning project. Swap in a HuggingFace pipeline later
if you want to level this project up.
"""
from __future__ import annotations

from textblob import TextBlob


def _label(polarity: float) -> str:
    if polarity > 0.1:
        return "positive"
    if polarity < -0.1:
        return "negative"
    return "neutral"


def analyze_articles(articles: list[dict]) -> list[dict]:
    """Add sentiment_polarity, sentiment_subjectivity, sentiment_label to each article."""
    scored = []

    for article in articles:
        blob = TextBlob(article["title"])
        polarity = round(blob.sentiment.polarity, 4)
        subjectivity = round(blob.sentiment.subjectivity, 4)

        scored.append(
            {
                **article,
                "sentiment_polarity": polarity,
                "sentiment_subjectivity": subjectivity,
                "sentiment_label": _label(polarity),
            }
        )

    return scored


if __name__ == "__main__":
    sample = [{"title": "Markets rally as inflation fears ease", "link": "x", "source": "test", "published_at": None}]
    print(analyze_articles(sample))
