import keyboard
import time

from ..storage.snippet_storage import SnippetStorage

class SnippetHandler:
    def __init__(self, snippet_storage: SnippetStorage):

        """Initialize the SnippetHandler with a SnippetStorage instance."""

        self.snippet_storage = snippet_storage

    def replace_snippet(self, cmd: str):
        try:
            
            # Calculate backspaces needed (length of command + 1 for the space)
            backspaces_needed = len(cmd) + 1 
            
            # Simulate backspaces
            for _ in range (backspaces_needed):
                keyboard.press_and_release('backspace')
                time.sleep(0.01) # Small delay between keys

            #insert snippet text
            snippet_text = self.snippet_storage.snippets.get(cmd) # Use the full command including ::

            if not snippet_text:
                raise KeyError(f"Snippet {cmd} not found in storage")

            keyboard.write(snippet_text)

            #Verify the replacement with UIA - COMMENTED OUT
            # QTimer.singleShot(100, self._verify_buffer_with_uia) #update the ui for some time for the app and buffer to react

        except KeyError as e:
            print (f"Error replacing snippet: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during snippet replacement: {e}")