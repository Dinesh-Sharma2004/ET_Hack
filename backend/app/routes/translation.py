from fastapi import APIRouter, Depends

from app.schemas.page_models import TranslationRequest, TranslationResponse
from app.services.dependencies import get_newsroom_service
from app.services.newsroom import NewsroomService

router = APIRouter()


@router.post("", response_model=TranslationResponse)
async def translate_article(
    payload: TranslationRequest, service: NewsroomService = Depends(get_newsroom_service)
) -> TranslationResponse:
    title, content = service.get_translated_article(payload.article_id, payload.language, payload.mode)
    return TranslationResponse(
        article_id=payload.article_id,
        language=payload.language,
        mode=payload.mode,
        title=title,
        content=content,
    )
