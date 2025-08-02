from fastapi import FastAPI, Response, HTTPException, Request
from .settings import Settings
from .vertex_ai_client import VertexAIClient
from .pydantic_models import PromptRequest, PromptResponse
from pydantic import ValidationError
settings = Settings()  # type: ignore - Pydantic loads from .env at runtime, Pylance can't see this.
import logging 
from contextlib import asynccontextmanager



def setup_logging():
    """config logging for the backend app"""
    root_logger = logging.getLogger()

    root_logger.setLevel(logging.INFO)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - [%levelname)s] - %(message)s')
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

    yield
    logger.info("Application shutdown sequence initiated")

app = FastAPI(lifespan=lifespan)

@app.post("/api/v1/generate-prompt")
async def generate_prompt(request: PromptRequest, http_request:Request)->PromptResponse:
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

