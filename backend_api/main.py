from fastapi import FastAPI, Response
from .settings import Settings

settings = Settings()

app = FastAPI()

@app.get("/health")
async def read_root():
    """health check end point."""

    return {
        "status": "ok", 
        "message": "booga",
        "model": settings.LLM_MODEL_NAME,
        "vertex_project": settings.VERTEX_AI_PROJECT
    }

@app.get("/favicon.ico", include_in_schema=False)
async def favicon_no_content():
    return Response(status_code=204)

