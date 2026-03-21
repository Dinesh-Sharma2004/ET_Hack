from app.schemas.page_models import StoryPageResponse
from app.schemas.story import StoryArcResponse
from app.services.ai.story_graph import StoryGraphEngine
from app.services.data.loader import DataRepository


class StoryService:
    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository
        self.engine = StoryGraphEngine()

    def get_story_arc(self) -> StoryArcResponse:
        return self.engine.build(self.repository.load_articles())

    def get_story_page(self, story_id: str) -> StoryPageResponse:
        related = self.repository.search_articles(interest=story_id) or self.repository.load_articles()
        arc = self.engine.build(related)
        return StoryPageResponse(story_id=story_id, arc=arc, related_articles=related[:4])
