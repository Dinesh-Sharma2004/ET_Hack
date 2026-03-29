# My ET - AI Personalized Newsroom

## Vision

My ET is an AI-native business news platform that turns raw reporting into personalized, explainable, multi-modal intelligence for investors, founders, analysts, and students.

## Architecture diagram

```text
                                +----------------------+
                                |  Web / Mobile Apps   |
                                |  React + Edge CDN    |
                                +----------+-----------+
                                           |
                                  HTTPS / WebSocket
                                           |
                              +------------v-------------+
                              |       API Gateway        |
                              | Auth, rate-limit, cache  |
                              +--+---------+----------+--+
                                 |         |          |
                 +---------------+         |          +----------------+
                 |                         |                           |
       +---------v--------+      +---------v----------+      +---------v---------+
       | personalization  |      |     rag-service    |      | translation-svc   |
       | profiles, ranker |      | retriever, agents  |      | contextual LLM    |
       +---------+--------+      +---------+----------+      +---------+---------+
                 |                         |                           |
                 |                         |                           |
       +---------v---------+     +--------v---------+       +---------v----------+
       | profile store     |     | vector database  |       | prompt templates   |
       | postgres / redis  |     | chroma/pinecone  |       | language packs     |
       +-------------------+     +--------+---------+       +--------------------+
                                            |
                                +-----------v-----------+
                                | knowledge-processing  |
                                | chunking / NER / KG   |
                                +-----------+-----------+
                                            |
                   +------------------------+------------------------+
                   |                                                 |
          +--------v----------+                            +---------v----------+
          | metadata store    |                            | graph store        |
          | postgres / s3     |                            | neo4j / networkx   |
          +--------+----------+                            +---------+----------+
                   |                                                 |
                   +------------------------+------------------------+
                                            |
                                 +----------v----------+
                                 | ingestion-service   |
                                 | RSS / APIs / PDFs   |
                                 +----------+----------+
                                            |
                                 +----------v----------+
                                 | Kafka / batch jobs  |
                                 | stream + replay     |
                                 +---------------------+

                       +--------------------------------------------+
                       | video-service                              |
                       | summarization -> script -> TTS -> FFmpeg   |
                       +--------------------------------------------+

                       +--------------------------------------------+
                       | Monitoring / MLOps                         |
                       | Prometheus, Grafana, MLflow, OpenTelemetry |
                       +--------------------------------------------+
```

## Service responsibilities

### `ingestion-service`

- Pull RSS/API feeds, PDFs, and article bodies.
- Validate source freshness and normalize schema.
- Publish canonical article events to Kafka.

### `knowledge-processing-service`

- Chunk articles into semantic blocks.
- Run NER, event extraction, topic tagging, sentiment scoring.
- Persist chunks, metadata, embeddings, and graph edges.

### `rag-service`

- Execute hybrid search across dense embeddings and keyword indices.
- Run agentic query decomposition for complex follow-up questions.
- Generate briefings, Q&A, and explainability traces.

### `personalization-service`

- Maintain user profiles, reading behavior, and preference weights.
- Rank articles using behavior + content + portfolio signals.
- Support recommendation experiments and feedback loops.

### `video-service`

- Generate text summaries, scripts, voiceovers, chart prompts, subtitles.
- Orchestrate FFmpeg render jobs with asynchronous workers.

### `translation-service`

- Translate and rewrite content in Hindi, Tamil, Telugu, and Bengali.
- Support literal and contextual modes with tone controls.

## Data flow

1. `ingestion-service` captures new content and emits `article.ingested`.
2. `knowledge-processing-service` enriches content and emits:
   - `article.chunked`
   - `article.embedded`
   - `article.graph.updated`
3. `personalization-service` updates candidate pools and user scoring tables.
4. `rag-service` serves chat, briefing, and retrieval requests under 2 seconds.
5. `video-service` consumes article or briefing events for asynchronous rendering.
6. `translation-service` serves low-latency contextual localization.

## Scaling strategy

### Stateless APIs

- Run gateway and retrieval APIs as horizontally scalable deployments.
- Cache hot queries in Redis.

### Event-driven workloads

- Use Kafka topics for ingestion, enrichment, embeddings, graph updates, and renders.
- Use dead-letter queues for poison records and replay support.

### Storage

- PostgreSQL for metadata, users, preferences, audit state.
- Object storage for raw articles, PDFs, video assets, subtitles, charts.
- Vector DB for semantic retrieval.
- Neo4j for graph analytics and story arcs.

### Low latency targets

- API gateway: P95 under 150 ms for cached feed requests.
- Chat/briefing: P95 under 2 seconds with retrieval cache and precomputed summaries.
- Translation: P95 under 1 second for hot article variants.

## Security and reliability

- JWT auth plus refresh tokens.
- Request-level rate limiting and abuse detection.
- Signed URLs for media access.
- Audit logging for prompts, model versions, and recommendation outcomes.
- Blue/green deploys for low-risk releases.

## Explainability model

- Every recommendation should surface:
  - matched interests
  - portfolio overlap
  - similar articles read
  - freshness / sentiment / entity signals
- Every RAG answer should carry:
  - retrieved documents
  - retrieval strategy
  - model version
  - confidence / fallback state
