# MyET AI Current Implementation

## Scope

This document describes the **current local implementation**, not the target architecture. It explains:

- which data files are actually used at runtime
- which data files are present but currently unused
- how the backend fetches that data
- what each frontend page is rendering from those backend responses
- current implementation gaps between UI intent and backend payloads

## Runtime data sources

The current app runs entirely on **local synthetic data**.

No live external APIs, RSS feeds, Kafka topics, vector databases, Neo4j instances, or third-party news sources are used in the current local runtime path.

The main runtime source is:

- [shared/sample_data/articles.json](d:/ET_Hackathon/shared/sample_data/articles.json)

The active profile source is:

- [shared/sample_data/user_profile.json](d:/ET_Hackathon/shared/sample_data/user_profile.json)

The active portfolio source is:

- [shared/sample_data/portfolio.csv](d:/ET_Hackathon/shared/sample_data/portfolio.csv)

Files present but **not currently consumed by the running services**:

- [shared/sample_data/user_behavior.json](d:/ET_Hackathon/shared/sample_data/user_behavior.json)
- [shared/sample_data/demo_portfolios.csv](d:/ET_Hackathon/shared/sample_data/demo_portfolios.csv)

## Shared repository behavior

All extracted services read from the same shared repository class:

- [services/shared-lib/myet_shared/repository.py](d:/ET_Hackathon/services/shared-lib/myet_shared/repository.py)

Current repository behavior:

- `load_articles()` reads `shared/sample_data/articles.json`
- `load_profile()` reads `shared/sample_data/user_profile.json`
- `save_profile()` writes back to `shared/sample_data/user_profile.json`
- `load_portfolio_symbols()` reads the first `symbol` column from `shared/sample_data/portfolio.csv`
- `save_portfolio_symbols()` overwrites `shared/sample_data/portfolio.csv`
- `search_articles()` filters locally in memory by `category`, `stock`, `interest`, and free-text substring matching

This means the current backend is effectively a **file-backed local demo system**.

## Synthetic files in use

### 1. Articles

- File: [shared/sample_data/articles.json](d:/ET_Hackathon/shared/sample_data/articles.json)
- Used by: news, recommendations, rag, translation, video, story, ingestion, profile recommendation-on-upload

Current shape:

- `id`
- `title`
- `summary`
- `content`
- `category`
- `entities`
- `sentiment`
- `language`
- `published_at`
- `source`
- `read_time_minutes`

Current article count: `12`

### 2. User profile

- File: [shared/sample_data/user_profile.json](d:/ET_Hackathon/shared/sample_data/user_profile.json)
- Used by: profile service, dashboard aggregation, recommendations ranking

Current behavior:

- loaded on app bootstrap
- updated through `/api/profile`
- overwritten when portfolio upload changes profile symbols

Important current state:

- the `portfolio_symbols` field currently contains profile names like `BALANCED INVESTOR`, `AI BULL`, and `INDIA GROWTH`, not stock tickers
- this happened because the upload path reads the **first CSV column only**, and the current saved portfolio file has profile labels in column 1

### 3. Portfolio file

- File: [shared/sample_data/portfolio.csv](d:/ET_Hackathon/shared/sample_data/portfolio.csv)
- Used by: profile service and repository helper methods

Current file contents are not ticker-clean. The `symbol` column currently contains:

- `BALANCED INVESTOR`
- `AI BULL`
- `INDIA GROWTH`

instead of actual equities like `NVDA`, `INFY`, etc.

So the current personalized ranking still runs, but the portfolio overlap signal is degraded.

## Synthetic files present but unused

### 1. User behavior

- File: [shared/sample_data/user_behavior.json](d:/ET_Hackathon/shared/sample_data/user_behavior.json)

What it contains:

- demo sessions
- clicked articles
- saved articles
- dwell time
- preferred mode

Current usage:

- not read by any extracted service
- not used by recommendations, ranking, or analytics in the live local stack

### 2. Demo portfolios

- File: [shared/sample_data/demo_portfolios.csv](d:/ET_Hackathon/shared/sample_data/demo_portfolios.csv)

What it contains:

- portfolio templates like `Balanced Investor`, `AI Bull`, `India Growth`
- actual ticker rows under each profile

Current usage:

- not read automatically by any service
- only relevant as a manual reference/demo asset

## Service-by-service runtime behavior

### Ingestion service

- File: [services/ingestion-service/app/main.py](d:/ET_Hackathon/services/ingestion-service/app/main.py)

Reads:

- `articles.json`

Behavior:

