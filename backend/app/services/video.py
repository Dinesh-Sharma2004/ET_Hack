from app.schemas.page_models import VideoDetailResponse, VideoListItem, VideoListResponse
from app.schemas.video import VideoSegment, VideoStudioResponse
from app.services.data.loader import DataRepository


class VideoService:
    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository

    def get_video_studio(self) -> VideoStudioResponse:
        lead = self.repository.load_articles()[0]
        return VideoStudioResponse(
            title=f"{lead.title} | 90-second AI explainer",
            runtime_seconds=94,
            tone="Crisp, analytical, optimistic",
            segments=[
                VideoSegment(
                    scene="Opening hook",
                    visual="Animated market pulse with article headline and live tickers",
                    voiceover="Markets are repricing the future around AI infrastructure, policy, and execution quality.",
                    duration_seconds=18,
                ),
                VideoSegment(
                    scene="Key chart",
                    visual="Bar chart of capex growth, earnings momentum, and valuation spread",
                    voiceover="The winners are not just growing faster. They are converting spend into defensible revenue.",
                    duration_seconds=26,
                ),
                VideoSegment(
                    scene="India angle",
                    visual="Map-led overlay with BFSI, semiconductor, and SaaS callouts",
                    voiceover="India's digital infrastructure and policy continuity are amplifying select business models.",
                    duration_seconds=24,
                ),
                VideoSegment(
                    scene="Close",
                    visual="Portfolio impact checklist and subscribe CTA",
                    voiceover="For investors and founders, the next move is disciplined focus on ROI, margins, and moats.",
                    duration_seconds=26,
                ),
            ],
            subtitles_preview=[
                "AI infrastructure is reshaping capital allocation.",
                "Execution quality matters more than narrative momentum.",
                "India-linked sectors may see structural tailwinds.",
            ],
            production_notes=[
                "Designed for FFmpeg stitching with chart PNG overlays and TTS narration.",
                "Swap voiceover provider through the async worker pipeline.",
            ],
        )

    def list_videos(self) -> VideoListResponse:
        articles = self.repository.load_articles()
        items = [
            VideoListItem(
                id=f"video-{article.id}",
                title=f"{article.title} | AI Video",
                runtime_seconds=75 + (index * 8),
                category=article.category,
                summary=article.summary,
                related_article_ids=[article.id],
            )
            for index, article in enumerate(articles)
        ]
        return VideoListResponse(items=items)

    def get_video_detail(self, video_id: str) -> VideoDetailResponse:
        article_id = video_id.replace("video-", "")
        article = self.repository.get_article(article_id) or self.repository.load_articles()[0]
        detail = self.get_video_studio()
        script = [segment.voiceover for segment in detail.segments]
        return VideoDetailResponse(
            id=video_id,
            detail=detail,
            script=script,
            key_highlights=detail.subtitles_preview,
            related_articles=[article],
        )
