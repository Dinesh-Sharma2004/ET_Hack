from fastapi import APIRouter, Depends

from app.schemas.page_models import StoryPageResponse
from app.services.dependencies import get_story_service
from app.services.story import StoryService

router = APIRouter()


@router.get("/{story_id}", response_model=StoryPageResponse)
async def get_story(story_id: str, service: StoryService = Depends(get_story_service)) -> StoryPageResponse:
    return service.get_story_page(story_id)
