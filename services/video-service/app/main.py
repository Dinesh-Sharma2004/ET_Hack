from threading import Thread

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, model_validator

from myet_shared.config import VIDEO_DIR
from myet_shared.repository import SharedRepository

from .project.config import VIDEO_PREGENERATE_COUNT
from .project import VideoGenerationPipeline


class GenerateVideoRequest(BaseModel):
    url: str | None = None
    text: str | None = None
    pdf_path: str | None = None
    title: str | None = None

    @model_validator(mode="after")
    def validate_input(self):
        if not any([self.url, self.text, self.pdf_path]):
            raise ValueError("Provide at least one of url, text, or pdf_path.")
        return self


repository = SharedRepository()
engine = VideoGenerationPipeline()
app = FastAPI(title="MyET Video Service", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/media", StaticFiles(directory=str(VIDEO_DIR)), name="media")


def _pregenerate_latest_videos() -> None:
    if VIDEO_PREGENERATE_COUNT <= 0:
        return
    for article in repository.load_articles()[:VIDEO_PREGENERATE_COUNT]:
        if repository.load_video_asset(article.id):
            continue
        try:
            engine.generate_for_article(article, repository)
        except Exception:
            continue


@app.on_event("startup")
async def warm_video_assets() -> None:
    Thread(target=_pregenerate_latest_videos, daemon=True).start()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "video-service"}


@app.get("/videos")
async def list_videos() -> dict[str, object]:
    return {"items": engine.list_videos(repository.load_articles(), repository)}


@app.get("/videos/{video_id}")
async def get_video(video_id: str) -> dict[str, object]:
    article_id = video_id.replace("video-", "")
    article = repository.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article {article_id} not found.")
    return engine.get_video_detail(article, repository)


@app.post("/generate-video")
async def generate_video(payload: GenerateVideoRequest) -> dict[str, object]:
    return engine.generate_from_source(
        text=payload.text,
        url=payload.url,
        pdf_path=payload.pdf_path,
        title=payload.title,
    )
