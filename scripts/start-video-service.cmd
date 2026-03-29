@echo off
set PYTHONPATH=d:\ET_Hackathon\services\shared-lib
set DATABASE_URL=postgresql+psycopg://myet:myet@localhost:5432/myet
set VIDEO_PUBLIC_BASE_URL=http://127.0.0.1:8105
set VIDEO_USE_DIFFUSION=0
set VIDEO_EMBED_LOCAL_ONLY_FIRST=1
set VIDEO_EMBED_ALLOW_DOWNLOADS=0
set VIDEO_TTS_PROVIDER=network
set VIDEO_PREGENERATE_COUNT=2
"d:\ET_Hackathon\backend\.venv\Scripts\python.exe" -m uvicorn services.video-service.app.main:app --host 127.0.0.1 --port 8105
