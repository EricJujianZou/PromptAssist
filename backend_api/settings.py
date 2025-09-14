from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path 
class Settings(BaseSettings):
    VERTEX_AI_PROJECT: str
    VERTEX_AI_LOCATION: str
    LLM_MODEL_NAME: str
    SYSTEM_INSTRUCTION: str
    MAX_OUTPUT_TOKENS: int
    TEMPERATURE: float
    API_RETRY_COUNT: int
    BACKEND_API_KEY:str
    REDIS_URL:str
    #model config for reliable loading:

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent/".env",
        env_file_encoding="utf-8"
    )