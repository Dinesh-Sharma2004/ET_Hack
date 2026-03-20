from fastapi import APIRouter, Depends

from app.schemas.analytics import AnalyticsResponse
from app.services.analytics import AnalyticsService
from app.services.dependencies import get_analytics_service

router = APIRouter()


@router.get("/overview", response_model=AnalyticsResponse)
async def get_analytics(service: AnalyticsService = Depends(get_analytics_service)) -> AnalyticsResponse:
    return service.get_overview()
