from fastapi import FastAPI, Response, HTTPException, Request, Header, Depends
from .settings import Settings
from .vertex_ai_client import VertexAIClient
from .pydantic_models import PromptRequest, PromptResponse
from pydantic import ValidationError
settings = Settings()  # type: ignore - Pydantic loads from .env at runtime, Pylance can't see this.
import logging 
from contextlib import asynccontextmanager
#rate limiting imports
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import secrets

CORRECT_API_KEY = settings.BACKEND_API_KEY
REDIS_URL = settings.REDIS_URL

async def verify_api_key(api_key_header: str | None = Header(None, alias = "X-API-KEY")):
    if not api_key_header:
        raise HTTPException(status_code = 401, detail = "API KEY MISSING")
    if not secrets.compare_digest(api_key_header, CORRECT_API_KEY):
        raise HTTPException(status_code = 401, detail = "API KEY INVALID")

def setup_logging():
    """config logging for the backend app"""
    root_logger = logging.getLogger()

    root_logger.setLevel(logging.INFO)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializing Vertex AI Client on Startup to prevent crash"""
    setup_logging()
    logger.info("application startup sequence initiated")
    try:
        app.state.vertex_ai_client = VertexAIClient(settings)
        logger.info("Vertex client initialized successfully")
    except Exception as e:
        #any failure we log error
        logger.critical(f"CRITICAL: failed to initialize Vertex AI Client during startup: {e}", exc_info=True)
        app.state.vertex_ai_client = None
    try:
        redis_conn = await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis_conn)
    except Exception as e:
        logger.error(f"CRITICAL: redis connection uninitialized")
        raise

    yield
    logger.info("Application shutdown sequence initiated")

app = FastAPI(lifespan=lifespan)


@app.post("/api/v1/generate-prompt")
async def generate_prompt(request: PromptRequest, http_request:Request, ratelimits: None = Depends(RateLimiter(times=20, minutes=1)), api_verification: None = Depends(verify_api_key))->PromptResponse:
    vertex_ai_client = http_request.app.state.vertex_ai_client

    if not vertex_ai_client:
        logger.error("reject request since Vertex Ai Client not available")
        raise HTTPException(status_code = 503, detail = "Service temporarily unavailable due to configuration error")
                     
    user_query = request.user_query
    logger.info(f"Received request payload: {request.dict()}")
    try:
        llm_response = vertex_ai_client.generate_prompt(user_query)
        return PromptResponse(augmented_prompt=llm_response)
    except ValidationError as e:
        logger.error(f"LLM response validation failed: {e}")
        raise HTTPException(
            status_code = 502,
            detail="API returned invalid response"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code = 500, detail = "Internal server error")


    
@app.get("/api/v1/health")
async def show_health():
    return Response(status_code=200)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon_no_content():
    return Response(status_code=204)

