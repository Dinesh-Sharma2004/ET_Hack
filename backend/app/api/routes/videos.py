from fastapi import APIRouter, Depends

from app.schemas.video import VideoStudioResponse
from app.services.dependencies import get_video_service
from app.services.video import VideoService

router = APIRouter()


@router.get("/studio", response_model=VideoStudioResponse)
async def get_video_studio(service: VideoService = Depends(get_video_service)) -> VideoStudioResponse:
    return service.get_video_studio()
