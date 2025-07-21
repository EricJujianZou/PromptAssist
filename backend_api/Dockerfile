FROM python:3.11-slim
WORKDIR /app
#layer caching - if everything before and including the i'th layer has not changed, Docker will just reuse the same layer from its cache
#instead of running the instruction for it again.
#Therefore, files that rarely change, such as .env, .requirements, should be placed first
COPY requirements_backend.txt .
RUN pip install --no-cache-dir -r requirements_backend.txt
COPY . .
EXPOSE 8000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}