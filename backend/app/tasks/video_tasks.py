from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.video_tasks.render_video")
def render_video(article_id: str) -> dict[str, str]:
    return {
        "article_id": article_id,
        "status": "queued",
        "message": "Video render scaffold is ready for FFmpeg, TTS, and subtitle generation jobs.",
    }
