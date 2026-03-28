from fastapi import APIRouter, Depends

from app.schemas.page_models import VideoDetailResponse, VideoListResponse
from app.services.dependencies import get_video_service
from app.services.video import VideoService

router = APIRouter()


@router.get("", response_model=VideoListResponse)
async def list_videos(service: VideoService = Depends(get_video_service)) -> VideoListResponse:
    return service.list_videos()


@router.get("/{video_id}", response_model=VideoDetailResponse)
async def get_video(video_id: str, service: VideoService = Depends(get_video_service)) -> VideoDetailResponse:
    return service.get_video_detail(video_id)
