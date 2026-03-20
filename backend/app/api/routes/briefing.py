from fastapi import APIRouter, Depends

from app.schemas.briefing import BriefingChatRequest, BriefingChatResponse, BriefingResponse
from app.services.briefing import BriefingService
from app.services.dependencies import get_briefing_service

router = APIRouter()


@router.get("/daily", response_model=BriefingResponse)
async def get_daily_briefing(service: BriefingService = Depends(get_briefing_service)) -> BriefingResponse:
    return service.generate_daily_briefing()


@router.post("/chat", response_model=BriefingChatResponse)
async def chat_with_briefing(
    payload: BriefingChatRequest, service: BriefingService = Depends(get_briefing_service)
) -> BriefingChatResponse:
    return service.answer_question(payload)
