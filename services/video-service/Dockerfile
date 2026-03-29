FROM python:3.12-slim

WORKDIR /app

COPY services/video-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/video-service/app ./app
COPY services/shared-lib /shared-lib
COPY shared /shared

ENV PYTHONPATH=/shared-lib

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8105"]
