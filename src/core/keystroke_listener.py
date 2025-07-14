import keyboard
import time
from PySide6.QtCore import QObject, Signal
import logging # Add logging import
from ..storage.snippet_storage import SnippetStorage
from ..keyboard_utils import simulate_keystrokes, clipboard_copy

logger = logging.getLogger(__name__) # Initialize logger

class KeystrokeListener(QObject):
    command_typed = Signal(str)  # Signal to emit when a command is typed
    llm_command_detected = Signal(str)

    def __init__(self, snippet_storage: SnippetStorage):
        super().__init__()
        self.snippet_storage = snippet_storage
        self.buffer = ""
        self.ctrl_pressed = False
        self.last_input_time = time.time()
        self.generating_text = "Generating Prompt..."

        self._init_keyboard_listener()

    def _init_keyboard_listener(self):
            """Monitoring keystrokes in live time for commands"""
            self.buffer = ""
            try:
                keyboard.hook(self._track_keystrokes)
                logger.info("Keyboard listener initialized.") 
            except Exception as e:
                logger.error(f"Error initializing keyboard listener: {e}") 
            
            
        # def _test_ctrl_events(self, event):
        #     logger.debug(f"--- TEST CTRL EVENT: name={event.name}, event_type={event.event_type} ---") 
        #needed to test if the ctrl key events are being detected properly. Found out that on_release is not working, but hook works


        # def _ctrl_key_handler(self, event):
        #     """ Handle Ctrl Key press
            
        #     * Updated to track the last input time when the user presses the Ctrl key
        #     * This is to ensure that the buffer is cleared when the user starts typing after pressing Ctrl
        #     """
        #     self.ctrl_pressed = (event.event_type == "down")
        #     if self.ctrl_pressed:
        #         self.last_input_time = time.time()


    def _track_keystrokes(self, event):
        """Using buffer of typed characters and check for commands"""
        logger.debug(f"--- _track_keystrokes CALLED: event_type={event.event_type}, name={event.name} ---") 

        if event.name == "ctrl" or event.name == "left_ctrl" or event.name == "right_ctrl":
            if event.event_type == "down":
                self.ctrl_pressed = True
            elif event.event_type == "up":
                self.ctrl_pressed = False
            return
            
        if event.event_type == keyboard.KEY_UP: #to prevent counting the key press and key release as two separate events
            return

        logger.debug(f"Keystroke detected: {event.name}")

        #Check last input time:
        self.last_input_time = time.time()

        #Handle ctrl combo presses:
        if self.ctrl_pressed and event.name in ('a', 'c', 'v', 'x', 'z'):
            logger.debug("Ctrl+Key detected, clearing buffer.") 
            self.buffer=""
            #Do a UIA poll to check input if the user pasted something in - COMMENTED OUT
            # QTimer.singleShot(100, self._verify_buffer_with_uia) #delay so uia updates before we check buffer
            return

        """ Handle Character Input """
        char = event.name
        if char == "backspace":
            if self.buffer: # Only modify if buffer is not empty
                self.buffer=self.buffer[:-1]
                logger.debug(f"Buffer after backspace: '{self.buffer}'") 
            else:
                logger.debug("Buffer empty, backspace ignored.") 
        elif char == "space":
            logger.debug(f"Space detected. Buffer before check: '{self.buffer}'") 

            #Check if the buffer contains a LLM Prompt Command

            llm_prefix = "::Prompt("
            if self.buffer.startswith(llm_prefix) and self.buffer.endswith(")"):
                if len(self.buffer)> len(llm_prefix) +1:
                    user_query = self.buffer[len(llm_prefix):-1]
                    logger.info(f"LLM prompt command detected. User query: '{user_query}'")
                    #now to show the user a visual feedback that a prompt is being generated.
                    try:
                        logger.debug("Showing feedback to user of 'Generating prompt...'")
                        backspaces_for_feedback = len(user_query)+1
                        
                        #backspace the typed command
                        simulate_keystrokes(self.generating_text, backspaces_for_feedback)
                    except Exception as e:
                        logger.error(f"Error showing 'Generating...' feedback {e}", exc_info=True)

                    self.llm_command_detected.emit(user_query)
                    self.buffer=""
                    logger.debug("Buffer cleared after LLM command.")
                    return
                else:
                    logger.debug(f"Empty prompt in format '{self.buffer}', no query is extracted and no API called.")

            #Check if buffer contains a registered command
            if "::" in self.buffer:
                parts = self.buffer.split("::")
                if len(parts) > 1:
                    cmd = "::" + parts[-1]
                    logger.debug(f"Checking for command: '{cmd}'") 
                    if cmd in self.snippet_storage.snippets:
                        logger.info(f"Command '{cmd}' found! Emitting signal.")
                        self.command_typed.emit(cmd)
                        self.buffer = ""
                        logger.debug("Buffer cleared after command.") 
                        return
                    else:
                        logger.debug(f"Command '{cmd}' not found in storage.") 
            
            self.buffer += " " # Add space if no command was triggered
            logger.debug(f"Buffer after space added: '{self.buffer}'") 
        elif len(char) == 1 and not self.ctrl_pressed:
            #add character to buffer
            self.buffer+=char
            logger.debug(f"Buffer after adding char '{char}': '{self.buffer}'") 

            #limit buffer size if they keep on typing for performance and privacy
            if len(self.buffer) > 200: #increased buffer cap to 200 chars because expecting longer commands from users for the LLM feature
                self.buffer = self.buffer[-50:]
                logger.debug(f"Buffer trimmed: '{self.buffer}'") 
        else:
            # Log other keys if needed (like shift, alt, etc.)
            # logger.debug(f"Non-character key ignored: {char}") 
            pass # Ignore other keys like shift, alt, etc. for now
    def clear_buffer(self):
        logger.debug ("KeystrokeListener: Buffer cleared") 
        self.buffer = ""
        
    def stop_listener(self):
        keyboard.unhook_all()