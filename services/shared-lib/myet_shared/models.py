from pydantic import BaseModel, Field


class Article(BaseModel):
    id: str
    title: str
    summary: str
    content: str
    category: str
    entities: list[str] = Field(default_factory=list)
    sentiment: float
    language: str = "English"
    published_at: str
    source: str
    read_time_minutes: int = 1
    url: str | None = None
    image_url: str | None = None


class UserProfile(BaseModel):
    role: str = "Investor"
    interests: list[str] = Field(default_factory=lambda: ["Markets", "AI"])
    sectors: list[str] = Field(default_factory=lambda: ["Technology", "Finance"])
    languages: list[str] = Field(default_factory=lambda: ["English", "Hindi"])
    risk_appetite: str = "Balanced"
    portfolio_symbols: list[str] = Field(default_factory=list)
    onboarding_completed: bool = True


class BehaviorSession(BaseModel):
    user_segment: str
    clicked_articles: list[str] = Field(default_factory=list)
    saved_articles: list[str] = Field(default_factory=list)
    dwell_seconds: int = 0
    preferred_mode: str = "expert"


class NewsCard(BaseModel):
    article_id: str
    title: str
    summary: str
    category: str
    relevance_score: float
    why_it_matters: str
    entities: list[str] = Field(default_factory=list)


class RetrievalHit(BaseModel):
    article_id: str
    title: str
    chunk_id: str
    text: str
    dense_score: float
    keyword_score: float
    combined_score: float
    source: str | None = None
    published_at: str | None = None
    url: str | None = None
