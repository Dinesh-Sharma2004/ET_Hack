from fastapi import FastAPI
from pydantic import BaseModel

from myet_shared.explainability import RecommendationExplainer
from myet_shared.personalization import PersonalizationEngine
from myet_shared.repository import SharedRepository


class FeedRequest(BaseModel):
    industry: str | None = None
    stock: str | None = None
    interest: str | None = None


repository = SharedRepository()
ranker = PersonalizationEngine()
explainer = RecommendationExplainer()
app = FastAPI(title="MyET Recommendations Service", version="2.0.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "recommendations-service"}


@app.post("/recommendations")
async def get_recommendations(payload: FeedRequest) -> dict[str, object]:
    profile = repository.load_profile()
    articles = repository.search_articles(
        category=payload.industry,
        stock=payload.stock,
        interest=payload.interest,
    ) or repository.load_articles()
    behavior = repository.load_behavior_sessions()
    cards = ranker.rank_articles(profile, articles, behavior)
    return {
        "profile": profile.model_dump(),
        "items": [card.model_dump() for card in cards[:8]],
        "filters": repository.available_filters(),
    }


@app.post("/recommendations/explain")
async def explain_feed(payload: FeedRequest) -> dict[str, object]:
    profile = repository.load_profile()
    articles = repository.search_articles(
        category=payload.industry,
        stock=payload.stock,
        interest=payload.interest,
    ) or repository.load_articles()
    top_article = articles[0]
    return explainer.explain(profile, top_article)
