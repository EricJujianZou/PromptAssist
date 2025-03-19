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
#UIA Part for content tracking and buffer comparison

from pywinauto import Desktop, Application

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
        self.cached_control = None #implement cache control, which stores reference to the active UI control to reduce UIA overhead
        self.last_input_time = time.time() #when did the user last type? 
        self.ctrl_pressed = False

        #App compatibility, works with most but for some can not detect the input content
        self.blacklisted_apps = ["powershell.exe", "cmd.exe", "putty.exe"]

        self._init_tray_icon()
        self._register_commands()
        self._init_keyboard_listener()
        self._init_uia_polling()
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
        keyboard.on_release(self._track_keystrokes)
        keyboard.on_press_key("ctrl", self._ctrl_key_handler, suppress=False) #Still let the normal ctrl + whatever combo to work

    def _ctrl_key_handler(self, event):
        """ Handle Ctrl Key press
         
        * Updated to track the last input time when the user presses the Ctrl key
        * This is to ensure that the buffer is cleared when the user starts typing after pressing Ctrl
        """
        self.ctrl_pressed = (event.event_type == "down")
        if self.ctrl_pressed:
            self.last_input_time = time.time()


    def _track_keystrokes(self, event):
        """Using buffer of typed characters and check for commands"""
        if event.event_type == "up":
            return

        #Check last input time:
        self.last_input_time = time.time()

        #Handle ctrl combo presses:
        if self.ctrl_pressed and event.name in ('a', 'c', 'v', 'x', 'z'):
            self.buffer=""
            #Do a UIA poll to check input if the user pasted something in
            QTimer.singleShot(100, self._verify_buffer_with_uia) #delay so ui updates before we check buffer
            return

        """ Handle Character Input """
        char = event.name
        if char == "backspace":
            self.buffer=self.buffer[:-1] if self.buffer else "" #concise way of writing if buffer has something then backspace the last thing else empty
        elif char == "space":
            #Check if buffer contains a registered command
            if "::" in self.buffer:
                parts = self.buffer.split("::")
                if len(parts) > 1:
                    cmd = "::" + parts[-1]
                    if cmd in self.storage.snippets:
                        self.command_typed.emit(cmd)
                        self.buffer = ""
                        return
            
            self.buffer += " "#normal space
        elif len(char) == 1 and not self.ctrl_pressed:
            #add character to buffer
            self.buffer+=char

            #limit buffer size if they keep on typing for performance and privacy
            if len(self.buffer) > 100:
                self.buffer = self.buffer[-50:]

            
    def _init_tray_icon(self):
        # Set up tray icon with quit option
        try: 
            self.tray_icon = QSystemTrayIcon(QIcon.fromTheme("application-exit"))
        
            self.tray_icon.setToolTip(f"Buffer: {self.buffer[:20]}")
        except Exception as e:
            print (f"Error initializing tray icon: {e}")
            self.tray_icon = QSystemTrayIcon(QIcon.fromTheme("document-new"))
           

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
        keyboard.unhook_all()
        self._register_commands()
    def _open_snippet_manager(self):
        #lazy loading to avoid circular imports
        from ui import SnippetUI
        #if ui is not already open, open it
        if not hasattr(self, 'ui'):
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
            lookup_cmd = cmd[2:] if cmd.startswith("::") else cmd
            #delete the command
            
            for _ in range (len(cmd)):
                keyboard.press_and_release('backspace')
                time.sleep(0.01)

            #insert snippet text
            snippet_text = self.storage.snippets.get(lookup_cmd) or self.storage.snippets.get(cmd)
            if not snippet_text:
                raise KeyError(f"Snippet {cmd} not found")

            keyboard.write(snippet_text)

            #Verify the replacement with UIA
            QTimer.singleShot(100, self._verify_buffer_with_uia) #update the ui for some time for the app and buffer to react

        except KeyError as e:
            print (f"Error: {e}")



    def _register_commands(self):
        """Register all commands from storage with the keyboard library"""
        if not self.storage.snippets:
            print("No snippets found!")
            return
            
        for cmd, text in self.storage.snippets.items():
            try:
                print(f"Registering command: {cmd}")
                if not cmd or len(cmd)<1:
                    print("Invalid command, skipping...")
                    continue
            except Exception as e:
                print(f"Error registering command {cmd}: {e}")
    #quitting app:
    def _handle_signal(self, signum, frame):
        """Handle termination signals"""
        print(f"Received signal {signum}, terminating application...")
        self._quit_app()


    """ 
    * UIA PART 
    """

    """ Initialize UIA polling for text content verification """
    def _init_uia_polling(self):
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self._verify_buffer_with_uia)

        #base polling rate of 500ms, should only use around 3-5% CPU if performing buffer check
        self.polling_interval = 500
        self.poll_timer.start(self.polling_interval)
    
    
    
    """ Poll the active text field and verify buffer """
    def _verify_buffer_with_uia(self):

        if not self._should_perform_uia_check():
            return    
        try:
            #get the text from the active control
            text = self._get_text_from_focused_control()
            print("UIA text: ", {text[:50]})

            #early exit if no text
            if not text:
                self.buffer =""
                return
            
            #Buffer comparison
            if self.buffer and not text.endswith(self.buffer):
                self.buffer =""

        except Exception as e:
            #UIA access failed
            print (f"UIA verification failed: {e}")

        #Adjust polling rate based on typing activity
        self._adjust_polling_rate()
    
    """ Adjust the polling rate if the user is typing or not """
    def _adjust_polling_rate(self):
        time_since_input = time.time() - self.last_input_time

        if time_since_input < 2.0: #They're typing. 2 second window accounts for slow typers
            if self.polling_interval != 100:
                self.polling_interval = 100
                self.poll_timer.setInterval(self.polling_interval)
        else: #They're not typing
            if self.polling_interval != 500:
                self.polling_interval = 500
                self.poll_timer.setInterval(self.polling_interval)

    """ Check if we should do UIA check """
    def _should_perform_uia_check(self):
        #Skip if the buffer is empty (they not typing) and no recent activity
        if not self.buffer and (time.time() - self.last_input_time) > 2.0:
            return False

        #Skip if the active window is blacklisted
        current_app = self._get_current_app_name() #not use active app cus blacklisted is blacklisted regardless of which window is active
        if current_app in self.blacklisted_apps:
            return False

        return True

    """ Get the text from the focused control """
    def _get_text_from_focused_control(self):
        try:
            if not self.cached_control or not self._is_control_valid():
                #getting focused element
                self.cached_control = Desktop(backend="uia").focused_control

            #return the text from the control. Using texts and window text to be flexible about how the UI expose their text
            if hasattr(self.cached_control, "texts"):
                text = " ".join(self.cached_control.texts())
                return text
            elif hasattr(self.cached_control, "window_text"):
                return self.cached_control.window_text()

        except Exception as e:
            print(f"Error getting text from control: {e}")
            self.cached_control = None
        
        return ""

    """ Check if the cached control is still valid, or if the user closed the window or modified UI """
    def _is_control_valid(self):
        try:
            #See if we can access properties
            if self.cached_control:
                #If control invalid, will raise exception
                self.cached_control.element_info.name #validating the name property, provided by pywinauto 
                return True #no exception means cach exists and is valid.
        except Exception:
            return False 
        
        return False

    """ Get the name of the current active application """
    def _get_current_app_name(self):
        try:
            hwnd = win32gui.GetForegroundWindow() #stores window handle
            _, pid = win32process.GetWindowThreadProcessId(hwnd) #whatever thread ID goes in _ we do not care. only care abt thread pid
            #Pid is a unique numerical id by OS to each running instance of program
            #E.g. think about processes in task manager, they need to run and be managed. PID allows OS to manage them effectively. 
            return win32process.GetModuleFileNameEx(win32process.OpenProcess( #getting permission for query process info
                0x1000, False, pid), 0).split('\\')[-1].lower()
                #getting the url and then splitting into delimiters, only caring abt last token cus that's the app name.
            
        except Exception as e:
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
                        #resetting buffer.
                        print("focus changed")
                        self.buffer = ""
                except Exception as e:
                    print(f"Focus tracker error: {e}")
                time.sleep(0.5) #half a second to match with our polling
        
        focus_thread = threading.Thread(target=focus_tracker, daemon=True) #background thread
        focus_thread.start()


    

    

if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) #app runs without window
    snippet_app = SnippetApp()
    sys.exit(app.exec())