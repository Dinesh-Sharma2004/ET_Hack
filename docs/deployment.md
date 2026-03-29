# Deployment Guide

## Monorepo shape

```text
backend/                  current gateway-style app and sample services
frontend/                 React client
shared/                   sample/demo datasets
docs/                     architecture, API, deployment docs
infra/
  k8s/                    kubernetes manifests
  monitoring/             Prometheus + Grafana assets
  mlops/                  MLflow and experiment configs
.github/workflows/        CI/CD pipelines
```

## Recommended production stack

- Edge: Cloudflare or Fastly
- Gateway/API: FastAPI behind NGINX or managed ingress
- Async/event bus: Kafka
- Cache: Redis
- Primary DB: PostgreSQL
- Vector DB: Chroma for self-hosted demos, Pinecone/Weaviate for scale
- Graph DB: Neo4j Aura or self-hosted Neo4j
- Object store: S3-compatible
- Orchestration: Kubernetes
- CI/CD: GitHub Actions + Argo CD or Helm deploys

## Local development

### Backend

```powershell
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

## Kubernetes deployment sequence

1. Build container images for gateway, workers, and frontend.
2. Push images to container registry.
3. Apply `namespace.yaml`, `configmap.yaml`, and `secrets`.
4. Deploy Redis/Postgres/Neo4j/vector DB or bind managed services.
5. Apply `api-gateway.yaml`, `frontend.yaml`, and worker deployments.
6. Apply ingress and autoscaling policies.
7. Apply monitoring stack.

## Operational controls

- Autoscale chat and retrieval pods on CPU + latency.
- Separate batch enrichment workers from low-latency APIs.
- Version models and prompts in MLflow.
- Record experiment IDs in recommendation responses.

## A/B testing loop

1. Assign user to experiment bucket.
2. Log shown recommendations and clicked outcomes.
3. Compare CTR, dwell time, saves, and downstream retention.
4. Promote winning rankers with rollback safety.
