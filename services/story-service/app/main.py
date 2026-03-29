from fastapi import FastAPI

from myet_shared.repository import SharedRepository
from myet_shared.story import StoryArcEngine


repository = SharedRepository()
story_engine = StoryArcEngine()
app = FastAPI(title="MyET Story Service", version="2.0.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "story-service"}


@app.get("/story/{story_id}")
async def get_story(story_id: str) -> dict[str, object]:
    return story_engine.build(repository.load_articles(), story_id)
