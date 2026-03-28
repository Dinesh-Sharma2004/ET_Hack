from fastapi import APIRouter, Depends

from app.schemas.page_models import RecommendationFeedResponse
from app.services.dependencies import get_newsroom_service
from app.services.newsroom import NewsroomService

router = APIRouter()


@router.get("", response_model=RecommendationFeedResponse)
async def get_recommendations(
    industry: str | None = None,
    stock: str | None = None,
    interest: str | None = None,
    service: NewsroomService = Depends(get_newsroom_service),
) -> RecommendationFeedResponse:
    return service.get_recommendations(industry=industry, stock=stock, interest=interest)
