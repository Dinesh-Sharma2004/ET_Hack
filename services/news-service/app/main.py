from datetime import UTC, datetime

from fastapi import FastAPI, Query

from myet_shared.nlp import parse_datetime
from myet_shared.repository import SharedRepository


repository = SharedRepository()
app = FastAPI(title="MyET News Service", version="2.0.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "news-service"}


@app.get("/news")
async def get_news(
    category: str | None = None,
    stock: str | None = None,
    interest: str | None = None,
    search: str | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=20),
) -> dict[str, object]:
    articles = repository.search_articles(category=category, stock=stock, interest=interest, search=search)
    page = [article.model_dump() for article in articles[offset : offset + limit]]
    return {
        "items": page,
        "total": len(articles),
        "offset": offset,
        "limit": limit,
        "highlights": [
            {"label": "Stories indexed", "value": str(len(articles)), "delta": "live"},
            {"label": "Industries", "value": str(len({article.category for article in articles})), "delta": "active"},
            {"label": "Fresh in 24h", "value": str(sum(1 for article in articles if (datetime.now(UTC) - parse_datetime(article.published_at)).days < 1)), "delta": "dynamic"},
        ],
        "trending_topics": sorted({entity for article in articles for entity in article.entities})[:10],
    }


@app.get("/news/dashboard")
async def get_dashboard() -> dict[str, object]:
    articles = repository.load_articles()
    profile = repository.load_profile()
    trending = [article.model_dump() for article in sorted(articles, key=lambda item: item.sentiment, reverse=True)[:3]]
    return {
        "profile": profile.model_dump(),
        "highlights": [
            {"label": "Market Pulse", "value": "Real-time RSS", "delta": "live"},
            {"label": "Tracked Sectors", "value": str(len(profile.sectors)), "delta": "+dynamic"},
            {"label": "Stories available", "value": str(len(articles)), "delta": "rolling"},
        ],
        "trending": trending,
    }
