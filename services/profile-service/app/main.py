from io import BytesIO

import pandas as pd
from fastapi import FastAPI, File, UploadFile

from myet_shared.personalization import PersonalizationEngine
from myet_shared.repository import SharedRepository


repository = SharedRepository()
ranker = PersonalizationEngine()
app = FastAPI(title="MyET Profile Service", version="2.0.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "profile-service"}


@app.get("/profile")
async def get_profile() -> dict[str, object]:
    return repository.load_profile().model_dump()


@app.put("/profile")
async def update_profile(payload: dict[str, object]) -> dict[str, object]:
    current = repository.load_profile().model_dump()
    current.update(payload)
    updated = repository.save_profile(type(repository.load_profile())(**current))
    return updated.model_dump()


@app.post("/profile/portfolio")
async def upload_portfolio(file: UploadFile = File(...)) -> dict[str, object]:
    content = await file.read()
    frame = pd.read_csv(BytesIO(content))
    column = "symbol" if "symbol" in frame.columns else frame.columns[0]
    symbols = frame[column].dropna().astype(str).str.upper().tolist()
    repository.save_portfolio_symbols(symbols)
    profile = repository.load_profile()
    behavior = repository.load_behavior_sessions()
    recommendations = ranker.rank_articles(profile, repository.load_articles(), behavior)[:5]
    return {
        "profile": profile.model_dump(),
        "items": [item.model_dump() for item in recommendations],
    }
