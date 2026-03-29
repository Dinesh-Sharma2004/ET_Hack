# API Design

## Gateway conventions

- Base path: `/api`
- Auth: `Authorization: Bearer <jwt>`
- Correlation header: `X-Request-ID`
- Rate-limit headers:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`

## Feed and personalization

### `GET /api/news`

Query params:

- `category`
- `stock`
- `interest`
- `search`
- `offset`
- `limit`

Response:

```json
{
  "items": [],
  "total": 120,
  "offset": 0,
  "limit": 10,
  "highlights": [],
  "trending_topics": ["AI", "BFSI"]
}
```

### `GET /api/news/dashboard`

- Personalized homepage payload with feed, trending, and highlights.

### `GET /api/recommendations`

- Returns role-aware and profile-aware ranked cards plus filter options.

### `GET /api/profile`

- Returns stored user preferences and portfolio symbols.

### `PUT /api/profile`

- Updates user preferences.

### `POST /api/profile/portfolio`

- Upload portfolio CSV and return recommendations plus updated profile.

## RAG and briefings

### `GET /api/briefing/{topic}`

- Returns a topic-centric AI briefing page.

### `POST /api/briefing/{topic}/chat`

Request:

```json
{
  "question": "What are the biggest risks next quarter?",
  "mode": "expert",
  "history": []
}
```

### `POST /api/rag/query`

Suggested production endpoint for generic agentic retrieval:

```json
{
  "query": "How is AI capex affecting Indian IT exporters?",
  "user_id": "user-123",
  "top_k": 8,
  "filters": {
    "language": "English",
    "categories": ["AI", "Enterprise"]
  }
}
```

## Story and graph APIs

### `GET /api/story/{id}`

- Returns timeline, graph nodes/edges, and prediction prompts.

### `GET /api/story/{id}/graph`

- Suggested dedicated graph endpoint for interactive canvases.

### `GET /api/story/{id}/timeline`

- Suggested dedicated timeline endpoint with pagination for long arcs.

## Video APIs

### `GET /api/video`

- Returns generated video cards.

### `GET /api/video/{id}`

- Returns storyboard, script, highlights, and related articles.

### `POST /api/video/{id}/render`

- Suggested production endpoint to queue rendering.

## Translation APIs

### `POST /api/translate`

```json
{
  "article_id": "art-002",
  "language": "Hindi",
  "mode": "contextual"
}
```

## Internal microservice APIs

### `POST /internal/ingestion/article`

- Canonical normalized article payload.

### `POST /internal/embeddings/upsert`

- Push article chunks and vectors into vector DB.

### `POST /internal/graph/upsert`

- Persist extracted entities and relationships.

### `POST /internal/recommendations/recompute`

- Rebuild user candidate pools or experiment cohorts.
