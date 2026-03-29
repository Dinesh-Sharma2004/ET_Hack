import math
import shutil
import subprocess
import wave
from pathlib import Path

import imageio_ffmpeg
import matplotlib.pyplot as plt
import pyttsx3
from PIL import Image, ImageDraw, ImageFont

from myet_shared.config import VIDEO_DIR, VIDEO_PUBLIC_BASE_URL
from myet_shared.generation import generate_text
from myet_shared.models import Article
from myet_shared.nlp import top_sentences


class VideoStudioEngine:
    def list_videos(self, articles: list[Article], repository) -> list[dict[str, object]]:
        items = []
        for article in articles:
            asset = repository.load_video_asset(article.id)
            items.append(
                {
                    "id": f"video-{article.id}",
                    "title": f"{article.title} | AI Video",
                    "runtime_seconds": asset.runtime_seconds if asset else 0,
                    "category": article.category,
                    "summary": article.summary,
                    "related_article_ids": [article.id],
                    "video_url": self._public_url(asset.video_path) if asset else None,
                    "status": asset.status if asset else "not_generated",
                }
            )
        return items

    def get_video_detail(self, article: Article, repository) -> dict[str, object]:
        output_dir = VIDEO_DIR / article.id
        output_dir.mkdir(parents=True, exist_ok=True)
        video_path = output_dir / "story.mp4"
        audio_path = output_dir / "narration.wav"

        script = self._generate_script(article)
        segments = self._generate_segments(article, script)
        highlights = [segment["voiceover"] for segment in segments[:3]]

        if not video_path.exists():
            self._synthesize_audio(script, audio_path)
            slide_paths = self._generate_visuals(article, segments, output_dir)
            self._render_video(slide_paths, audio_path, video_path)

        runtime_seconds = self._audio_duration_seconds(audio_path) if audio_path.exists() else 0
        repository.save_video_asset(
            article_id=article.id,
            title=f"{article.title} | AI explainer",
            video_path=str(video_path),
            audio_path=str(audio_path) if audio_path.exists() else None,
            runtime_seconds=runtime_seconds,
            script=script,
            highlights=highlights,
            segments=segments,
        )
        return {
            "id": f"video-{article.id}",
            "detail": {
                "title": f"{article.title} | AI explainer",
                "runtime_seconds": runtime_seconds,
                "tone": "Analytical and newsroom-ready",
                "segments": segments,
                "subtitles_preview": highlights,
                "production_notes": [
                    f"Rendered to {video_path.name}",
                    "Generated from article text, TTS narration, and chart frames.",
                ],
                "video_url": self._public_url(str(video_path)),
            },
            "script": script,
            "key_highlights": highlights,
            "related_articles": [article.model_dump()],
            "video_url": self._public_url(str(video_path)),
        }

    def _generate_script(self, article: Article) -> list[str]:
        generated = generate_text(
            f"Write a 5 line business news video narration script, each line concise, for this article.\n"
            f"Title: {article.title}\nSummary: {article.summary}\nContent: {article.content[:1600]}",
            max_new_tokens=180,
        )
        lines = [line.strip("- ").strip() for line in generated.split("\n") if line.strip()]
        if len(lines) >= 4:
            return lines[:5]
        sentences = top_sentences(article.title, f"{article.summary}. {article.content}", limit=4)
        opener = f"Today in business news: {article.title}."
        closer = f"The takeaway for decision makers is to watch {', '.join(article.entities[:3]) or article.category} closely."
        return [opener, *sentences, closer]

    def _generate_segments(self, article: Article, script: list[str]) -> list[dict[str, object]]:
        labels = ["Opening", "Context", "Drivers", "Takeaway", "Close"]
        segments = []
        for index, line in enumerate(script):
            segments.append(
                {
                    "scene": labels[index] if index < len(labels) else f"Scene {index + 1}",
                    "visual": f"Dynamic text frame for {article.category} with entity overlay: {', '.join(article.entities[:3])}",
                    "voiceover": line,
                    "duration_seconds": max(8, math.ceil(len(line.split()) / 2.6)),
                }
            )
        return segments

    def _synthesize_audio(self, script: list[str], audio_path: Path) -> None:
        engine = pyttsx3.init()
        engine.setProperty("rate", 172)
        engine.save_to_file(" ".join(script), str(audio_path))
        engine.runAndWait()

    def _generate_visuals(self, article: Article, segments: list[dict[str, object]], output_dir: Path) -> list[Path]:
        slide_paths: list[Path] = []
        chart_path = output_dir / "chart.png"
        plt.figure(figsize=(8, 4.5))
        plt.bar(["sentiment", "read time", "entities"], [article.sentiment, article.read_time_minutes / 10, len(article.entities) / 10])
        plt.title(article.title[:60])
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        font = ImageFont.load_default()
        for index, segment in enumerate(segments):
            image = Image.new("RGB", (1280, 720), color=(9 + (index * 12), 26, 41))
            drawer = ImageDraw.Draw(image)
            drawer.text((60, 60), article.category.upper(), fill=(136, 244, 214), font=font)
            drawer.text((60, 120), article.title[:120], fill=(255, 255, 255), font=font)
            drawer.multiline_text((60, 220), segment["voiceover"], fill=(220, 230, 241), font=font, spacing=8)
            if chart_path.exists():
                chart = Image.open(chart_path).resize((420, 240))
                image.paste(chart, (800, 380))
            slide_path = output_dir / f"slide-{index:02d}.png"
            image.save(slide_path)
            slide_paths.append(slide_path)
        return slide_paths

    def _render_video(self, slide_paths: list[Path], audio_path: Path, video_path: Path) -> None:
        ffmpeg_executable = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()
        if not ffmpeg_executable:
            raise RuntimeError("ffmpeg is required to generate video assets.")
        duration = max(self._audio_duration_seconds(audio_path), 1)
        per_slide = max(duration / max(len(slide_paths), 1), 2)
        concat_path = video_path.parent / "slides.txt"
        concat_lines = []
        for slide_path in slide_paths:
            concat_lines.append(f"file '{slide_path.as_posix()}'")
            concat_lines.append(f"duration {per_slide}")
        concat_lines.append(f"file '{slide_paths[-1].as_posix()}'")
        concat_path.write_text("\n".join(concat_lines), encoding="utf-8")
        subprocess.run(
            [
                ffmpeg_executable,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_path),
                "-i",
                str(audio_path),
                "-vsync",
                "vfr",
                "-pix_fmt",
                "yuv420p",
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                "-shortest",
                str(video_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    @staticmethod
    def _audio_duration_seconds(audio_path: Path) -> int:
        with wave.open(str(audio_path), "rb") as audio_file:
            frames = audio_file.getnframes()
            rate = audio_file.getframerate()
            return max(int(frames / max(rate, 1)), 1)

    @staticmethod
    def _public_url(video_path: str | None) -> str | None:
        if not video_path:
            return None
        path = Path(video_path)
        relative = path.relative_to(VIDEO_DIR).as_posix()
        return f"{VIDEO_PUBLIC_BASE_URL}/media/{relative}"
