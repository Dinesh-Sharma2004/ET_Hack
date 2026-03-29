from __future__ import annotations

import json
from pathlib import Path

from myet_shared.config import VIDEO_DIR, VIDEO_PUBLIC_BASE_URL
from myet_shared.models import Article

from .config import IMAGE_DIR_NAME, MANIFEST_NAME, RAG_DIR_NAME, SCENE_DIR_NAME, SUBTITLE_DIR_NAME
from .image_gen import SceneImageGenerator
from .llm import ScenePlanner
from .rag import LoadedNews, NewsRAGPipeline
from .subtitles import SubtitleGenerator
from .tts import NarrationEngine
from .utils import get_logger, stable_hash
from .video_gen import MovieComposer


logger = get_logger("myet.video.pipeline")


class VideoGenerationPipeline:
    def __init__(self) -> None:
        self.rag = NewsRAGPipeline()
        self.planner = ScenePlanner()
        self.image_generator = SceneImageGenerator()
        self.tts = NarrationEngine()
        self.subtitles = SubtitleGenerator()
        self.composer = MovieComposer()

    def list_videos(self, articles: list[Article], repository) -> list[dict[str, object]]:
        items = []
        for article in articles:
            asset = repository.load_video_asset(article.id)
            video_url = self._public_url(asset.video_path) if asset and Path(asset.video_path).exists() else None
            items.append(
                {
                    "id": f"video-{article.id}",
                    "title": f"{article.title} | AI Video",
                    "runtime_seconds": asset.runtime_seconds if asset else 0,
                    "category": article.category,
                    "summary": article.summary,
                    "related_article_ids": [article.id],
                    "video_url": video_url,
                    "status": asset.status if video_url and asset else "available",
                }
            )
        return items

    def get_video_detail(self, article: Article, repository) -> dict[str, object]:
        asset = repository.load_video_asset(article.id)
        if asset and asset.video_path and Path(asset.video_path).exists():
            return self._payload_from_asset(article, asset)
        return self.generate_for_article(article, repository)

    def generate_for_article(self, article: Article, repository) -> dict[str, object]:
        loaded = LoadedNews(
            title=article.title,
            text=f"{article.summary}\n\n{article.content}",
            source=article.source,
            url=article.url,
        )
        payload = self._generate(loaded, article.id)
        repository.save_video_asset(
            article_id=article.id,
            title=payload["detail"]["title"],
            video_path=payload["video_path"],
            audio_path=payload["detail"]["audio_path"],
            runtime_seconds=int(payload["detail"]["runtime_seconds"]),
            script=payload["script"],
            highlights=payload["key_highlights"],
            segments=payload["detail"]["segments"],
        )
        payload["related_articles"] = [article.model_dump()]
        payload.pop("video_path", None)
        return payload

    def generate_from_source(
        self,
        *,
        text: str | None = None,
        url: str | None = None,
        pdf_path: str | None = None,
        title: str | None = None,
    ) -> dict[str, object]:
        loaded = self.rag.load_source(text=text, url=url, pdf_path=pdf_path, title=title)
        source_id = stable_hash(loaded.title, loaded.url or loaded.text[:500])
        payload = self._generate(loaded, source_id)
        payload.pop("video_path", None)
        return payload

    def _generate(self, loaded: LoadedNews, source_id: str) -> dict[str, object]:
        output_dir = VIDEO_DIR / source_id
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = output_dir / MANIFEST_NAME
        if manifest_path.exists():
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload["video_url"] = self._public_url(payload["video_path"])
            return payload

        _, context_chunks = self.rag.build_context(
            loaded,
            persist_dir=output_dir / RAG_DIR_NAME,
            query=f"Build a sharp 60 to 120 second business news reel about {loaded.title}",
        )
        summary = self.planner.summarize(loaded.title, context_chunks)
        scenes = [scene.to_dict() for scene in self.planner.create_scene_plan(loaded.title, summary, context_chunks)]
        image_outputs = [self.image_generator.generate(loaded.title, scene, output_dir / IMAGE_DIR_NAME) for scene in scenes]
        tracks = self.tts.synthesize_scenes(scenes, output_dir / SCENE_DIR_NAME)
        durations = [track.duration_seconds for track in tracks]
        subtitle_timeline = self.subtitles.create_srt(scenes, durations, output_dir / "captions.srt")
        subtitle_frames = self.subtitles.render_overlays(subtitle_timeline, output_dir / SUBTITLE_DIR_NAME)
        runtime_seconds = self.composer.compose(
            scene_frames=[item["frame_path"] for item in image_outputs],
            subtitle_frames=subtitle_frames,
            narration_audio=[track.audio_path for track in tracks],
            durations=durations,
            output_path=output_dir / "story.mp4",
        )

        segments = []
        for index, scene in enumerate(scenes):
            segments.append(
                {
                    "scene": scene["title"],
                    "visual": scene["visual_description"],
                    "image_prompt": scene["image_prompt"],
                    "voiceover": scene["narration"],
                    "duration_seconds": round(durations[index], 2),
                    "image_path": image_outputs[index]["image_path"],
                }
            )

        payload = {
            "id": f"video-{source_id}",
            "detail": {
                "title": f"{loaded.title} | AI explainer",
                "runtime_seconds": round(runtime_seconds, 2),
                "tone": "AI newsroom reel",
                "segments": segments,
                "subtitles_preview": [item["text"] for item in subtitle_timeline[:3]],
                "production_notes": [
                    "Generated with LangChain + Chroma retrieval.",
                    "Scene visuals created with a Stable Diffusion CPU pipeline with deterministic fallback art.",
                    "Narration and subtitles are synced scene by scene.",
                ],
                "audio_path": tracks[0].audio_path if tracks else None,
                "video_url": self._public_url(str(output_dir / "story.mp4")),
            },
            "script": [scene["narration"] for scene in scenes],
            "key_highlights": [scene["summary"] for scene in scenes[:3]],
            "related_articles": [],
            "summary": summary,
            "source": {"title": loaded.title, "url": loaded.url, "type": loaded.source},
            "srt_path": str(output_dir / "captions.srt"),
            "video_path": str(output_dir / "story.mp4"),
            "video_url": self._public_url(str(output_dir / "story.mp4")),
        }
        manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def _payload_from_asset(self, article: Article, asset) -> dict[str, object]:
        video_url = self._public_url(asset.video_path)
        srt_path = str(Path(asset.video_path).with_name("captions.srt"))
        segments = asset.segments or []
        subtitles_preview = [segment.get("voiceover", "") for segment in segments[:3] if segment.get("voiceover")]
        return {
            "id": f"video-{article.id}",
            "detail": {
                "title": asset.title or f"{article.title} | AI explainer",
                "runtime_seconds": float(asset.runtime_seconds or 0),
                "tone": "AI newsroom reel",
                "segments": segments,
                "subtitles_preview": subtitles_preview,
                "production_notes": [
                    "Loaded from a cached video asset.",
                    "Scene visuals and narration were generated during an earlier render.",
                ],
                "audio_path": asset.audio_path,
                "video_url": video_url,
            },
            "script": asset.script or [],
            "key_highlights": asset.highlights or [],
            "related_articles": [article.model_dump()],
            "summary": article.summary,
            "source": {"title": article.title, "url": article.url, "type": article.source},
            "srt_path": srt_path if Path(srt_path).exists() else None,
            "video_url": video_url,
        }

    @staticmethod
    def _public_url(video_path: str | None) -> str | None:
        if not video_path:
            return None
        path = Path(video_path)
        relative = path.relative_to(VIDEO_DIR).as_posix()
        return f"{VIDEO_PUBLIC_BASE_URL}/media/{relative}"
