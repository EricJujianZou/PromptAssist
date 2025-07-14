import logging
from PySide6.QtCore import QObject, Slot, Signal
import os 
from dotenv import load_dotenv

from ..keyboard_utils import simulate_keystrokes, clipboard_copy


import httpx

logger = logging.getLogger(__name__)
load_dotenv()

class LLMHandler(QObject):
    prompt_received = Signal(str)
    @Slot(str)
    def get_prompt_from_backend (self, user_query : str) -> str|None:
        """Make a post request to the backend with user_query, return an augmented prompt"""
        try:
            base_url = os.getenv("BACKEND_API_URL")
            if not base_url:
                logger.error("Backend API environment variable error, not set")
                return None
            
            payload = {"user_query": user_query}

            #here we use a dictionary structure very standard, but then use httpx built in library json function to turn it into json
            #This is using the concept of serialization
            response = httpx.post(f"{base_url}/api/v1/generate-prompt", json=payload, timeout=30.0)
            #raises error for error codes like 4xx or 5xx
            response.raise_for_status() 

            #parsing JSON value from PromptResponse body
            data = response.json()

            augmented_prompt = data.get("augmented_prompt")
            if augmented_prompt:
                logger.info(f"Augmented prompt successfully received, now emitting signal to copy to clipboard")
                
                self.prompt_received.emit(augmented_prompt)
        except httpx.HTTPStatusError as e:
            #catch the HTTP error
            print(f"HTTP error occured: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            #catches network lev el errors
            print(f"A network error occured: {e}")
            return None
        
        
    




    

        