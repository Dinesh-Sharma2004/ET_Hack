from fastapi import APIRouter, Depends

from app.schemas.story import StoryArcResponse
from app.services.dependencies import get_story_service
from app.services.story import StoryService

router = APIRouter()


@router.get("/arc", response_model=StoryArcResponse)
async def get_story_arc(service: StoryService = Depends(get_story_service)) -> StoryArcResponse:
    return service.get_story_arc()
