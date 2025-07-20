import logging
from PySide6.QtCore import QObject, Slot, Signal
import os 
from dotenv import load_dotenv

from ..keyboard_utils import simulate_keystrokes, clipboard_copy


import httpx

logger = logging.getLogger(__name__)
load_dotenv()

class LLMHandler(QObject):
    # Signal to emit the successful prompt and the original query
    prompt_received = Signal(str, str) 
    # Signal to emit the error message on failure
    prompt_failed = Signal(str)


    @Slot(str, str)
    def get_prompt_from_backend (self, user_query: str, original_command: str):
        """Make a post request to the backend with user_query, return an augmented prompt"""
        try:
            base_url = os.getenv("BACKEND_API_URL")
            if not base_url:
                error_msg = "BACKEND_API_URL environment variable is not set."
                logger.error(error_msg)
                self.prompt_failed.emit(error_msg)
                return
            
            payload = {"user_query": user_query}
            response = httpx.post(f"{base_url}/api/v1/generate-prompt", json=payload, timeout=30.0)
            response.raise_for_status() 

            data = response.json()
            augmented_prompt = data.get("augmented_prompt")

            if augmented_prompt:
                logger.info("Augmented prompt successfully received, emitting signal.")
                # Pass the original command along with the result
                self.prompt_received.emit(augmented_prompt, original_command)
            else:
                error_msg = "Backend returned an empty prompt."
                logger.warning(error_msg)
                self.prompt_failed.emit(error_msg)

        except httpx.HTTPStatusError as e:
            error_body = e.response.text
            error_msg = f"HTTP {e.response.status_code}: {error_body}"
            logger.error(f"HTTP error occurred: {error_msg}", exc_info=True)
            self.prompt_failed.emit(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Network error: {e}"
            logger.error(f"A network error occurred: {error_msg}", exc_info=True)
            self.prompt_failed.emit(error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            logger.error(error_msg, exc_info=True)
            self.prompt_failed.emit(error_msg)









