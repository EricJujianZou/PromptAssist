from fastapi import FastAPI, Response, HTTPException
from .settings import Settings
from .vertex_ai_client import VertexAIClient
from .pydantic_models import PromptRequest, PromptResponse
from pydantic import ValidationError
settings = Settings()  # type: ignore - Pydantic loads from .env at runtime, Pylance can't see this.
import logging 


logger = logging.getLogger(__name__)

app = FastAPI()

vertex_ai_client = VertexAIClient(settings)

@app.post("/api/v1/generate-prompt")
async def generate_prompt(request: PromptRequest)->PromptResponse:
    user_query = request.user_query
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


@app.get("/favicon.ico", include_in_schema=False)
async def favicon_no_content():
    return Response(status_code=204)

