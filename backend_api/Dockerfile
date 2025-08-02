FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH /app
#layer caching - if everything before and including the i'th layer has not changed, Docker will just reuse the same layer from its cache
#instead of running the instruction for it again.
#Therefore, files that rarely change, such as .env, .requirements, should be placed first
COPY backend_api/requirements_backend.txt .
RUN pip install --no-cache-dir -r requirements_backend.txt
COPY backend_api/ /app/backend_api/
EXPOSE 8000
CMD uvicorn backend_api.main:app --host 0.0.0.0 --port ${PORT:-8000}