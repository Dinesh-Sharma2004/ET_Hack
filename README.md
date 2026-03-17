# MyET AI

MyET AI is an AI-first business news intelligence platform that turns static reporting into personalized feeds, interactive briefings, evolving story arcs, multilingual explainers, and article-to-video storyboards.

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
docker-compose.yml
```

## Local setup

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
