from app.schemas.briefing import BriefingChatRequest, BriefingChatResponse, BriefingResponse
from app.schemas.page_models import BriefingPageResponse
from app.services.ai.briefing_engine import BriefingEngine
from app.services.data.loader import DataRepository


class BriefingService:
    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository
        self.engine = BriefingEngine()

    def generate_daily_briefing(self) -> BriefingResponse:
        return self.engine.generate(self.repository.load_articles())

    def generate_topic_briefing(self, topic: str) -> BriefingPageResponse:
        related = self.repository.search_articles(interest=topic) or self.repository.load_articles()
        report = self.engine.generate(related)
        return BriefingPageResponse(
            topic=topic,
            report=report,
            related_articles=related[:4],
            suggested_questions=report.faqs,
        )

    def answer_question(self, payload: BriefingChatRequest) -> BriefingChatResponse:
        return self.engine.answer(payload, self.repository.load_articles())
