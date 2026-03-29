from __future__ import annotations

import os
from pathlib import Path

from myet_shared.config import VIDEO_DIR


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_VIDEO_SIZE = (1280, 720)
DEFAULT_IMAGE_SIZE = (512, 512)
DEFAULT_FPS = int(os.getenv("VIDEO_FPS", "15"))
DEFAULT_SCENE_COUNT = int(os.getenv("VIDEO_SCENE_COUNT", "5"))
CHROMA_COLLECTION = os.getenv("VIDEO_CHROMA_COLLECTION", "myet_video_chunks")
VIDEO_EMBED_MODEL = os.getenv("VIDEO_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
VIDEO_EMBED_LOCAL_ONLY_FIRST = os.getenv("VIDEO_EMBED_LOCAL_ONLY_FIRST", "1") == "1"
VIDEO_EMBED_ALLOW_DOWNLOADS = os.getenv("VIDEO_EMBED_ALLOW_DOWNLOADS", "0") == "1"
VIDEO_DIFFUSION_MODEL = os.getenv("VIDEO_DIFFUSION_MODEL", "runwayml/stable-diffusion-v1-5")
VIDEO_USE_DIFFUSION = os.getenv("VIDEO_USE_DIFFUSION", "0") == "1"
VIDEO_LLM_MODEL = os.getenv("VIDEO_LLM_MODEL", "google/flan-t5-small")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")
VIDEO_TTS_PROVIDER = os.getenv("VIDEO_TTS_PROVIDER", "local")
VIDEO_PREGENERATE_COUNT = int(os.getenv("VIDEO_PREGENERATE_COUNT", "2"))
WATERMARK_TEXT = os.getenv("VIDEO_WATERMARK_TEXT", "MyET AI")
BACKGROUND_MUSIC_PATH = os.getenv("VIDEO_BACKGROUND_MUSIC")
VIDEO_CACHE_DIR = VIDEO_DIR
RAG_DIR_NAME = "rag"
IMAGE_DIR_NAME = "images"
SUBTITLE_DIR_NAME = "subtitles"
SCENE_DIR_NAME = "scenes"
MANIFEST_NAME = "manifest.json"
