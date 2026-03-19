from pydantic import BaseModel


class TimelinePoint(BaseModel):
    date: str
    headline: str
    sentiment: float
    impact_score: float


class StoryNode(BaseModel):
    id: str
    label: str
    group: str


class StoryEdge(BaseModel):
    source: str
    target: str
    relation: str


class StoryArcResponse(BaseModel):
    theme: str
    timeline: list[TimelinePoint]
    entities: list[StoryNode]
    relationships: list[StoryEdge]
    what_next: list[str]
