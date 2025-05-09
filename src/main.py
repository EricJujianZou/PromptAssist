import keyboard
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtGui import QIcon
from storage import SnippetStorage
import sys
import signal
import time 
import threading
import win32gui #apis for window changes
import win32process
#UIA Part for content tracking and buffer comparison - COMMENTED OUT FOR NOW
# from pywinauto import Desktop, Application

#QObject is the base class for all Qt objects
#inherit event loop and signal slot mechanism
class SnippetApp(QObject):
    command_typed = Signal(str) #signal to be emitted when command is typed

    #emit passed to any connected slots
    #Emit call returns immediately without waiting fo slots to finish processing

    def __init__(self):
        super().__init__()#initialize QObject from super class constructor
        self.storage = SnippetStorage()
        self.buffer="" #initialize buffer
        self.last_active_window = None
        # self.cached_control = None #implement cache control, which stores reference to the active UI control to reduce UIA overhead - COMMENTED OUT
        self.last_input_time = time.time() #when did the user last type? 
        self.ctrl_pressed = False

        #App compatibility, works with most but for some can not detect the input content
        self.blacklisted_apps = ["powershell.exe", "cmd.exe", "putty.exe"] # Still relevant for focus tracking/buffer clearing

        self._init_tray_icon()
        self._register_commands()
        self._init_keyboard_listener()
        # self._init_uia_polling() # COMMENTED OUT
        self._start_focus_tracker()

        self.command_typed.connect(self._replace_snippet)

        #signal handlers for termination
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)


    """ 
    *Updated Keystroke Tracking for our Buffer and UIA System and to Standardize the :: Prefix for now
    TODO - Allow for custom prefixes to classify different types of snippets, or provide a list of prefixes to choose from to avoid
    TODO - Stuff like C++ code std::cout to mess up with the snippets.
     """

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
                    if cmd in self.storage.snippets:
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

            
    def _init_tray_icon(self):
        # Set up tray icon with quit option
        try: 
            # Try to load a specific icon, fall back if needed
            icon_path = "path/to/your/icon.ico" # Replace with actual path if you have one
            self.tray_icon = QSystemTrayIcon(QIcon(icon_path))
            if self.tray_icon.icon().isNull(): # Check if icon loaded successfully
                 raise FileNotFoundError("Icon file not found or invalid")
            self.tray_icon.setToolTip("Snippet App") # Simpler tooltip for now
        except Exception as e:
            print (f"Error initializing tray icon: {e}. Using default.")
            # Fallback to a standard system icon
            self.tray_icon = QSystemTrayIcon(QIcon.fromTheme("document-new")) 
            self.tray_icon.setToolTip("Snippet App (Default Icon)")
           

        # Create a menu for the tray icon
        tray_menu = QMenu()

        #Open Snippet Manager option
        open_action = tray_menu.addAction("Open Snippet Manager")
        open_action.triggered.connect(self._open_snippet_manager)

        #Separator
        tray_menu.addSeparator()
        
        #Quit action
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self._quit_app)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def _quit_app(self):
        keyboard.unhook_all() #stop listener
        QApplication.quit()
    
    
    def _refresh_commands(self):
        # This might not be needed if registration is simple, but keep for now
        # keyboard.unhook_all() # Careful with unhooking all if other parts use keyboard
        self._register_commands()

    def _open_snippet_manager(self):
        #lazy loading to avoid circular imports
        from ui import SnippetUI
        #if ui is not already open, open it
        if not hasattr(self, 'ui') or not self.ui.isVisible(): # Check if UI exists and is visible
            self.ui = SnippetUI(storage=self.storage, parent_app=self)
            self.ui.show()
        else:
            self.ui.show()
            self.ui.raise_()
            self.ui.activateWindow()
    
    """ 
    *Replacing Snippet
     """
    def _replace_snippet(self, cmd):
        try:
            #Remove prefix if its using new :: format
            # lookup_cmd = cmd[2:] if cmd.startswith("::") else cmd # Assuming cmd already includes ::
            
            # Calculate backspaces needed (length of command + 1 for the space)
            backspaces_needed = len(cmd) + 1 
            
            # Simulate backspaces
            for _ in range (backspaces_needed):
                keyboard.press_and_release('backspace')
                time.sleep(0.01) # Small delay between keys

            #insert snippet text
            snippet_text = self.storage.snippets.get(cmd) # Use the full command including ::
            if not snippet_text:
                raise KeyError(f"Snippet {cmd} not found in storage")

            keyboard.write(snippet_text)

            #Verify the replacement with UIA - COMMENTED OUT
            # QTimer.singleShot(100, self._verify_buffer_with_uia) #update the ui for some time for the app and buffer to react

        except KeyError as e:
            print (f"Error replacing snippet: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during snippet replacement: {e}")


    def _register_commands(self):
        """Register all commands from storage with the keyboard library"""
        # No actual registration needed with the buffer approach, just load them
        if not self.storage.snippets:
            print("No snippets found!")
            return
            
        for cmd, text in self.storage.snippets.items():
            # Basic validation
            if not cmd.startswith("::") or len(cmd) <= 2:
                print(f"Invalid command format, skipping: {cmd}")
                continue
            print(f"Loaded command: {cmd}") # Changed from "Registering"

    #quitting app:
    def _handle_signal(self, signum, frame):
        """Handle termination signals"""
        print(f"Received signal {signum}, terminating application...")
        self._quit_app()


    # """ 
    # * UIA PART - COMMENTED OUT
    # """

    # """ Initialize UIA polling for text content verification """
    # def _init_uia_polling(self):
    #     self.poll_timer = QTimer()
    #     self.poll_timer.timeout.connect(self._verify_buffer_with_uia)

    #     #base polling rate of 500ms, should only use around 3-5% CPU if performing buffer check
    #     self.polling_interval = 500
    #     self.poll_timer.start(self.polling_interval)
    
    
    
    # """ Poll the active text field and verify buffer """
    # def _verify_buffer_with_uia(self):
    #     if not self._should_perform_uia_check():
    #         return    
    #     try:
    #         # Get the text from the active control
    #         text = self._get_text_from_focused_control()
    #         # print("Buffer: '{}'".format(self.buffer)) # Optional debug
    #         # print("UIA text: '{}'".format(text[:50] if text else "")) # Optional debug

    #         # Early exit if no text
    #         if not text:
    #             # self.buffer = "" # Maybe don't clear buffer if UIA fails?
    #             return
            
    #         # Buffer comparison
    #         if self.buffer and not text.endswith(self.buffer):
    #             print("Buffer doesn't match UIA text, resetting buffer")
    #             self.buffer = ""

    #     except Exception as e:
    #         # UIA access failed
    #         print(f"UIA verification failed: {e}")

    #     # Adjust polling rate based on typing activity
    #     self._adjust_polling_rate()
    
    # """ Adjust the polling rate if the user is typing or not """
    # def _adjust_polling_rate(self):
    #     time_since_input = time.time() - self.last_input_time

    #     if time_since_input < 2.0: #They're typing. 2 second window accounts for slow typers
    #         if self.polling_interval != 100:
    #             self.polling_interval = 100
    #             self.poll_timer.setInterval(self.polling_interval)
    #     else: #They're not typing
    #         if self.polling_interval != 500:
    #             self.polling_interval = 500
    #             self.poll_timer.setInterval(self.polling_interval)

    # """ Check if we should do UIA check """
    # def _should_perform_uia_check(self):
    #     #Skip if the buffer is empty (they not typing) and no recent activity
    #     # if not self.buffer and (time.time() - self.last_input_time) > 2.0:
    #     #     return False

    #     #Skip if the active window is blacklisted
    #     current_app = self._get_current_app_name() #not use active app cus blacklisted is blacklisted regardless of which window is active
    #     if current_app in self.blacklisted_apps:
    #         return False

    #     return True # Simplified for now if UIA is minimal

    # """ Get the text from the focused control """
    # def _get_text_from_focused_control(self):
    #     """Get text from the currently focused control with improved focus detection"""
    #     # THIS ENTIRE METHOD IS COMMENTED OUT AS UIA IS DISABLED
    #     return "" # Return empty string if UIA is disabled

    # """ Check if the cached control is still valid, or if the user closed the window or modified UI """
    # def _is_control_valid(self):
    #     # THIS ENTIRE METHOD IS COMMENTED OUT AS UIA IS DISABLED
    #     return False # Assume invalid if UIA is disabled
        

    """ Get the name of the current active application """
    # Still needed for focus tracking and potentially blacklisting
    def _get_current_app_name(self):
        try:
            hwnd = win32gui.GetForegroundWindow() #stores window handle
            _, pid = win32process.GetWindowThreadProcessId(hwnd) #whatever thread ID goes in _ we do not care. only care abt thread pid
            #Pid is a unique numerical id by OS to each running instance of program
            #E.g. think about processes in task manager, they need to run and be managed. PID allows OS to manage them effectively. 
            
            # Use PROCESS_QUERY_LIMITED_INFORMATION (0x1000) for better compatibility
            process_handle = win32process.OpenProcess(0x1000, False, pid)
            if not process_handle:
                return "" # Failed to open process
            
            try:
                # GetModuleFileNameEx requires a handle with PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
                # Fallback or adjust permissions if needed, but 0x1000 is often sufficient for just the name
                app_path = win32process.GetModuleFileNameEx(process_handle, 0)
                return app_path.split('\\')[-1].lower()
            finally:
                win32process.CloseHandle(process_handle) # Ensure handle is closed
            
        except Exception as e:
            # print(f"Error getting app name: {e}") # Optional debug
            return ""

    """ 
    *Implement Focus tracking
     """

    """ Starting a thread to monitor focus and changes """
    def _start_focus_tracker(self):
        def focus_tracker():
            while True:
                try:
                    current_window = win32gui.GetForegroundWindow()
                    if current_window != self.last_active_window:
                        self.last_active_window = current_window
                        #update last input time - Keep this, useful for other logic potentially
                        self.last_input_time = time.time() 
                        #resetting buffer.
                        print("focus changed") # Keep this log
                        self.buffer = ""
                except Exception as e:
                    print(f"Focus tracker error: {e}")
                time.sleep(0.5) #half a second check interval
        
        focus_thread = threading.Thread(target=focus_tracker, daemon=True) #background thread
        focus_thread.start()


    

    

if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) #app runs without window
    snippet_app = SnippetApp()
    sys.exit(app.exec())