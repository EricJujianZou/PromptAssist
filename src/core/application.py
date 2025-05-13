import keyboard
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon
from ..storage.snippet_storage import SnippetStorage
from ..ui.snippet_manager_ui import SnippetUI
from .keystroke_listener import KeystrokeListener
from .focus_tracker import FocusTracker 
from .snippet_handler import SnippetHandler 
import sys
import signal
import time 
#UIA Part for content tracking and buffer comparison - COMMENTED OUT FOR NOW
# from pywinauto import Desktop, Application

#QObject is the base class for all Qt objects
#inherit event loop and signal slot mechanism
class Application(QObject):
    

    def __init__(self):
        super().__init__()#initialize QObject from super class constructor
        self.storage = SnippetStorage()
        # self.cached_control = None #implement cache control, which stores reference to the active UI control to reduce UIA overhead - COMMENTED OUT
        #App compatibility, works with most but for some can not detect the input content
        
        self.blacklisted_apps = ["powershell.exe", "cmd.exe", "putty.exe"] # Still relevant for focus tracking/buffer clearing
    
        """
        TODO - sort out the blacklist if it's even needed
        """
        self.keystroke_listener = KeystrokeListener(self.storage)
        self.focus_tracker = FocusTracker(self.keystroke_listener)
        self.snippet_handler = SnippetHandler(self.storage)
        self._init_tray_icon()
        # self._init_uia_polling() # COMMENTED OUT
        self.focus_tracker.start()

        #Connect signals
        self.keystroke_listener.command_typed.connect(self.snippet_handler._replace_snippet) # Connect the command_typed signal to the snippet handler

        #signal handlers for termination
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
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
        print("Application: Quitting application...")
        if hasattr(self, 'keystroke_listener'):
            self.keystroke_listener.stop_listener()
        QApplication.quit()

    def _open_snippet_manager(self):
        #lazy loading to avoid circular imports
        from ..ui.snippet_manager_ui import SnippetUI # Corrected import
        #if ui is not already open, open it
        if not hasattr(self, 'ui') or not self.ui.isVisible(): # Check if UI exists and is visible
            self.ui = SnippetUI(storage=self.storage, parent_app=self)
            self.ui.show()
        else:
            self.ui.show()
            self.ui.raise_()
            self.ui.activateWindow()
     #quitting app:
    def _handle_signal(self, signum, frame):
        """Handle termination signals"""
        print(f"Received signal {signum}, terminating application...")
        self._quit_app()


    # def _register_commands(self):
    #     """Register all commands from storage with the keyboard library"""
    #     # No actual registration needed with the buffer approach, just load them
    #     if not self.storage.snippets:
    #         print("No snippets found!")
    #         return
            
    #     for cmd, text in self.storage.snippets.items():
    #         # Basic validation
    #         if not cmd.startswith("::") or len(cmd) <= 2:
    #             print(f"Invalid command format, skipping: {cmd}")
    #             continue
    #         print(f"Loaded command: {cmd}") # Changed from "Registering"

   

    """ 
    *Updated Keystroke Tracking for our Buffer and UIA System and to Standardize the :: Prefix for now
    TODO - Allow for custom prefixes to classify different types of snippets, or provide a list of prefixes to choose from to avoid
    TODO - Stuff like C++ code std::cout to mess up with the snippets.
     """

    