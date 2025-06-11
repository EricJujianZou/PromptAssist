import pyperclip
from PySide6.QtCore import Signal
from ..storage.snippet_storage import SnippetStorage
from ..keyboard_utils import simulate_keystrokes, clipboard_copy
import logging
import time
import keyboard

logger = logging.getLogger(__name__)

class SnippetHandler:
    snippet_pasted = Signal (str) #this is a signal we will send after 
    def __init__(self, snippet_storage: SnippetStorage):

        """Initialize the SnippetHandler with a SnippetStorage instance."""

        self.snippet_storage = snippet_storage

    def replace_snippet(self, cmd: str) -> None:
        try:
            logger.info (f"Replacing snippet command with clipboard")
            # Calculate backspaces needed (length of command + 1 for the space)
            backspaces_needed = len(cmd) + 1 
            
            simulate_keystrokes(backspaces=backspaces_needed)

            snippet_text = self.snippet_storage.snippets.get(cmd)

            if snippet_text is None:
                logger.warning(f"No matching command can be found in the storage")
                return

            logger.debug(f"Snippet text found for {cmd}: {snippet_text[:100]}")

            original_clipboard_content = None
            clipboard_modified = False

            try:
                original_clipboard_content = pyperclip.paste()
                logger.debug(f"Retrieved original clipboard content")
            except pyperclip.PyperclipException as e_get_paste:
                logger.warning(f"Error retrieving original clipboard content: {e_get_paste}")
            

            clipboard_copy(snippet_text)
            clipboard_modified = True
            time.sleep(0.1)

            keyboard.send('ctrl + v')
            logger.info(f"Pasted snippet for command {cmd}")
            time.sleep(0.2)
            #proceed with deletion from clipboard

        except KeyError as e:
            print (f"Error replacing snippet: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during snippet replacement: {e}")
        finally:
            if clipboard_modified and original_clipboard_content is not None: #"is not" checks for memory address or identity inequality vs value inequality
                try:
                    pyperclip.copy(original_clipboard_content)
                    logger.debug("restored user's original clipboard content")
                except pyperclip.PyperclipException as e_restore:
                    logger.warning(f"Error when restoring user's original clipboard content: {e_restore}")
                except Exception as e_unexpected_restore:
                    logger.error(f"Unexpected error during clipboard restoration: {e_unexpected_restore}")
            elif clipboard_modified:
                logger.debug(f"Clipboard was modified, but there was no original content to restore")