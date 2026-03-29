# MyET AI

MyET AI is an AI-first business news intelligence platform that turns static reporting into personalized feeds, interactive briefings, evolving story arcs, multilingual explainers, and article-to-video outputs. The current repository now includes an upgraded extracted-services slice with dynamic RSS ingestion, PostgreSQL-backed storage, FAISS-backed retrieval, model-driven translation, behavior-aware recommendations, and on-demand MP4 generation.

## Capabilities

- Personalized AI newsroom with profile, portfolio, and semantic ranking
- News Navigator briefings with FAQs and conversational follow-up hooks
- Story Arc Tracker with timeline and entity relationship graph scaffolding
- AI video studio contracts for script, TTS, chart, subtitle, and FFmpeg orchestration
- Vernacular business adaptation for Hindi, Tamil, Telugu, and Bengali
- Analytics layer for retention, audience segments, and alerts

## Project structure

```text
backend/
  app/
    api/
    core/
    schemas/
    services/
    tasks/
  tests/
frontend/
  src/
    api/
    components/
    pages/
    styles/
shared/
  sample_data/
services/
  ingestion-service/
  rag-service/
  personalization-service/
  shared-lib/
docs/
infra/
docker-compose.yml
```

## Production architecture assets

- System architecture: `docs/system-architecture.md`
- API design: `docs/api-design.md`
- Deployment guide: `docs/deployment.md`
- Extracted service slice: `services/README.md`
- Kubernetes manifests: `infra/k8s/`
- Monitoring and MLOps notes: `infra/monitoring/`, `infra/mlops/`
- CI pipeline: `.github/workflows/ci.yml`

## Tech stack rationale

- FastAPI: low-latency Python APIs with strong typing for AI services.
- React + Vite: fast modular frontend with route-based code splitting.
- Redis + Celery: simple async orchestration for media and enrichment tasks.
- Chroma / Pinecone / FAISS: vector retrieval for hybrid RAG.
- Neo4j / NetworkX: story graph and entity relationship tracking.
- Kafka: scalable event backbone for ingestion and enrichment.
- Kubernetes: service isolation, autoscaling, and fault tolerance.
- MLflow + Prometheus + Grafana: model tracking and production observability.

## Local setup

### Dynamic service prerequisites

- PostgreSQL 16+
- `ffmpeg` available on `PATH`
- Python virtual environments for the extracted services
- Model downloads on first use for:
  - `sentence-transformers/all-MiniLM-L6-v2`
  - MarianMT / mBART translation models
- Optional: `OPENAI_API_KEY` if you want to replace the local deterministic briefing synthesis with hosted generation in a later pass

### Environment

Copy values from [backend/.env.example](d:/ET_Hackathon/backend/.env.example) or export these variables before starting services:

```bash
DATABASE_URL=postgresql+psycopg://myet:myet@localhost:5432/myet
RSS_FEEDS=https://news.google.com/rss/search?q=business&hl=en-IN&gl=IN&ceid=IN:en,https://news.google.com/rss/search?q=finance&hl=en-IN&gl=IN&ceid=IN:en
INGEST_REFRESH_MINUTES=15
VIDEO_PUBLIC_BASE_URL=http://127.0.0.1:8105
```

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker compose up --build
```

This starts:

- PostgreSQL
- API gateway
- ingestion, news, profile, recommendations, RAG, story, translation, video services
- frontend dev server

## Dynamic pipeline notes

### Ingestion

- `ingestion-service` fetches live RSS feeds on startup and refreshes periodically
- normalized articles are persisted in PostgreSQL

### Recommendations

- rankings now combine semantic similarity, behavior signals from `user_behavior.json`, portfolio overlap, and recency
- filter metadata is returned for the newsroom page

### RAG

- articles are chunked dynamically
- embeddings are generated with `sentence-transformers`
- chunks are indexed in FAISS under `shared/runtime/vector/`
- briefings now return the richer `report` shape expected by the frontend

### Translation

- the translation service now uses MarianMT / mBART models instead of hardcoded strings

### Video generation

- the video service generates:
  - a script from article text
  - TTS narration
  - chart/text slide frames
  - an actual MP4 through `ffmpeg`
- outputs are written under `shared/runtime/videos/`

## Example API calls

### 1. Get a demo token from the gateway

```bash
curl -X POST http://127.0.0.1:8100/auth/demo-login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"demo-user\",\"role\":\"investor\"}"
```

### 2. Run a dynamic briefing

```bash
curl http://127.0.0.1:8100/api/briefing/markets \
  -H "Authorization: Bearer <token>"
```

### 3. Translate an article dynamically

```bash
curl -X POST http://127.0.0.1:8100/api/translate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d "{\"article_id\":\"<article-id>\",\"language\":\"Hindi\",\"mode\":\"contextual\"}"
```

### 4. Generate a real video file

```bash
curl http://127.0.0.1:8100/api/video/video-<article-id> \
  -H "Authorization: Bearer <token>"
```

The returned payload includes a `video_url` pointing to the generated MP4.

## Demo flow

1. Open the web app to see a personalized dashboard driven by the seeded user profile.
2. Inspect the Deep Briefings section for cross-article synthesis, risks, and opportunities.
3. Explore Story Tracker to see timeline and what-next predictions.
4. Review AI Videos for the production storyboard that feeds a real render worker.
5. Check the Vernacular Engine cards for context-aware regional-language adaptation.

## Production upgrade path

- Replace the local embedding helper with OpenAI or sentence-transformers embeddings stored in Chroma or FAISS.
- Persist user activity and portfolio uploads in PostgreSQL plus object storage.
- Back the story graph with Neo4j and NER-driven entity extraction jobs.
- Connect Celery video tasks to FFmpeg, TTS, subtitle generation, and chart rendering.
- Add auth, alerting, and push notification services.
- Move from a gateway-style app to dedicated ingestion, RAG, personalization, video, and translation services over Kafka.
- The repository now includes initial runnable extractions for ingestion, RAG, and personalization under `services/`.
