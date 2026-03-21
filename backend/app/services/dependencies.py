from functools import lru_cache

from app.services.analytics import AnalyticsService
from app.services.briefing import BriefingService
from app.services.data.loader import DataRepository
from app.services.newsroom import NewsroomService
from app.services.story import StoryService
from app.services.video import VideoService


@lru_cache
def get_repository() -> DataRepository:
    return DataRepository()


def get_newsroom_service() -> NewsroomService:
    return NewsroomService(get_repository())


def get_briefing_service() -> BriefingService:
    return BriefingService(get_repository())


def get_story_service() -> StoryService:
    return StoryService(get_repository())


def get_video_service() -> VideoService:
    return VideoService(get_repository())


def get_analytics_service() -> AnalyticsService:
    return AnalyticsService(get_repository())
