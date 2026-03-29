import base64
import asyncio
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from typing import Any

import httpx
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel


class BriefingRequest(BaseModel):
    question: str
    mode: str = "expert"
    history: list[str] = []


class TranslationRequest(BaseModel):
    article_id: str
    language: str = "Hindi"
    mode: str = "contextual"


class DemoLoginRequest(BaseModel):
    username: str = "demo-user"
    role: str = "investor"


@dataclass
class CircuitState:
    failures: int = 0
    opened_until: float = 0.0


app = FastAPI(title="MyET API Gateway", version="2.0.0")
bearer_scheme = HTTPBearer(auto_error=False)

INGESTION_URL = os.getenv("INGESTION_SERVICE_URL", "http://127.0.0.1:8101")
RAG_URL = os.getenv("RAG_SERVICE_URL", "http://127.0.0.1:8102")
PERSONALIZATION_URL = os.getenv("PERSONALIZATION_SERVICE_URL", "http://127.0.0.1:8103")
TRANSLATION_URL = os.getenv("TRANSLATION_SERVICE_URL", "http://127.0.0.1:8104")
VIDEO_URL = os.getenv("VIDEO_SERVICE_URL", "http://127.0.0.1:8105")
NEWS_URL = os.getenv("NEWS_SERVICE_URL", "http://127.0.0.1:8106")
PROFILE_URL = os.getenv("PROFILE_SERVICE_URL", "http://127.0.0.1:8107")
STORY_URL = os.getenv("STORY_SERVICE_URL", "http://127.0.0.1:8108")
RECOMMENDATIONS_URL = os.getenv("RECOMMENDATIONS_SERVICE_URL", "http://127.0.0.1:8109")

REQUEST_TIMEOUT = float(os.getenv("GATEWAY_REQUEST_TIMEOUT", "8"))
RETRY_ATTEMPTS = int(os.getenv("GATEWAY_RETRY_ATTEMPTS", "3"))
RETRY_BACKOFF_SECONDS = float(os.getenv("GATEWAY_RETRY_BACKOFF_SECONDS", "0.35"))
CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("GATEWAY_CIRCUIT_BREAKER_THRESHOLD", "3"))
CIRCUIT_BREAKER_RESET_SECONDS = float(os.getenv("GATEWAY_CIRCUIT_BREAKER_RESET_SECONDS", "15"))
AUTH_SECRET = os.getenv("GATEWAY_AUTH_SECRET", "myet-demo-secret")
TOKEN_TTL_SECONDS = int(os.getenv("GATEWAY_TOKEN_TTL_SECONDS", "43200"))
ALLOWED_ORIGINS = os.getenv(
    "GATEWAY_ALLOWED_ORIGINS",
    "http://127.0.0.1:5173,http://localhost:5173",
).split(",")

SERVICE_URLS = {
    "ingestion": INGESTION_URL,
    "rag": RAG_URL,
    "personalization": PERSONALIZATION_URL,
    "translation": TRANSLATION_URL,
    "video": VIDEO_URL,
    "news": NEWS_URL,
    "profile": PROFILE_URL,
    "story": STORY_URL,
    "recommendations": RECOMMENDATIONS_URL,
}

CIRCUITS: dict[str, CircuitState] = {name: CircuitState() for name in SERVICE_URLS}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _urlsafe_b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _urlsafe_b64decode(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")


def create_access_token(subject: str, role: str) -> str:
    payload = {
        "sub": subject,
        "role": role,
        "exp": int(time.time()) + TOKEN_TTL_SECONDS,
        "iss": "myet-api-gateway",
    }
    encoded_payload = _urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(AUTH_SECRET.encode("utf-8"), encoded_payload.encode("utf-8"), hashlib.sha256).digest()
    return f"{encoded_payload}.{_urlsafe_b64encode(signature)}"


def verify_access_token(token: str) -> dict[str, Any]:
    try:
        encoded_payload, encoded_signature = token.split(".", maxsplit=1)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed access token.") from exc

    expected_signature = hmac.new(
        AUTH_SECRET.encode("utf-8"),
        encoded_payload.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    actual_signature = _urlsafe_b64decode(encoded_signature)
    if not hmac.compare_digest(expected_signature, actual_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")

    try:
        payload = json.loads(_urlsafe_b64decode(encoded_payload).decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unreadable access token.") from exc

    if payload.get("exp", 0) < time.time():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token expired.")
    return payload


async def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token.")
    return verify_access_token(credentials.credentials)


def service_status_snapshot() -> dict[str, dict[str, Any]]:
    now = time.time()
    return {
        name: {
            "base_url": SERVICE_URLS[name],
            "failures": state.failures,
            "circuit_open": state.opened_until > now,
            "opened_until": state.opened_until or None,
        }
        for name, state in CIRCUITS.items()
    }


def check_circuit(service_name: str) -> None:
    state = CIRCUITS[service_name]
    if state.opened_until > time.time():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service_name} is temporarily unavailable while the gateway circuit breaker is open.",
        )
    if state.opened_until and state.opened_until <= time.time():
        state.opened_until = 0.0
        state.failures = 0


def record_success(service_name: str) -> None:
    state = CIRCUITS[service_name]
    state.failures = 0
    state.opened_until = 0.0


def record_failure(service_name: str) -> None:
    state = CIRCUITS[service_name]
    state.failures += 1
    if state.failures >= CIRCUIT_BREAKER_THRESHOLD:
        state.opened_until = time.time() + CIRCUIT_BREAKER_RESET_SECONDS


async def fetch_json(service_name: str, method: str, path: str, **kwargs) -> dict | list:
    check_circuit(service_name)
    base_url = SERVICE_URLS[service_name]
    last_error: Exception | None = None

    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.request(method, f"{base_url}{path}", **kwargs)

            if response.status_code >= 500:
                raise httpx.HTTPStatusError(
                    f"{service_name} returned {response.status_code}",
                    request=response.request,
                    response=response,
                )
            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail=response.text or "Upstream request failed.")

            record_success(service_name)
            return response.json()
        except HTTPException:
            raise
        except (httpx.RequestError, httpx.HTTPStatusError) as exc:
            last_error = exc
            record_failure(service_name)
            if attempt < RETRY_ATTEMPTS:
                await asyncio.sleep(RETRY_BACKOFF_SECONDS * attempt)

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"Gateway could not reach {service_name} after {RETRY_ATTEMPTS} attempts: {last_error}",
    )


