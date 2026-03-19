from pydantic import BaseModel


class AudienceSlice(BaseModel):
    segment: str
    engagement: float
    save_rate: float


class AnalyticsResponse(BaseModel):
    retention_curve: list[float]
    sentiment_mix: dict[str, float]
    audience: list[AudienceSlice]
    alerts: list[str]
