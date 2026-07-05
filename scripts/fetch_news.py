"""Fetch articles from a set of RSS feeds.

Kept dependency-light on purpose: feedparser handles the RSS/Atom parsing,
we just normalize the fields we care about.
"""
from __future__ import annotations

from datetime import datetime
from time import mktime

import feedparser
import requests

# Add / remove feeds here. All of these are free, no API key required.
RSS_FEEDS = {
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "NPR News": "https://feeds.npr.org/1001/rss.xml",
}

# Seconds to wait for a single feed before giving up on it.
REQUEST_TIMEOUT = 10


def _fetch_one_feed(source_name: str, url: str) -> list[dict]:
    """Fetch and parse a single feed. Never raises - logs and returns [] on failure,
    so one broken/slow feed can't block the others or hang the whole task."""
    try:
        # requests enforces the timeout; feedparser.parse() alone does not.
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        parsed = feedparser.parse(response.content)
    except Exception as e:
        print(f"[WARN] Skipping '{source_name}' ({url}): {e}")
        return []

    articles = []
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


def fetch_articles(feeds: dict[str, str] = RSS_FEEDS) -> list[dict]:
    """Return a flat list of article dicts: source, title, link, published_at."""
    articles = []
    for source_name, url in feeds.items():
        articles.extend(_fetch_one_feed(source_name, url))
    return articles


if __name__ == "__main__":
    # Quick manual test: `python scripts/fetch_news.py`
    for a in fetch_articles()[:5]:
        print(a)

