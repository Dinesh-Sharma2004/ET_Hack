from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pyttsx3
from gtts import gTTS
from moviepy import AudioFileClip

from ..config import VIDEO_TTS_PROVIDER
from ..utils import get_logger, stable_hash


logger = get_logger("myet.video.tts")


@dataclass
class NarrationTrack:
    text: str
    audio_path: str
    duration_seconds: float


class NarrationEngine:
    def synthesize_scenes(self, scene_plans: list[dict[str, object]], output_dir: Path) -> list[NarrationTrack]:
        output_dir.mkdir(parents=True, exist_ok=True)
        tracks: list[NarrationTrack] = []
        for scene in scene_plans:
            text = str(scene["narration"]).strip()
            audio_stem = output_dir / stable_hash(text)
            audio_path = self._ensure_audio(text, audio_stem)
            duration = self._duration(audio_path)
            tracks.append(NarrationTrack(text=text, audio_path=str(audio_path), duration_seconds=max(duration, 2.2)))
        return tracks

    def _ensure_audio(self, text: str, audio_stem: Path) -> Path:
        mp3_path = audio_stem.with_suffix(".mp3")
        wav_path = audio_stem.with_suffix(".wav")
        if mp3_path.exists():
            return mp3_path
        if wav_path.exists():
            return wav_path
        providers = ["local", "network"] if VIDEO_TTS_PROVIDER == "local" else ["network", "local"]
        for provider in providers:
            try:
                if provider == "local":
                    engine = pyttsx3.init()
                    engine.setProperty("rate", 178)
                    engine.save_to_file(text, str(wav_path))
                    engine.runAndWait()
                    return wav_path
                tts = gTTS(text=text, lang="en", tld="co.in")
                tts.save(str(mp3_path))
                return mp3_path
            except Exception as exc:  # noqa: BLE001
                logger.warning("%s TTS failed, trying fallback: %s", provider, exc)
        raise RuntimeError("Unable to synthesize narration audio with local or network TTS.")

    @staticmethod
    def _duration(audio_path: Path) -> float:
        with AudioFileClip(str(audio_path)) as clip:
            return float(clip.duration or 0)
