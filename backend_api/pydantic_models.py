from pydantic import BaseModel, Field

class PromptRequest (BaseModel):
    """Request model for prompt generation endpoint"""
    user_query: str = Field(
        min_length=1,
        max_length=1000,
        description="User's natural language before transformation"
    )

class PromptResponse(BaseModel):
    """Response model for prompt generation endpoint"""
    augmented_prompt: str = Field(
        min_length=1,
        max_length = 10000,
        description="AI-generated augmented prompt"
    )
#note: 
#we set the min length to 1 to catch empty strings, and the max length to prevent prompt injection 
#into wasting my credits and getting super long answers
