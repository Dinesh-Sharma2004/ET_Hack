@echo off
set PYTHONPATH=d:\ET_Hackathon\services\shared-lib
set DATABASE_URL=postgresql+psycopg://myet:myet@localhost:5432/myet
set GATEWAY_AUTH_SECRET=myet-live-secret
set GATEWAY_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
set GATEWAY_REQUEST_TIMEOUT=180
set GATEWAY_RETRY_ATTEMPTS=1
"d:\ET_Hackathon\backend\.venv\Scripts\python.exe" -m uvicorn services.api-gateway.app.main:app --host 127.0.0.1 --port 8100
