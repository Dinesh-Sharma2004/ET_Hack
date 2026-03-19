from pydantic import BaseModel, Field

from app.schemas.common import MetricCard, NewsCard


class UserProfile(BaseModel):
    role: str
    interests: list[str]
    sectors: list[str]
    languages: list[str]
    risk_appetite: str
    portfolio_symbols: list[str] = Field(default_factory=list)


class OnboardingRequest(UserProfile):
    onboarding_completed: bool = True


class RecommendationResponse(BaseModel):
    profile: UserProfile
    recommendations: list[NewsCard]


class DashboardResponse(BaseModel):
    profile: UserProfile
    featured: list[NewsCard]
    deep_briefings: list[NewsCard]
    metrics: list[MetricCard]
    translations: dict[str, str]
