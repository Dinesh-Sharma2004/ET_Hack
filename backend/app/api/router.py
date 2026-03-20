from fastapi import APIRouter

from app.api.routes import analytics, briefing, personalization, stories, videos
from app.routes import briefing as page_briefing
from app.routes import news, profile, recommendations, story, translation, video

api_router = APIRouter()
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(page_briefing.router, prefix="/briefing", tags=["briefing"])
api_router.include_router(story.router, prefix="/story", tags=["story"])
api_router.include_router(video.router, prefix="/video", tags=["video"])
api_router.include_router(translation.router, prefix="/translate", tags=["translation"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(personalization.router, prefix="/personalization", tags=["personalization"])
api_router.include_router(briefing.router, prefix="/briefings", tags=["briefings"])
api_router.include_router(stories.router, prefix="/stories", tags=["stories"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
