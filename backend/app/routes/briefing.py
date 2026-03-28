from fastapi import APIRouter, Depends

from app.schemas.briefing import BriefingChatRequest
from app.schemas.page_models import BriefingChatPageResponse, BriefingPageResponse
from app.services.briefing import BriefingService
from app.services.dependencies import get_briefing_service

router = APIRouter()


@router.get("/{topic}", response_model=BriefingPageResponse)
async def get_briefing(topic: str, service: BriefingService = Depends(get_briefing_service)) -> BriefingPageResponse:
    return service.generate_topic_briefing(topic)


@router.post("/{topic}/chat", response_model=BriefingChatPageResponse)
async def chat_briefing(
    topic: str, payload: BriefingChatRequest, service: BriefingService = Depends(get_briefing_service)
) -> BriefingChatPageResponse:
    return BriefingChatPageResponse(topic=topic, response=service.answer_question(payload))