- `/ingest/batch` emits one synthetic `article.ingested` event per local article
- `/ingest/stream-preview` creates a fake event preview from the first five articles
- `/ingest/normalize` lowercases incoming payload keys

This is a synthetic ingestion simulator, not a real external feed consumer.

### News service

- File: [services/news-service/app/main.py](d:/ET_Hackathon/services/news-service/app/main.py)

Reads:

- `articles.json`
- `user_profile.json`

Behavior:

- `/news` filters local articles and paginates them
- `/news/dashboard` builds trending items from the highest-sentiment articles

No external fetch happens here.

### Recommendations service

- File: [services/recommendations-service/app/main.py](d:/ET_Hackathon/services/recommendations-service/app/main.py)
- Ranking logic: [services/shared-lib/myet_shared/personalization.py](d:/ET_Hackathon/services/shared-lib/myet_shared/personalization.py)
- Explainability logic: [services/shared-lib/myet_shared/explainability.py](d:/ET_Hackathon/services/shared-lib/myet_shared/explainability.py)

Reads:

- `articles.json`
- `user_profile.json`

Behavior:

- computes a lightweight embedding-like score using local text hashing helpers
- mixes semantic similarity, interest overlap, and portfolio overlap
- returns top `8` cards

Important note:

- it does **not** currently use `user_behavior.json`
- it does **not** return `filters` metadata, even though the frontend expects filter option arrays

### Profile service

- File: [services/profile-service/app/main.py](d:/ET_Hackathon/services/profile-service/app/main.py)

Reads/writes:

- `user_profile.json`
- `portfolio.csv`

Behavior:

- `/profile` returns the saved profile JSON
- `PUT /profile` merges and persists profile fields
- `POST /profile/portfolio` reads the uploaded CSV and uses the first column as symbols

Important note:

- if the uploaded file’s first column is not actual tickers, profile portfolio symbols become invalid for portfolio matching

### RAG service

- File: [services/rag-service/app/main.py](d:/ET_Hackathon/services/rag-service/app/main.py)
- Retrieval logic: [services/shared-lib/myet_shared/retrieval.py](d:/ET_Hackathon/services/shared-lib/myet_shared/retrieval.py)

Reads:

- `articles.json`

Behavior:

- `/rag/query` performs synthetic hybrid retrieval over the local article set
- `/briefing/{topic}` returns a simplified synthetic briefing
- `/briefing/{topic}/chat` returns a synthetic answer plus supporting retrieval hits

Important note:

- this is not using an LLM right now
- it is a deterministic local retrieval demo

### Story service

- File: [services/story-service/app/main.py](d:/ET_Hackathon/services/story-service/app/main.py)
- Story builder: [services/shared-lib/myet_shared/story.py](d:/ET_Hackathon/services/shared-lib/myet_shared/story.py)

Reads:

- `articles.json`

Behavior:

- finds related articles by substring matching on the story id
- builds:
  - a synthetic timeline
  - entity nodes
  - co-mention relationships
  - fixed “what next” bullets

This is generated from article metadata only. No graph database is involved in the current runtime.

### Translation service

- File: [services/translation-service/app/main.py](d:/ET_Hackathon/services/translation-service/app/main.py)
- Translation logic: [services/shared-lib/myet_shared/translation.py](d:/ET_Hackathon/services/shared-lib/myet_shared/translation.py)

Reads:

- `articles.json`

Behavior:

- resolves an article by `article_id`
- falls back to the first article if not found
- returns either:
  - a literal string wrapper, or
  - a hardcoded contextual translation map for Hindi, Tamil, Telugu, Bengali

Important note:

- current translations are synthetic templates, not model-generated outputs

### Video service

- File: [services/video-service/app/main.py](d:/ET_Hackathon/services/video-service/app/main.py)
- Video generator: [services/shared-lib/myet_shared/video.py](d:/ET_Hackathon/services/shared-lib/myet_shared/video.py)

Reads:

- `articles.json`

Behavior:

- `/videos` turns each article into a synthetic video card
- `/videos/{id}` returns:
  - fake scene breakdown
  - fake script lines
  - fake subtitles preview
  - related article payload

Important note:

- there is no real FFmpeg render, TTS, or actual video asset in the current local runtime

## API gateway behavior

- File: [services/api-gateway/app/main.py](d:/ET_Hackathon/services/api-gateway/app/main.py)

What it does now:

- exposes the frontend-facing API surface
- performs demo auth via `/auth/demo-login`
- requires bearer auth on `/api/*`
- applies retry + circuit breaker logic when calling upstream services
- adds CORS for the Vite frontend origins

It does not fetch external news itself. It only orchestrates local extracted services.

