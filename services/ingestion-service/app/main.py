import asyncio
from contextlib import suppress
from datetime import UTC, datetime

from fastapi import FastAPI
from pydantic import BaseModel

from myet_shared.config import INGEST_REFRESH_MINUTES, RSS_FEEDS
from myet_shared.ingestion import fetch_rss_articles
from myet_shared.repository import SharedRepository


class IngestionEvent(BaseModel):
    event_type: str
    article_id: str
    published_at: str
    category: str
    source: str


class BatchIngestionResponse(BaseModel):
    total_articles: int
    categories: list[str]
    events: list[IngestionEvent]


repository = SharedRepository()
app = FastAPI(title="MyET Ingestion Service", version="2.0.0")
refresh_task: asyncio.Task | None = None


async def refresh_articles() -> int:
    try:
        articles = await asyncio.to_thread(fetch_rss_articles, RSS_FEEDS)
        repository.upsert_articles(articles)
        return len(articles)
    except Exception:
        return 0


async def refresh_loop() -> None:
    while True:
        await refresh_articles()
        await asyncio.sleep(INGEST_REFRESH_MINUTES * 60)


@app.on_event("startup")
async def startup() -> None:
    global refresh_task
    await refresh_articles()
    refresh_task = asyncio.create_task(refresh_loop())


@app.on_event("shutdown")
async def shutdown() -> None:
    global refresh_task
    if refresh_task:
        refresh_task.cancel()
        with suppress(asyncio.CancelledError):
            await refresh_task


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "ingestion-service"}


@app.get("/ingest/batch", response_model=BatchIngestionResponse)
async def batch_ingest() -> BatchIngestionResponse:
    articles = repository.load_articles()
    categories = sorted({article.category for article in articles})
    events = [
        IngestionEvent(
            event_type="article.ingested",
            article_id=article.id,
            published_at=article.published_at,
            category=article.category,
            source=article.source,
        )
        for article in articles
    ]
    return BatchIngestionResponse(total_articles=len(articles), categories=categories, events=events)


@app.get("/ingest/stream-preview")
async def stream_preview() -> dict[str, object]:
    articles = repository.load_articles()[:5]
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "topic": "article.ingested",
        "messages": [
            {
                "key": article.id,
                "value": {
                    "title": article.title,
                    "category": article.category,
                    "entities": article.entities,
                    "url": article.url,
                },
            }
            for article in articles
        ],
    }


@app.post("/ingest/normalize")
async def normalize_payload(payload: dict[str, object]) -> dict[str, object]:
    normalized = {str(key).lower().strip(): value for key, value in payload.items()}
    normalized["normalized_at"] = datetime.now(UTC).isoformat()
    return normalized
