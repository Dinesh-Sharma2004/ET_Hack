from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass

import requests

from myet_shared.generation import generate_text

from ..config import DEFAULT_SCENE_COUNT, OPENROUTER_API_KEY, OPENROUTER_MODEL
from ..utils import get_logger


logger = get_logger("myet.video.llm")


@dataclass
class ScenePlan:
    index: int
    title: str
    summary: str
    visual_description: str
    image_prompt: str
    narration: str
    subtitle: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class ScenePlanner:
    def summarize(self, title: str, context_chunks: list[str]) -> str:
        prompt = (
            "Summarize this business news story in 3 concise sentences for a modern AI video explainer.\n"
            f"Title: {title}\n"
            f"Context: {' '.join(context_chunks[:4])[:2200]}"
        )
        return self._generate(prompt, max_new_tokens=120)

    def create_scene_plan(self, title: str, summary: str, context_chunks: list[str], scene_count: int = DEFAULT_SCENE_COUNT) -> list[ScenePlan]:
        prompt = (
            "Create a JSON array for an AI business news video. "
            "Each object must have keys: title, summary, visual_description, image_prompt, narration, subtitle. "
            f"Return exactly {scene_count} scenes. Keep narration under 18 words per scene. "
            "Keep visual prompts cinematic and newsroom-friendly.\n"
            f"Story title: {title}\n"
            f"Summary: {summary}\n"
            f"Context: {' '.join(context_chunks[:5])[:2600]}"
        )
        raw = self._generate(prompt, max_new_tokens=640)
        parsed = self._parse_json(raw, scene_count=scene_count)
        if parsed:
            return [ScenePlan(index=index + 1, **scene) for index, scene in enumerate(parsed[:scene_count])]
        return self._fallback_scenes(title, summary, context_chunks, scene_count=scene_count)

    def _generate(self, prompt: str, max_new_tokens: int) -> str:
        if OPENROUTER_API_KEY:
            try:
                return self._generate_openrouter(prompt, max_new_tokens=max_new_tokens)
            except Exception as exc:  # noqa: BLE001
                logger.warning("OpenRouter fallback failed, using local generation: %s", exc)
        return generate_text(prompt, max_new_tokens=max_new_tokens)

    @staticmethod
    def _generate_openrouter(prompt: str, max_new_tokens: int) -> str:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            timeout=60,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_new_tokens,
            },
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"].strip()

    @staticmethod
    def _parse_json(raw: str, scene_count: int) -> list[dict[str, str]] | None:
        try:
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if not match:
                return None
            items = json.loads(match.group(0))
            cleaned: list[dict[str, str]] = []
            for item in items[:scene_count]:
                cleaned.append(
                    {
                        "title": str(item.get("title", "Scene")).strip(),
                        "summary": str(item.get("summary", "")).strip(),
                        "visual_description": str(item.get("visual_description", "")).strip(),
                        "image_prompt": str(item.get("image_prompt", "")).strip(),
                        "narration": str(item.get("narration", "")).strip(),
                        "subtitle": str(item.get("subtitle", item.get("narration", ""))).strip(),
                    }
                )
            return cleaned or None
        except json.JSONDecodeError:
            return None

    def _fallback_scenes(self, title: str, summary: str, context_chunks: list[str], scene_count: int) -> list[ScenePlan]:
        logger.info("Falling back to deterministic scene planning for %s scenes.", scene_count)
        sentences = self._split_sentences(summary + ". " + " ".join(context_chunks[:4]))
        while len(sentences) < scene_count:
            sentences.append(summary)
        scenes: list[ScenePlan] = []
        for index in range(scene_count):
            sentence = self._condense_sentence(sentences[index], limit_words=18)[:180]
            scene_title = self._short_title(sentence, fallback=f"Scene {index + 1}")
            scenes.append(
                ScenePlan(
                    index=index + 1,
                    title=scene_title,
                    summary=sentence,
                    visual_description=f"Clean business-news visual centered on {scene_title.lower()} with editorial overlays.",
                    image_prompt=(
                        f"Editorial business news illustration, modern newsroom aesthetic, "
                        f"{scene_title.lower()}, data overlays, cinematic lighting, consistent palette"
                    ),
                    narration=sentence,
                    subtitle=sentence,
                )
            )
        if scenes:
            opening = self._condense_sentence(f"Here is the key business story: {title}. {scenes[0].narration}", limit_words=20)
            scenes[0].narration = opening
            scenes[0].subtitle = opening
        return scenes

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        parts = [item.strip() for item in re.split(r"(?<=[.!?])\s+", text) if len(item.strip()) > 20]
        return parts or [text.strip()]

    @staticmethod
    def _short_title(text: str, fallback: str) -> str:
        words = text.split()[:5]
        return " ".join(words).strip(" .,:;") or fallback

    @staticmethod
    def _condense_sentence(text: str, limit_words: int) -> str:
        words = text.split()
        if len(words) <= limit_words:
            return text.strip()
        return " ".join(words[:limit_words]).strip(" ,;:.") + "..."
