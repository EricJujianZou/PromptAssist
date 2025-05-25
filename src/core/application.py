import keyboard
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon
from ..storage.snippet_storage import SnippetStorage
from ..ui.snippet_manager_ui import SnippetUI
from .keystroke_listener import KeystrokeListener
from .focus_tracker import FocusTracker 
from .snippet_handler import SnippetHandler 
import signal
import time 
import os
import logging # Import logging

logger = logging.getLogger(__name__) # Get a logger for this module

#QObject is the base class for all Qt objects
#inherit event loop and signal slot mechanism
class Application(QObject):
    
    def __init__(self):
        super().__init__()#initialize QObject from super class constructor
        logger.info("Initializing Application...")
        self.storage = SnippetStorage()
        # self.cached_control = None #implement cache control, which stores reference to the active UI control to reduce UIA overhead - COMMENTED OUT
        #App compatibility, works with most but for some can not detect the input content
        
        self.blacklisted_apps = ["powershell.exe", "cmd.exe", "putty.exe"] # Still relevant for focus tracking/buffer clearing
    
        """
        TODO - sort out the blacklist if it's even needed
        """
        self.keystroke_listener = KeystrokeListener(self.storage)
        self.focus_tracker = FocusTracker(self.keystroke_listener, self.blacklisted_apps)
        self.snippet_handler = SnippetHandler(self.storage)
        self._init_tray_icon()
        # self._init_uia_polling() # COMMENTED OUT
        self.focus_tracker.start()
        logger.info("Application components initialized.")

        #Connect signals
        self.keystroke_listener.command_typed.connect(self.snippet_handler.replace_snippet) # Connect the command_typed signal to the snippet handler

        #signal handlers for termination
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        logger.info("Signal handlers registered.")
    def _init_tray_icon(self):
        # Set up tray icon with quit option
        logger.debug("Initializing tray icon...")
        try: 
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(current_dir, '..','icons','logo.png')
            
            self.tray_icon = QSystemTrayIcon(QIcon(icon_path))
            if self.tray_icon.icon().isNull(): # Check if icon loaded successfully
                    logger.warning(f"Icon file not found or invalid at {icon_path}. File exists: {os.path.exists(icon_path)}")
                    raise FileNotFoundError(f"Icon file not found or invalid at{icon_path}")
            self.tray_icon.setToolTip("Snippet App") # Simpler tooltip for now
            logger.info(f"Tray icon loaded from {icon_path}")
        except Exception as e:
            logger.error(f"Error initializing tray icon: {e}. Using default.", exc_info=True)
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
        logger.debug("Tray icon setup complete and shown.")

    def _quit_app(self):
        logger.info("Quitting application...")
        if hasattr(self, 'keystroke_listener'):
            self.keystroke_listener.stop_listener()
        if hasattr(self, 'focus_tracker'):
            self.focus_tracker.stop()
        
        QApplication.quit()
        logger.info("QApplication quit.")

    def _open_snippet_manager(self):
        logger.debug("Attempting to open snippet manager UI...")
        #lazy loading to avoid circular imports
        from ..ui.snippet_manager_ui import SnippetUI
        #if ui is not already open, open it
        if not hasattr(self, 'ui_window') or not self.ui_window.isVisible(): # Check if UI exists and is visible, renamed self.ui to self.ui_window
            logger.info("Snippet manager UI not found or not visible, creating new instance.")
            self.ui_window = SnippetUI(storage=self.storage, parent_app=self)
            self.ui_window.show()
        else:
            logger.debug("Snippet manager UI already exists, showing and raising.")
            self.ui_window.show()
            self.ui_window.raise_()
            self.ui_window.activateWindow()
     #quitting app:
    def _handle_signal(self, signum, frame):
        """Handle termination signals"""
        logger.info(f"Received signal {signum}, terminating application...")
        self._quit_app()


    # def _register_commands(self):
    #     """Register all commands from storage with the keyboard library"""
    #     # No actual registration needed with the buffer approach, just load them
    #     if not self.storage.snippets:
    #         logger.info("No snippets found in storage for registration.")
    #         return
            
    #     for cmd, text in self.storage.snippets.items():
    #         # Basic validation
    #         if not cmd.startswith("::") or len(cmd) <= 2:
    #             logger.warning(f"Invalid command format, skipping registration: {cmd}")
    #             continue
    #         logger.debug(f"Loaded command for potential registration: {cmd}") # Changed from "Registering"

    def _refresh_commands(self):
        """
        Refreshes commands. Currently, this is a placeholder as KeystrokeListener
        reads directly from SnippetStorage. If caching or more complex command
        management is introduced in KeystrokeListener or SnippetHandler,
        this method would trigger updates in those components.
        """
        logger.info("Application: Commands refresh requested (currently a placeholder).")
        # Potentially, if SnippetStorage had signals, other components could listen.
        # self._register_commands() # Example: if _register_commands had an active role.
        pass


    """ 
    *Updated Keystroke Tracking for our Buffer and UIA System and to Standardize the :: Prefix for now
    TODO - Allow for custom prefixes to classify different types of snippets, or provide a list of prefixes to choose from to avoid
    TODO - Stuff like C++ code std::cout to mess up with the snippets.
     """