@app.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "service": "api-gateway", "resilience": service_status_snapshot()}


@app.post("/auth/demo-login")
async def demo_login(payload: DemoLoginRequest) -> dict[str, Any]:
    token = create_access_token(payload.username, payload.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": TOKEN_TTL_SECONDS,
        "user": {"username": payload.username, "role": payload.role},
    }


@app.get("/api/news")
async def get_news(
    category: str | None = None,
    stock: str | None = None,
    interest: str | None = None,
    search: str | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=20),
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, object]:
    return await fetch_json(
        "news",
        "GET",
        "/news",
        params={
            "category": category,
            "stock": stock,
            "interest": interest,
            "search": search,
            "offset": offset,
            "limit": limit,
        },
    )


@app.get("/api/news/dashboard")
async def get_dashboard(_: dict[str, Any] = Depends(require_auth)) -> dict[str, object]:
    dashboard = await fetch_json("news", "GET", "/news/dashboard")
    recommendations = await fetch_json("recommendations", "POST", "/recommendations", json={})
    profile = await fetch_json("profile", "GET", "/profile")
    avg_score = 0.0
    if recommendations.get("items"):
        avg_score = sum(item.get("relevance_score", 0.0) for item in recommendations["items"][:4]) / min(
            len(recommendations["items"][:4]),
            4,
        )
    return {
        "profile": profile,
        "feed": recommendations["items"][:4],
        "highlights": dashboard["highlights"] + [
            {
                "label": "Signal Match",
                "value": f"{round(avg_score * 100)}%",
                "delta": f"{len(recommendations.get('items', []))} ranked",
            }
        ],
        "trending": dashboard["trending"],
    }


@app.get("/api/recommendations")
async def get_recommendations(
    industry: str | None = None,
    stock: str | None = None,
    interest: str | None = None,
    _: dict[str, Any] = Depends(require_auth),
) -> dict | list:
    return await fetch_json(
        "recommendations",
        "POST",
        "/recommendations",
        json={"industry": industry, "stock": stock, "interest": interest},
    )


@app.get("/api/profile")
async def get_profile(_: dict[str, Any] = Depends(require_auth)) -> dict | list:
    return await fetch_json("profile", "GET", "/profile")


@app.put("/api/profile")
async def update_profile(payload: dict[str, object], _: dict[str, Any] = Depends(require_auth)) -> dict | list:
    return await fetch_json("profile", "PUT", "/profile", json=payload)


@app.post("/api/profile/portfolio")
async def upload_portfolio(
    file: UploadFile = File(...),
    _: dict[str, Any] = Depends(require_auth),
) -> dict | list:
    content = await file.read()
    files = {"file": (file.filename or "portfolio.csv", content, file.content_type or "text/csv")}
    return await fetch_json("profile", "POST", "/profile/portfolio", files=files)


@app.get("/api/briefing/{topic}")
async def get_briefing(topic: str, _: dict[str, Any] = Depends(require_auth)) -> dict | list:
    return await fetch_json("rag", "GET", f"/briefing/{topic}")


@app.post("/api/briefing/{topic}/chat")
async def chat_briefing(
    topic: str,
    payload: BriefingRequest,
    _: dict[str, Any] = Depends(require_auth),
) -> dict | list:
    return await fetch_json("rag", "POST", f"/briefing/{topic}/chat", json=payload.model_dump())


@app.post("/api/translate")
async def translate(payload: TranslationRequest, _: dict[str, Any] = Depends(require_auth)) -> dict | list:
    try:
        return await fetch_json("translation", "POST", "/translate", json=payload.model_dump())
    except HTTPException as exc:
        if exc.status_code != status.HTTP_503_SERVICE_UNAVAILABLE:
            raise
        from myet_shared.repository import SharedRepository
        from myet_shared.translation import VernacularEngine

        repository = SharedRepository()
        article = repository.get_article(payload.article_id)
        if not article:
            raise HTTPException(status_code=404, detail=f"Article {payload.article_id} not found.")
        return VernacularEngine().translate(article, payload.language, payload.mode)


@app.get("/api/story/{story_id}")
async def get_story(story_id: str, _: dict[str, Any] = Depends(require_auth)) -> dict | list:
    return await fetch_json("story", "GET", f"/story/{story_id}")


@app.get("/api/video")
async def list_videos(_: dict[str, Any] = Depends(require_auth)) -> dict | list:
    return await fetch_json("video", "GET", "/videos")


@app.get("/api/video/{video_id}")
async def get_video(video_id: str, _: dict[str, Any] = Depends(require_auth)) -> dict | list:
    return await fetch_json("video", "GET", f"/videos/{video_id}")


@app.get("/api/ingestion/batch")
async def batch_ingest(_: dict[str, Any] = Depends(require_auth)) -> dict | list:
    return await fetch_json("ingestion", "GET", "/ingest/batch")


@app.get("/api/service-map")
async def service_map(_: dict[str, Any] = Depends(require_auth)) -> dict[str, object]:
    return {
        "gateway": "http://127.0.0.1:8100",
        "services": service_status_snapshot(),
    }
