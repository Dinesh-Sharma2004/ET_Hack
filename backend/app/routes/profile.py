from fastapi import APIRouter, Depends, File, UploadFile

from app.schemas.page_models import PortfolioUploadResponse, ProfileUpdateRequest
from app.schemas.personalization import UserProfile
from app.services.dependencies import get_newsroom_service
from app.services.newsroom import NewsroomService

router = APIRouter()


@router.get("", response_model=UserProfile)
async def get_profile(service: NewsroomService = Depends(get_newsroom_service)) -> UserProfile:
    return service.repository.load_profile()


@router.put("", response_model=UserProfile)
async def update_profile(
    payload: ProfileUpdateRequest, service: NewsroomService = Depends(get_newsroom_service)
) -> UserProfile:
    return service.update_profile(payload)


@router.post("/portfolio", response_model=PortfolioUploadResponse)
async def upload_portfolio(
    file: UploadFile = File(...), service: NewsroomService = Depends(get_newsroom_service)
) -> PortfolioUploadResponse:
    content = await file.read()
    return service.upload_portfolio(content, file.filename or "portfolio.csv")
