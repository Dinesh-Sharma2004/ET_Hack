@echo off
set PYTHONPATH=d:\ET_Hackathon\services\shared-lib
set DATABASE_URL=postgresql+psycopg://myet:myet@localhost:5432/myet
set TRANSLATION_LOCAL_ONLY_FIRST=1
set TRANSLATION_ALLOW_DOWNLOADS=1
set TRANSLATION_WARM_LANGUAGES=Hindi
"d:\ET_Hackathon\backend\.venv\Scripts\python.exe" -m uvicorn services.translation-service.app.main:app --host 127.0.0.1 --port 8104