## Frontend page-to-data mapping

### Dashboard

- File: [frontend/src/pages/DashboardPage.jsx](d:/ET_Hackathon/frontend/src/pages/DashboardPage.jsx)
- Calls: `GET /api/news/dashboard`

Displays:

- aggregated profile from profile service
- top recommendation cards from recommendations service
- synthetic highlights from gateway/news service
- trending articles from news service

### Personalized Newsroom

- File: [frontend/src/pages/MyNewsPage.jsx](d:/ET_Hackathon/frontend/src/pages/MyNewsPage.jsx)
- Calls:
  - `GET /api/recommendations`
  - `GET /api/news`

Displays:

- recommendation cards
- infinite scroll news feed
- filter controls

Current limitation:

- the UI expects `recommendations.filters`
- the backend does not currently provide that field
- so dropdown option lists remain effectively empty

### Briefing page

- File: [frontend/src/pages/BriefingPage.jsx](d:/ET_Hackathon/frontend/src/pages/BriefingPage.jsx)
- Calls:
  - `GET /api/briefing/:topic`
  - `POST /api/briefing/:topic/chat`

Current backend response:

- `headline`
- `summary`
- `retrieved`

Current UI expectation:

- `report.headline`
- `report.summary`
- `report.insights`
- `report.risks`
- `report.opportunities`
- `related_articles`
- `suggested_questions`

So this page currently depends on a richer contract than the extracted RAG service returns.

The chat panel has a similar mismatch:

- [frontend/src/components/chat/ChatPanel.jsx](d:/ET_Hackathon/frontend/src/components/chat/ChatPanel.jsx) expects `payload.response`
- the current backend returns `answer` and `supporting_results`

### Story page

- File: [frontend/src/pages/StoryPage.jsx](d:/ET_Hackathon/frontend/src/pages/StoryPage.jsx)
- Calls: `GET /api/story/:id`

Displays:

- synthetic timeline
- entity chips
- co-mention relationship list
- sentiment chart
- fixed “what next” predictions

This page is backed correctly by the current story service contract.

### Videos pages

- Files:
  - [frontend/src/pages/VideosPage.jsx](d:/ET_Hackathon/frontend/src/pages/VideosPage.jsx)
  - [frontend/src/pages/VideoDetailPage.jsx](d:/ET_Hackathon/frontend/src/pages/VideoDetailPage.jsx)
- Calls:
  - `GET /api/video`
  - `GET /api/video/:id`

Displays:

- synthetic video cards
- placeholder player UI
- generated script
- synthetic scene cards
- related local article

### Vernacular page

- File: [frontend/src/pages/VernacularPage.jsx](d:/ET_Hackathon/frontend/src/pages/VernacularPage.jsx)
- Calls: `POST /api/translate`

Displays:

- translation for hardcoded `article_id: art-001`
- selected language
- selected mode

### Profile page

- File: [frontend/src/pages/ProfilePage.jsx](d:/ET_Hackathon/frontend/src/pages/ProfilePage.jsx)
- Calls:
  - `GET /api/profile`
  - `PUT /api/profile`
  - `POST /api/profile/portfolio`

Displays:

- editable profile fields
- current portfolio symbols
- upload modal with recommended articles after portfolio upload

## Auth and frontend bootstrap

- Frontend client: [frontend/src/api/client.js](d:/ET_Hackathon/frontend/src/api/client.js)

Current behavior:

- frontend auto-creates a demo session through `/auth/demo-login`
- stores bearer token in localStorage
- sends `Authorization: Bearer ...` on every gateway request
- retries once on `401`

## Current implementation summary

What is real in the current implementation:

- multi-page React frontend
- extracted FastAPI services
- gateway auth, CORS, retries, circuit breaker
- local end-to-end service orchestration
- file-backed synthetic article/profile/portfolio state

What is synthetic or mocked:

- news corpus
- translations
- video generation output
- RAG synthesis
- story forecasting bullets
- ingestion events

What exists but is not yet wired into runtime:

- `user_behavior.json`
- `demo_portfolios.csv`
- live external news feeds
- vector database
- graph database
- real LLM generation
- real TTS/video rendering

## Suggested next cleanup steps

1. Fix `portfolio.csv` and `user_profile.json` so portfolio symbols store actual tickers again.
2. Wire `user_behavior.json` into recommendations scoring.
3. Normalize the briefing and chat API contracts so they match the frontend page expectations.
4. Add filter metadata to the recommendations response for the newsroom page.
5. Decide whether `demo_portfolios.csv` should become a real seed input or remain documentation-only demo data.
