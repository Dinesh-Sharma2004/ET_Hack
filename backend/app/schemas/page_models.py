from pydantic import BaseModel, Field

from app.schemas.briefing import BriefingChatResponse, BriefingResponse
from app.schemas.common import Article, MetricCard, NewsCard
from app.schemas.personalization import UserProfile
from app.schemas.story import StoryArcResponse
from app.schemas.video import VideoStudioResponse


class NewsFeedResponse(BaseModel):
    items: list[Article]
    total: int
    offset: int
    limit: int
    highlights: list[MetricCard]
    trending_topics: list[str]


class RecommendationFeedResponse(BaseModel):
    profile: UserProfile
    items: list[NewsCard]
    total: int
    filters: dict[str, list[str]]


class DashboardOverviewResponse(BaseModel):
    profile: UserProfile
    feed: list[NewsCard]
    highlights: list[MetricCard]
    trending: list[Article]


class BriefingPageResponse(BaseModel):
    topic: str
    report: BriefingResponse
    related_articles: list[Article]
    suggested_questions: list[str]


class StoryPageResponse(BaseModel):
    story_id: str
    arc: StoryArcResponse
    related_articles: list[Article]


class VideoListItem(BaseModel):
    id: str
    title: str
    runtime_seconds: int
    category: str
    summary: str
    related_article_ids: list[str]


class VideoListResponse(BaseModel):
    items: list[VideoListItem]


class VideoDetailResponse(BaseModel):
    id: str
    detail: VideoStudioResponse
    script: list[str]
    key_highlights: list[str]
    related_articles: list[Article]


class TranslationRequest(BaseModel):
    article_id: str
    language: str = "Hindi"
    mode: str = "contextual"


class TranslationResponse(BaseModel):
    article_id: str
    language: str
    mode: str
    title: str
    content: str


class ProfileUpdateRequest(UserProfile):
    onboarding_completed: bool = True


class PortfolioUploadResponse(BaseModel):
    profile: UserProfile
    items: list[NewsCard]


class BriefingChatPageResponse(BaseModel):
    topic: str
    response: BriefingChatResponse


class FilterOptionsResponse(BaseModel):
    industries: list[str] = Field(default_factory=list)
    stocks: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
