from app.schemas.analytics import AnalyticsResponse, AudienceSlice
from app.services.data.loader import DataRepository


class AnalyticsService:
    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository

    def get_overview(self) -> AnalyticsResponse:
        return AnalyticsResponse(
            retention_curve=[1.0, 0.92, 0.84, 0.78, 0.71, 0.68, 0.63],
            sentiment_mix={"positive": 44.0, "neutral": 38.0, "negative": 18.0},
            audience=[
                AudienceSlice(segment="Investors", engagement=82.0, save_rate=37.0),
                AudienceSlice(segment="Founders", engagement=74.0, save_rate=29.0),
                AudienceSlice(segment="Students", engagement=68.0, save_rate=23.0),
            ],
            alerts=[
                "AI explainer videos are outperforming text briefings by 24% completion.",
                "Users with portfolio uploads click 1.8x more sector-specific briefings.",
            ],
        )
