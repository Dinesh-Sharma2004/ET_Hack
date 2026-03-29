from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from ..config import DEFAULT_IMAGE_SIZE, DEFAULT_VIDEO_SIZE, VIDEO_DIFFUSION_MODEL, VIDEO_USE_DIFFUSION, WATERMARK_TEXT
from ..utils import get_logger, stable_hash


logger = get_logger("myet.video.image")


class SceneImageGenerator:
    def __init__(self) -> None:
        self.font = ImageFont.load_default()

    def generate(self, title: str, scene: dict[str, object], output_dir: Path) -> dict[str, str]:
        output_dir.mkdir(parents=True, exist_ok=True)
        prompt = str(scene["image_prompt"])
        scene_key = stable_hash(title, prompt)
        raw_image_path = output_dir / f"{scene_key}.png"
        frame_path = output_dir / f"{scene_key}-frame.png"
        metadata_path = output_dir / f"{scene_key}.json"

        if not raw_image_path.exists():
            image = self._generate_with_diffusion(prompt) or self._generate_fallback_art(prompt, str(scene["title"]))
            image.save(raw_image_path)
            metadata_path.write_text(json.dumps({"prompt": prompt}, indent=2), encoding="utf-8")
        if not frame_path.exists():
            self._build_story_frame(raw_image_path, frame_path, title, scene)
        return {"image_path": str(raw_image_path), "frame_path": str(frame_path)}

    def _build_story_frame(self, image_path: Path, frame_path: Path, story_title: str, scene: dict[str, object]) -> None:
        source = Image.open(image_path).convert("RGB")
        canvas = Image.new("RGB", DEFAULT_VIDEO_SIZE, "#08111f")
        background = source.resize(DEFAULT_VIDEO_SIZE).filter(ImageFilter.GaussianBlur(radius=18))
        overlay = Image.new("RGBA", DEFAULT_VIDEO_SIZE, (5, 11, 24, 158))
        canvas.paste(background, (0, 0))
        canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay)

        hero = source.resize((560, 560))
        canvas.paste(hero.convert("RGBA"), (70, 80))
        drawer = ImageDraw.Draw(canvas)
        drawer.rounded_rectangle((54, 56, 1226, 664), radius=36, outline=(255, 255, 255, 20), width=2)
        drawer.text((680, 92), WATERMARK_TEXT, fill=(125, 211, 252), font=self.font)
        drawer.text((680, 136), str(scene["title"])[:80], fill=(255, 255, 255), font=self.font)
        drawer.multiline_text((680, 196), story_title[:120], fill=(203, 213, 225), font=self.font, spacing=10)
        drawer.multiline_text((680, 310), str(scene["visual_description"])[:220], fill=(226, 232, 240), font=self.font, spacing=10)
        drawer.rounded_rectangle((680, 560, 1180, 628), radius=18, fill=(15, 23, 42, 185))
        drawer.multiline_text((700, 580), str(scene["subtitle"])[:120], fill=(248, 250, 252), font=self.font, spacing=8)
        canvas.convert("RGB").save(frame_path)

    def _generate_with_diffusion(self, prompt: str) -> Image.Image | None:
        if not VIDEO_USE_DIFFUSION:
            return None
        try:
            pipe = self._load_pipe()
            result = pipe(
                prompt=prompt,
                num_inference_steps=18,
                guidance_scale=6.5,
                height=DEFAULT_IMAGE_SIZE[1],
                width=DEFAULT_IMAGE_SIZE[0],
            )
            return result.images[0]
        except Exception as exc:  # noqa: BLE001
            logger.warning("Stable Diffusion image generation failed, using fallback art: %s", exc)
            return None

    def _generate_fallback_art(self, prompt: str, scene_title: str) -> Image.Image:
        image = Image.new("RGB", DEFAULT_IMAGE_SIZE, color=(6, 18, 32))
        drawer = ImageDraw.Draw(image)
        color_seed = int(stable_hash(prompt)[:6], 16)
        accent = ((color_seed >> 16) & 255, (color_seed >> 8) & 255, color_seed & 255)
        drawer.ellipse((28, 40, 380, 380), fill=(*accent, 110), outline=(255, 255, 255))
        drawer.rectangle((220, 120, 486, 470), outline=(125, 211, 252), width=4)
        drawer.multiline_text((32, 400), scene_title[:80], fill=(255, 255, 255), font=self.font, spacing=10)
        drawer.multiline_text((32, 448), prompt[:130], fill=(203, 213, 225), font=self.font, spacing=8)
        return image

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_pipe():
        from diffusers import DPMSolverMultistepScheduler, StableDiffusionPipeline

        pipe = StableDiffusionPipeline.from_pretrained(VIDEO_DIFFUSION_MODEL)
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        pipe.enable_attention_slicing()
        pipe = pipe.to("cpu")
        return pipe
