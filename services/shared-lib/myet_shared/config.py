import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
SHARED_DIR = ROOT_DIR / "shared"
RUNTIME_DIR = SHARED_DIR / "runtime"
VECTOR_DIR = RUNTIME_DIR / "vector"
VIDEO_DIR = RUNTIME_DIR / "videos"
DB_DIR = RUNTIME_DIR / "db"
TRANSLATION_CACHE_DIR = RUNTIME_DIR / "translations"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(DB_DIR / 'myet.db').as_posix()}")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
TRANSLATION_MODEL_HI = os.getenv("TRANSLATION_MODEL_HI", "Helsinki-NLP/opus-mt-en-hi")
TRANSLATION_MODEL_BN = os.getenv("TRANSLATION_MODEL_BN", "Helsinki-NLP/opus-mt-en-bn")
TRANSLATION_MODEL_TA = os.getenv("TRANSLATION_MODEL_TA", "facebook/mbart-large-50-many-to-many-mmt")
TRANSLATION_MODEL_TE = os.getenv("TRANSLATION_MODEL_TE", "facebook/mbart-large-50-many-to-many-mmt")
TRANSLATION_LOCAL_ONLY_FIRST = os.getenv("TRANSLATION_LOCAL_ONLY_FIRST", "1") == "1"
TRANSLATION_ALLOW_DOWNLOADS = os.getenv("TRANSLATION_ALLOW_DOWNLOADS", "1") == "1"
TRANSLATION_WARM_LANGUAGES = [
    item.strip()
    for item in os.getenv("TRANSLATION_WARM_LANGUAGES", "Hindi").split(",")
    if item.strip()
]
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
RSS_FEEDS = [
    item.strip()
    for item in os.getenv(
        "RSS_FEEDS",
        ",".join(
            [
                "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
                "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
                "https://economictimes.indiatimes.com/tech/funding/rssfeeds/78570550.cms",
                "https://economictimes.indiatimes.com/tech/startups/rssfeeds/78570540.cms",
                "https://economictimes.indiatimes.com/mf/mf-news/rssfeeds/1107225967.cms",
            ]
        ),
    ).split(",")
    if item.strip()
]
INGEST_REFRESH_MINUTES = int(os.getenv("INGEST_REFRESH_MINUTES", "15"))
VIDEO_PUBLIC_BASE_URL = os.getenv("VIDEO_PUBLIC_BASE_URL", "http://127.0.0.1:8105")

for directory in [RUNTIME_DIR, VECTOR_DIR, VIDEO_DIR, DB_DIR, TRANSLATION_CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
