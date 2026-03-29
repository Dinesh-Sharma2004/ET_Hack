import hashlib
import re
from email.utils import parsedate_to_datetime

import feedparser
import requests

from myet_shared.models import Article
from myet_shared.nlp import classify_category, compute_sentiment, estimate_read_time, extract_entities


BUSINESS_URL_KEYWORDS = (
    "/markets/",
    "/tech/",
    "/startup",
    "/startups/",
    "/funding/",
    "/industry/",
    "/news/company/",
    "/wealth/",
    "/mf/",
    "/mutual-funds/",
    "/small-biz/",
    "/economy/",
    "/policy/",
    "/prime/economy-and-policy/",
)

BUSINESS_TEXT_KEYWORDS = (
    "market",
    "markets",
    "stock",
    "stocks",
    "investor",
    "investors",
    "economy",
    "economic",
    "business",
    "finance",
    "financial",
    "bank",
    "banking",
    "startup",
    "funding",
    "merger",
    "acquisition",
    "ipo",
    "mutual fund",
    "policy",
    "inflation",
    "rupee",
    "trade",
    "company",
    "companies",
    "revenue",
    "profit",
    "earnings",
    "layoff",
    "manufacturing",
    "energy",
    "telecom",
    "technology",
)

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
    )
}


def _clean_html(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value or "").replace("&nbsp;", " ").strip()


def _is_business_relevant(title: str, summary: str, content: str, url: str | None) -> bool:
    lowered_url = (url or "").lower()
    if any(keyword in lowered_url for keyword in BUSINESS_URL_KEYWORDS):
        return True
    blob = f"{title} {summary} {content}".lower()
    return sum(1 for keyword in BUSINESS_TEXT_KEYWORDS if keyword in blob) >= 2


def fetch_rss_articles(feed_urls: list[str]) -> list[Article]:
    articles: list[Article] = []
    seen_ids: set[str] = set()
    for feed_url in feed_urls:
        response = requests.get(feed_url, headers=REQUEST_HEADERS, timeout=30)
        response.raise_for_status()
        feed = feedparser.parse(response.text)
        source = getattr(feed.feed, "title", None) or feed_url
        for entry in getattr(feed, "entries", []):
            title = getattr(entry, "title", "").strip()
            summary = _clean_html(getattr(entry, "summary", ""))
            content_parts = []
            for item in getattr(entry, "content", []) or []:
                value = item.get("value")
                if value:
                    content_parts.append(_clean_html(value))
            content = " ".join(content_parts) or summary or title
            url = getattr(entry, "link", None)
            identifier = hashlib.sha1(f"{title}|{url}|{summary}".encode("utf-8")).hexdigest()
            if not title or identifier in seen_ids:
                continue
            if not _is_business_relevant(title, summary, content, url):
                continue
            seen_ids.add(identifier)
            published_at = getattr(entry, "published", None) or getattr(entry, "updated", None)
            if published_at:
                try:
                    published_at = parsedate_to_datetime(published_at).isoformat()
                except (TypeError, ValueError):
                    pass
            article_text = f"{title}. {summary}. {content}"
            articles.append(
                Article(
                    id=identifier,
                    title=title,
                    summary=summary or title,
                    content=content,
                    category=classify_category(article_text),
                    entities=extract_entities(article_text),
                    sentiment=compute_sentiment(article_text),
                    language="English",
                    published_at=str(published_at or ""),
                    source=source,
                    read_time_minutes=estimate_read_time(content),
                    url=url,
                    image_url=None,
                )
            )
    return articles
