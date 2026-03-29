from threading import Thread

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from myet_shared.config import TRANSLATION_WARM_LANGUAGES
from myet_shared.repository import SharedRepository
from myet_shared.translation import VernacularEngine


class TranslationRequest(BaseModel):
    article_id: str
    language: str = "Hindi"
    mode: str = "contextual"


repository = SharedRepository()
engine = VernacularEngine()
app = FastAPI(title="MyET Translation Service", version="2.0.0")


@app.on_event("startup")
async def warm_translation_models() -> None:
    Thread(target=engine.warm_models, args=(TRANSLATION_WARM_LANGUAGES,), daemon=True).start()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "translation-service"}


@app.post("/translate")
async def translate(payload: TranslationRequest) -> dict[str, str]:
    article = repository.get_article(payload.article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article {payload.article_id} not found.")
    return engine.translate(article, payload.language, payload.mode)
