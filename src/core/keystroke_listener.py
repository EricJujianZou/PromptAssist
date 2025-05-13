import keyboard
import time
from PySide6.QtCore import QObject, Signal
from ..storage.snippet_storage import SnippetStorage

class KeystrokeListener(QObject):
    command_typed = Signal(str)  # Signal to emit when a command is typed

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
                print("Keyboard listener initialized. Went in track keystrokes for press and release")
            except Exception as e:
                print(f"Error initializing keyboard listener: {e}")
            
            
        # def _test_ctrl_events(self, event):
        #     print(f"--- TEST CTRL EVENT: name={event.name}, event_type={event.event_type} ---")
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
        print(f"--- _track_keystrokes CALLED: event_type={event.event_type}, name={event.name} ---") # New top-level log

        if event.name == "ctrl" or event.name == "left_ctrl" or event.name == "right_ctrl":
            if event.event_type == "down":
                self.ctrl_pressed = True
            elif event.event_type == "up":
                self.ctrl_pressed = False
            return
            
        if event.event_type == keyboard.KEY_UP: #to prevent counting the key press and key release as two separate events
            return

        print(f"Keystroke detected: {event.name}") # Uncomment this if you want to see every key press

        #Check last input time:
        self.last_input_time = time.time()

        #Handle ctrl combo presses:
        if self.ctrl_pressed and event.name in ('a', 'c', 'v', 'x', 'z'):
            print("Ctrl+Key detected, clearing buffer.") # Log buffer clear
            self.buffer=""
            #Do a UIA poll to check input if the user pasted something in - COMMENTED OUT
            # QTimer.singleShot(100, self._verify_buffer_with_uia) #delay so uia updates before we check buffer
            return

        """ Handle Character Input """
        char = event.name
        if char == "backspace":
            if self.buffer: # Only modify if buffer is not empty
                self.buffer=self.buffer[:-1]
                print(f"Buffer after backspace: '{self.buffer}'") # Log after backspace
            else:
                print("Buffer empty, backspace ignored.")
        elif char == "space":
            print(f"Space detected. Buffer before check: '{self.buffer}'") # Log before space check
            #Check if buffer contains a registered command
            if "::" in self.buffer:
                parts = self.buffer.split("::")
                if len(parts) > 1:
                    cmd = "::" + parts[-1]
                    print(f"Checking for command: '{cmd}'") # Log command check
                    if cmd in self.snippet_storage.snippets:
                        print(f"Command '{cmd}' found! Emitting signal.") # Log command found
                        self.command_typed.emit(cmd)
                        self.buffer = ""
                        print("Buffer cleared after command.") # Log buffer clear
                        return
                    else:
                        print(f"Command '{cmd}' not found in storage.") # Log command not found
            
            self.buffer += " " # Add space if no command was triggered
            print(f"Buffer after space added: '{self.buffer}'") # Log after space added
        elif len(char) == 1 and not self.ctrl_pressed:
            #add character to buffer
            self.buffer+=char
            print(f"Buffer after adding char '{char}': '{self.buffer}'") # Log after adding character

            #limit buffer size if they keep on typing for performance and privacy
            if len(self.buffer) > 100:
                self.buffer = self.buffer[-50:]
                print(f"Buffer trimmed: '{self.buffer}'") # Log buffer trimming
        else:
            # Log other keys if needed (like shift, alt, etc.)
            # print(f"Non-character key ignored: {char}")
            pass # Ignore other keys like shift, alt, etc. for now
    def clear_buffer(self):
        print ("keystrokeListener: Buffer cleared")
        self.buffer = ""
        
    def stop_listener(self):
        keyboard.unhook_all()