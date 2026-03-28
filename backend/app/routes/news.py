from fastapi import APIRouter, Depends, Query

from app.schemas.page_models import DashboardOverviewResponse, NewsFeedResponse
from app.services.dependencies import get_newsroom_service
from app.services.newsroom import NewsroomService

router = APIRouter()


@router.get("", response_model=NewsFeedResponse)
async def get_news(
    category: str | None = None,
    stock: str | None = None,
    interest: str | None = None,
    search: str | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=20),
    service: NewsroomService = Depends(get_newsroom_service),
) -> NewsFeedResponse:
    return service.get_news_feed(category=category, stock=stock, interest=interest, search=search, offset=offset, limit=limit)


@router.get("/dashboard", response_model=DashboardOverviewResponse)
async def get_dashboard(service: NewsroomService = Depends(get_newsroom_service)) -> DashboardOverviewResponse:
    return service.get_dashboard_overview()
