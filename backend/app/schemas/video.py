from pydantic import BaseModel


class VideoSegment(BaseModel):
    scene: str
    visual: str
    voiceover: str
    duration_seconds: int


class VideoStudioResponse(BaseModel):
    title: str
    runtime_seconds: int
    tone: str
    segments: list[VideoSegment]
    subtitles_preview: list[str]
    production_notes: list[str]
