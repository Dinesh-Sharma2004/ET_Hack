from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..config import DEFAULT_VIDEO_SIZE


class SubtitleGenerator:
    def create_srt(self, scene_plans: list[dict[str, object]], durations: list[float], output_path: Path) -> list[dict[str, object]]:
        timeline: list[dict[str, object]] = []
        current = 0.0
        entries: list[str] = []
        for index, scene in enumerate(scene_plans):
            start = current
            end = current + durations[index]
            text = str(scene["subtitle"]).strip()
            timeline.append({"index": index + 1, "start": start, "end": end, "text": text})
            entries.append(f"{index + 1}\n{self._fmt(start)} --> {self._fmt(end)}\n{text}\n")
            current = end
        output_path.write_text("\n".join(entries), encoding="utf-8")
        return timeline

    def render_overlays(self, subtitle_timeline: list[dict[str, object]], output_dir: Path) -> list[str]:
        output_dir.mkdir(parents=True, exist_ok=True)
        font = ImageFont.load_default()
        paths: list[str] = []
        for item in subtitle_timeline:
            image = Image.new("RGBA", DEFAULT_VIDEO_SIZE, (0, 0, 0, 0))
            drawer = ImageDraw.Draw(image)
            drawer.rounded_rectangle((140, 602, 1140, 676), radius=18, fill=(7, 11, 18, 210))
            drawer.multiline_text((180, 624), item["text"][:180], fill=(248, 250, 252), font=font, spacing=8)
            target = output_dir / f"subtitle-{item['index']:02d}.png"
            image.save(target)
            paths.append(str(target))
        return paths

    @staticmethod
    def _fmt(seconds: float) -> str:
        milliseconds = int(round(seconds * 1000))
        hours = milliseconds // 3_600_000
        minutes = (milliseconds % 3_600_000) // 60_000
        secs = (milliseconds % 60_000) // 1_000
        millis = milliseconds % 1_000
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
