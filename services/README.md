# Extracted Backend Services

This folder starts the transition from the current gateway-style backend to runnable service slices.

## Services

- `api-gateway`
  - Fronts the extracted services and exposes a stable client-facing API surface.
- `ingestion-service`
  - Handles normalized article intake, batch ingestion previews, and stream event previews.
- `rag-service`
  - Handles hybrid retrieval, topic briefings, and briefing chat answers.
- `personalization-service`
  - Handles ranked feed generation, profile access, and recommendation explainability.
- `translation-service`
  - Handles contextual and literal Indian-language article translation.
- `video-service`
  - Handles AI video list and detail/storyboard generation.
- `news-service`
  - Handles news feed and dashboard metadata.
- `profile-service`
  - Handles persisted profile reads, updates, and portfolio upload workflows.
- `story-service`
  - Handles story arc, timeline, and relationship graph responses.
- `recommendations-service`
  - Handles ranked feed generation and recommendation explainability.
- `shared-lib`
  - Common repository access, models, retrieval logic, personalization logic, and explainability helpers.

## Run locally

### API gateway

```powershell
cd services/api-gateway
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH = "..\\shared-lib"
uvicorn app.main:app --host 127.0.0.1 --port 8100
```

### Ingestion service

```powershell
cd services/ingestion-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH = "..\\shared-lib"
uvicorn app.main:app --host 127.0.0.1 --port 8101
```

### RAG service

```powershell
cd services/rag-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH = "..\\shared-lib"
uvicorn app.main:app --host 127.0.0.1 --port 8102
```

### Personalization service

```powershell
cd services/personalization-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH = "..\\shared-lib"
uvicorn app.main:app --host 127.0.0.1 --port 8103
```

### Translation service

```powershell
cd services/translation-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH = "..\\shared-lib"
uvicorn app.main:app --host 127.0.0.1 --port 8104
```

### Video service

```powershell
cd services/video-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH = "..\\shared-lib"
uvicorn app.main:app --host 127.0.0.1 --port 8105
```

### News service

```powershell
cd services/news-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH = "..\\shared-lib"
uvicorn app.main:app --host 127.0.0.1 --port 8106
```

### Profile service

```powershell
cd services/profile-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH = "..\\shared-lib"
uvicorn app.main:app --host 127.0.0.1 --port 8107
```

### Story service

```powershell
cd services/story-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH = "..\\shared-lib"
uvicorn app.main:app --host 127.0.0.1 --port 8108
```

### Recommendations service

```powershell
cd services/recommendations-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH = "..\\shared-lib"
uvicorn app.main:app --host 127.0.0.1 --port 8109
```

## Compose

```powershell
cd services
docker compose -f docker-compose.services.yml up --build
```

## Next extraction targets

- `knowledge-processing-service`
- frontend migration to consume only the gateway
- gateway auth refresh flow and role policies
