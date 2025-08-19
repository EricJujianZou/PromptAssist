from .settings import Settings
from google import genai
from google.genai.types import GenerateContentConfig
import logging

logger = logging.getLogger(__name__)

class VertexAIClient:
    """
    Class to handle Vertex Client related interactions"""

    def __init__(self, settings: Settings):
        """Initializing the Vertex AI Client"""
        self.project=settings.VERTEX_AI_PROJECT
        self.location=settings.VERTEX_AI_LOCATION
        self.model_name = settings.LLM_MODEL_NAME
        self.system_instructions = settings.SYSTEM_INSTRUCTION
        self.max_tokens=settings.MAX_OUTPUT_TOKENS
        self.temperature= settings.TEMPERATURE
        self.retry_count=settings.API_RETRY_COUNT
        if not self.project or not self.location:
            raise ValueError("VERTEX_AI_PROJECT and LOCATION not set")


        self.client = genai.Client(
            vertexai=True, 
            project = self.project,
            location=self.location
        )
        logger.info(f"VertexAIClient initialized for model '{settings.LLM_MODEL_NAME}'.")

    def generate_prompt(self, user_query:str)->str:
        logger.info(f"system instruction injected: {self.system_instructions}")
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_query,
                config = GenerateContentConfig(
                    temperature = self.temperature,
                    max_output_tokens=self.max_tokens,
                    system_instruction=self.system_instructions
                )            
            )
            return response.text or ""
        except Exception as e:
            logger.error(f"Error ocrrued during API call: {e}")
            raise

