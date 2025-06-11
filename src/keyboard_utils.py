import keyboard
import time
import logging
import pyperclip

logger = logging.getLogger(__name__)

def simulate_keystrokes(text_to_type: str="", backspaces:int=0, char_delay: float = 0.005, backspace_delay: float= 0.01)-> None:
        """
        Simulates keystrokes for backspacing and optionally typing single-line text.

        Newline characters in text_to_type will be replaced with spaces
        to prevent unintended "Enter" key simulations by keyboard.write().

        Args:
            text_to_type (str, optional): The text to type. Defaults to "".
                                          If only backspacing is needed, this can be omitted.
                                          
            backspaces (int, optional): The number of backspace keys to simulate. Defaults to 0.
            char_delay (float, optional): The delay between each character input
            backspace_delay (float, optional): The delay between each backspace input
        """
        try:
            if backspaces>0:
                for back in range (backspaces):
                    keyboard.send('backspace')
                    #time.sleep(0.01)
                    #Try without delay first, if it's not reliable then add it back
            if text_to_type:
                safe_text_to_type = text_to_type.replace("\n", " ")
                keyboard.write(safe_text_to_type)
            
            log_message_parts = []
            if backspaces > 0:
                log_message_parts.append(f"simulated {backspaces} backspaces")
            if text_to_type:
                log_message_parts.append(f"typed message: {safe_text_to_type}")
            if log_message_parts:
                logger.debug(". ".join(log_message_parts))
        except Exception as e:
            logger.error(f"Attempted to simulate typing, error occurred: {e}", exc_info=True)

def clipboard_copy(text_to_copy: str):
        """
        feature: copy the API returned text to the clipboard, and notify the user that they can paste at any time.
        This feature update gives more freedom for the user to decide when to use the prompt based on their workflow

    
        """
        try: 
            pyperclip.copy(text_to_copy)
            logger.debug(f"Copied to clipboard: {text_to_copy[:100]}")

            
        except pyperclip.PyperclipException as e_pyperclip:
            logger.error(f"Pyperclip error: Failed to copy text {e_pyperclip}", exc_info=True)
        except Exception as e:
            logger.error(f"Error happened during clipboard copy or sound notif: {e}", exc_info = True)