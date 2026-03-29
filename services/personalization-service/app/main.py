from fastapi import FastAPI

from myet_shared.repository import SharedRepository


repository = SharedRepository()
app = FastAPI(title="MyET Personalization Service", version="1.0.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "personalization-service"}


@app.get("/profile")
async def get_profile() -> dict[str, object]:
    return repository.load_profile().model_dump()


@app.get("/signals")
async def get_personalization_signals() -> dict[str, object]:
    profile = repository.load_profile()
    behavior = repository.load_behavior_sessions()
    return {
        "profile": profile.model_dump(),
        "signals": {
            "roles": [profile.role],
            "interests": profile.interests,
            "sectors": profile.sectors,
            "portfolio_symbols": profile.portfolio_symbols,
            "risk_appetite": profile.risk_appetite,
            "behavior_sessions": len(behavior),
            "clicked_articles": sorted({article_id for session in behavior for article_id in session.clicked_articles})[:10],
        },
    }
