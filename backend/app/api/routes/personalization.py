from fastapi import APIRouter, Depends, File, UploadFile

from app.schemas.personalization import (
    DashboardResponse,
    OnboardingRequest,
    RecommendationResponse,
    UserProfile,
)
from app.services.dependencies import get_newsroom_service
from app.services.newsroom import NewsroomService

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(service: NewsroomService = Depends(get_newsroom_service)) -> DashboardResponse:
    return service.build_dashboard()


@router.post("/onboarding", response_model=UserProfile)
async def complete_onboarding(
    payload: OnboardingRequest, service: NewsroomService = Depends(get_newsroom_service)
) -> UserProfile:
    return service.save_profile(payload)


@router.post("/portfolio/upload", response_model=RecommendationResponse)
async def upload_portfolio(
    file: UploadFile = File(...), service: NewsroomService = Depends(get_newsroom_service)
) -> RecommendationResponse:
    content = await file.read()
    return service.recommend_from_portfolio_bytes(content, file.filename or "portfolio.csv")
