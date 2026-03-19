from pydantic import BaseModel


class Article(BaseModel):
    id: str
    title: str
    summary: str
    content: str
    category: str
    entities: list[str]
    sentiment: float
    language: str
    published_at: str
    source: str
    read_time_minutes: int


class NewsCard(BaseModel):
    article_id: str
    title: str
    summary: str
    category: str
    relevance_score: float
    why_it_matters: str
    entities: list[str]


class MetricCard(BaseModel):
    label: str
    value: str
    delta: str
