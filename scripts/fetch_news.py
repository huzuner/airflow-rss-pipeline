"""Fetch articles from a set of RSS feeds.

Kept dependency-light on purpose: feedparser handles the RSS/Atom parsing,
we just normalize the fields we care about.
"""
from __future__ import annotations

from datetime import datetime
from time import mktime
import feedparser

# Add / remove feeds here. All of these are free, no API key required.
RSS_FEEDS = {
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Reuters World": "https://www.reutersagency.com/feed/?best-topics=world",
    "NPR News": "https://feeds.npr.org/1001/rss.xml",
}


def fetch_articles(feeds: dict[str, str] = RSS_FEEDS) -> list[dict]:
    """Return a flat list of article dicts: source, title, link, published_at."""
    articles = []

    for source_name, url in feeds.items():
        parsed = feedparser.parse(url)

        for entry in parsed.entries:
            published_at = None
            if getattr(entry, "published_parsed", None):
                published_at = datetime.fromtimestamp(
                    mktime(entry.published_parsed)
                ).isoformat()

            articles.append(
                {
                    "source": source_name,
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", "").strip(),
                    "published_at": published_at,
                }
            )

    return articles


if __name__ == "__main__":
    # Quick manual test: `python scripts/fetch_news.py`
    for a in fetch_articles()[:5]:
        print(a)
