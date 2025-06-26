import logging
from PySide6.QtCore import QObject, Slot
import time
import os 
from dotenv import load_dotenv
import winsound

from ..keyboard_utils import simulate_keystrokes, clipboard_copy

#Vertex Ai Imports

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig as VertexGenerationConfig

logger = logging.getLogger(__name__)
load_dotenv()


class LLMConfig:
    #loading llm info from .env
    VERTEX_AI_PROJECT = os.getenv('VERTEX_AI_PROJECT')
    VERTEX_AI_LOCATION = os.getenv('VERTEX_AI_LOCATION')  
    LLM_MODEL_NAME = os.getenv('LLM_MODEL_NAME')
    SYSTEM_INSTRUCTION = "You are an expert prompt engineer. Your task is to transform the following users natural language request into a highly effective, detailed, and well-structured prompt suitable for a large language model. Prioritize result optimizationwith conciseness as the second priority.Ensure the generated prompt elicits a comprehensive and accurate response.Output ONLY the refined prompt. Do not include any of your own conversational text, thinking,explanations, apologies, or any text other than the prompt itself.The generated prompt should be complete and ready for immediate input into a large language model."
    print(f"LLMConfig - Loaded SYSTEM_INSTRUCTION (first 100 chars): '{SYSTEM_INSTRUCTION[:500]}...'") # Log it

    #Must cast these numeric values as int and float, because the .env treats all values as strings
    max_tokens_str = os.getenv('MAX_OUTPUT_TOKENS')
    MAX_OUTPUT_TOKENS = int(max_tokens_str) if max_tokens_str else 1000
    temp_str = os.getenv('TEMPERATURE')
    TEMPERATURE = float(temp_str) if temp_str else 0.1
    retry_str = os.getenv('API_RETRY_COUNT')
    API_RETRY_COUNT = int(retry_str) if retry_str else 2
    print(f"--- Debug: LLM_MODEL_NAME from env: {LLM_MODEL_NAME}")

class LLMPromptHandler(QObject):
    def __init__(self, parent=None):
        super().__init__(parent) #question: why we use super() init if parent is None?
        self.vertex_client=None
        self.config = LLMConfig()
        if not self.config.VERTEX_AI_PROJECT:
            logger.error("Vertex AI project env variable not set. All LLM features will fail")
        if not self.config.SYSTEM_INSTRUCTION:
            logger.warning("SYSTEM_INSTRUCTION is empty or not loaded from .env. Model may not behave as expected.")
        self._initialize_vertex_client()
        
        

    def _initialize_vertex_client(self):
        try:
            vertexai.init(
                project=self.config.VERTEX_AI_PROJECT,
                location=self.config.VERTEX_AI_LOCATION
            )
            self.vertex_client=GenerativeModel(
                
                self.config.LLM_MODEL_NAME,
                system_instruction=[self.config.SYSTEM_INSTRUCTION],
            )
            logger.info(f"Vertex AI Client intialized for Model: {self.config.LLM_MODEL_NAME}")
        except Exception as e:
            logger.error(f"failed to initialize Vertex AI client: {e}", exc_info=True)
            self.vertex_client=None
    
    def _construct_meta_prompt(self, user_query: str) -> list:
        """First test -> assume that the system instruction is handled by the model initialization, and the grounding prompt will be sent first every time"""
        # If we need to explicitly combine them:
        # return f"{SYSTEM_INSTRUCTION}\n\nUser Request: \"{user_query}\""

        return [user_query]

    def _call_llm_api(self, user_query_content: list) -> str | None:
        """Calls LLM API with content and handles the retries. None if error occurs"""
        if not self.vertex_client:
            logger.error(f"Error with calling LLM API as vertex AI client is not initialized", exc_info=True)
            return None

        for attempt in range (self.config.API_RETRY_COUNT):
            try:
                logger.info(f"Calling LLM API (Attempt {attempt+1}/{self.config.API_RETRY_COUNT}) with query: {user_query_content}")
                generation_config = VertexGenerationConfig(
                    max_output_tokens=self.config.MAX_OUTPUT_TOKENS,
                    temperature=self.config.TEMPERATURE,
                    #add top K top P if needed
                )
                #pass system instruction if not already set during model init
                response = self.vertex_client.generate_content(
                    contents=user_query_content,
                    generation_config=generation_config,
                    #pass system instructions if not done at init, we have to test. if not passed as param, we will just include as generate_content by prepending.
                )
                logger.debug(f"Full LLM response object: {response}")

                if response.candidates and response.candidates[0].content.parts:
                    augmented_prompt = response.candidates[0].content.parts[0].text
                    logger.info (f"LLM API Successfully called. Augmented prompt: '{augmented_prompt[:100]}...")
                    return augmented_prompt
                else:
                    logger.warning("LLM API did not return expected content")
                    if response.prompt_feedback and response.prompt_feedback.block_reason:
                        logger.warning(f"Prompt was blocked. Reason: {response.prompt_feedback.block_reason}")
                    #error fall thru
            except Exception as e:
                logger.error(f"LLM API call failed (Attempt {attempt+1}/{self.config.API_RETRY_COUNT}): {e}", exc_info=True)
                if attempt < self.config.API_RETRY_COUNT-1:
                    time.sleep(0.5)
        #all loops finished with returning anything
        logger.error("Max retries reached for API error") 
        return None
    
    
    
    @Slot(str)
    def handle_llm_prompt_command(self, user_query: str):

        logger.info(f"LLMPrompt Handler received query: {user_query}")
        original_trigger_text_approx = f"::Prompt({user_query}) "

        if not self.vertex_client:
            logger.error("Vertex AI client not initialized, can not handle LLM prompt", exc_info=True)
            simulate_keystrokes("[LLM Service Not Initialized]", len(original_trigger_text_approx)+1)
            return
        generating_feedback_text="Generating prompt..."

        try:
            logger.debug("Showing feedback to user of 'Generating prompt...'")
            backspaces_for_feedback = len(original_trigger_text_approx)+1
            
            simulate_keystrokes(generating_feedback_text, backspaces_for_feedback)
        except Exception as e:
            logger.error(f"Error showing 'Generating...' feedback {e}", exc_info=True)

        
        """Now using the API to send the configs and input text to the LLM to get a response"""

        augmented_prompt_ = self._call_llm_api([user_query])
        backspaces_for_call = len(generating_feedback_text)+1

        if augmented_prompt_:
            logger.info("augmented prompt received. Replacing text")
            simulate_keystrokes(backspaces=backspaces_for_call)
            clipboard_copy(augmented_prompt_)
            try:
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
                logger.debug("played notif sound (winsound)")
            except Exception as e_sound:
                logger.warning(f"Could not play winsound notif, falling back to bell sound: {e_sound}")
                print("\a", flush=True)
                logger.debug("Played notif sound (system bell \a).")
        else:
            logger.warning("Failed to get augmented prompt, displaying error")
            error_msg = "[Prompt Generation Failed. Try Again]"
            simulate_keystrokes(error_msg, backspaces_for_call)




    

        