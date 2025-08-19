import keyboard
import time
from PySide6.QtCore import QObject, Signal
import logging 
from ..storage.snippet_storage import SnippetStorage
import pyperclip

logger = logging.getLogger(__name__) # Initialize logger

class KeystrokeListener(QObject):
    command_typed = Signal(str)  # Signal to emit when a command is typed
    llm_command_detected = Signal(str, str)

    def __init__(self, snippet_storage: SnippetStorage):
        super().__init__()
        self.snippet_storage = snippet_storage
        self.buffer = ""
        self.ctrl_pressed = False
        self.last_input_time = time.time()
        

        self._init_keyboard_listener()

    def _init_keyboard_listener(self):
            """Monitoring keystrokes in live time for commands"""
            self.buffer = ""
            try:
                keyboard.hook(self._track_keystrokes)
                logger.info("Keyboard listener initialized.") 
                keyboard.add_hotkey('ctrl+v', self._on_paste)
                logger.info("Hotkey for pasting a prompt added")
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
        llm_prefix = "::Prompt("

        #Handle ctrl combo presses:
        if self.ctrl_pressed and event.name in ('a', 'c', 'x', 'z'):
            logger.debug("Ctrl+Key detected, clearing buffer.") 
            self.buffer=""
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

            #Check if the buffer contains a stored Command
           

            snippet_prefix = "::"
            if snippet_prefix in self.buffer:
                possible_snippet = self.buffer[self.buffer.index("::"):]
                if possible_snippet in self.snippet_storage.snippets:
                    logger.info(f"Command '{possible_snippet}' found! Emitting signal.")
                    self.command_typed.emit(possible_snippet)
                    return

            
                
            if llm_prefix in self.buffer and self.buffer.endswith(")"):
                original_command_start = self.buffer.find(llm_prefix)
                
                user_query_start = original_command_start + len(llm_prefix)
                original_command = self.buffer[original_command_start : ]
                user_query = self.buffer[user_query_start : -1]
                if not user_query:
                    logger.debug(f"Empty prompt in format '{self.buffer}', no query is extracted and no API called.")
                    self.buffer += " "
                    return
                
                else:
                    self.llm_command_detected.emit(original_command, user_query)
                    return


            
            self.buffer += " " # Add space if no command was triggered
            logger.debug(f"Buffer after space added: '{self.buffer}'") 


            
                        
        elif len(char) == 1 and not self.ctrl_pressed:
            #add character to buffer
            self.buffer+=char
            logger.debug(f"Buffer after adding char '{char}': '{self.buffer}'") 

            if len(self.buffer) > 200: 
                if llm_prefix not in self.buffer:
                    #if we have a long buffer string without a prefix indicating someone's sending a crazy prompt, then trim it for performance and 
                    #for privacy
                    self.buffer = self.buffer[-50:]
                    logger.debug(f"Buffer trimmed: '{self.buffer}'") 
        else:
            # Log other keys if needed (like shift, alt, etc.)
            # logger.debug(f"Non-character key ignored: {char}") 
            pass # Ignore other keys like shift, alt, etc. for now

    def _on_paste(self):
        logger.debug("attempting to paste last clipboard object")
        try:

            pasted_object = pyperclip.paste()
            #check if the pasted object is of string type
            if (isinstance(pasted_object, str)):
                self.buffer += pasted_object
                logger.info(f"Adding text: \"{pasted_object}\" to buffer")
            else:
                logger.info("Pasted text is not a string, ignoring")
        except Exception as e:
            logger.error(f"Error with clipboard pasting. Error: {e}", exc_info=True)
        

    def clear_buffer(self):
        logger.debug ("KeystrokeListener: Buffer cleared") 
        self.buffer = ""
        
    def stop_listener(self):
        keyboard.unhook_all()