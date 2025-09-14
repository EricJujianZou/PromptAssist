from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QStyle, QMenu
from PySide6.QtGui import QIcon
from ..storage.snippet_storage import SnippetStorage
from ..storage.settings_storage import SettingsStorage
from ..storage.history_storage import HistoryStorage
from ..ui.snippet_manager_ui import SnippetUI
from ..ui.frameless_window import FramelessWindow
from .keystroke_listener import KeystrokeListener
from .focus_tracker import FocusTracker 
from .snippet_handler import SnippetHandler 
from .llm_prompt_handler import LLMHandler
from ..keyboard_utils import clipboard_copy, simulate_keystrokes
from .resource_handler import get_path_for_resource
import signal
import logging # Import logging
import winsound
import sys
import os


logger = logging.getLogger(__name__) # Get a logger for this module

#QObject is the base class for all Qt objects
#inherit event loop and signal slot mechanism
class Application(QObject):
     
    def __init__(self):
        
        super().__init__()#initialize QObject from super class constructor
        logger.info("Initializing Application...")
        self.storage = SnippetStorage()
        self.settings = SettingsStorage()
        self.history = HistoryStorage()
        self.main_window = None # To hold the reference to the UI window
        # self.cached_control = None #implement cache control, which stores reference to the active UI control to reduce UIA overhead - COMMENTED OUT
        #App compatibility, works with most but for some can not detect the input content
        self.is_request_in_flight = False

        #resource handler for icon
        

        # Load settings into application properties, ensuring correct types
        self.blacklisted_apps = self.settings.get("blacklisted_apps", [])
        self.clear_clipboard = bool(self.settings.get("clear_clipboard_on_paste", False))

        self.generating_text = "Generating Prompt..."
        """
        TODO - sort out the blacklist if it's even needed
        """
        self.keystroke_listener = KeystrokeListener(self.storage)
        self.focus_tracker = FocusTracker(self.keystroke_listener, self.blacklisted_apps)
        self.snippet_handler = SnippetHandler(self.storage)
        self._init_tray_icon()
        self.llm_handler = LLMHandler()
        # self._init_uia_polling() # COMMENTED OUT
        self.focus_tracker.start()
        logger.info("Application components initialized.")

        #Connect signals
        self.keystroke_listener.command_typed.connect(self.snippet_handler.replace_snippet) # Connect the command_typed signal to the snippet handler

        #llm related signal connections
        self.keystroke_listener.llm_command_detected.connect(self.on_llm_command) #Connect the llm command detection to the visual feedback and backend calling
        self.llm_handler.prompt_received.connect(self.handle_llm_augmented_prompt) 
        self.llm_handler.prompt_failed.connect(self.handle_llm_failure)

        #snippet replacement and clear connections
        self.snippet_handler.snippet_pasted.connect(self.replace_and_clear_buffer)
        #signal handlers for termination
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        logger.info("Signal handlers registered.")

    @Slot()
    def replace_and_clear_buffer(self):
        self.keystroke_listener.clear_buffer()
    @Slot()
    def show_snippet_manager(self):
        """Create and show the snippet manager UI."""
        if self.main_window is None or not self.main_window.isVisible():
            logger.debug("Creating or showing main window.")
            
            # 1. Create the content widget first, passing all storage objects
            dashboard_content = SnippetUI(self.storage, self.settings, self.history)
            
            # 2. Wrap it in our custom frameless window
            self.main_window = FramelessWindow(dashboard_content)

            # 3. Load and apply the stylesheet to the main window
            try:
                # Correct path from src/core/ to src/
                style_path = get_path_for_resource('style.qss')
                with open(style_path, "r") as f:
                    stylesheet = f.read()
                self.main_window.setStyleSheet(stylesheet)
                logger.debug(f"Stylesheet loaded for main window from {style_path}")
            except Exception as e:
                logger.error(f"Error loading stylesheet for main window: {e}")

            self.main_window.show()
            self.main_window.activateWindow() # Bring to front
        else:
            logger.debug("Main window already visible. Activating window.")
            self.main_window.activateWindow() # Bring to front if already open
    
    @Slot(str, str)
    def on_llm_command(self, original_command: str, user_query: str):
        if self.is_request_in_flight:
            logger.warning("ignore request because llm command is already in flight")
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC)
            return # Stop processing immediately
        
        self.is_request_in_flight = True
        logger.info(f"Received llm command: {original_command}")
        #Type the generating text
        try:
            
            simulate_keystrokes(self.generating_text, len(original_command)+1)
        except Exception as e:
            logger.error(f"Error showing the 'generating...' visual feedback: {e}", exc_info = True)
        
        #call the backend, passing the original query for history
        self.llm_handler.get_prompt_from_backend(user_query, original_command)
        

        

    @Slot(str, str)
    def handle_llm_augmented_prompt(self, augmented_prompt: str, original_query: str):

        try:
            backspaces_for_call = len(self.generating_text)

            if augmented_prompt:
                # Add to history
                self.history.add_entry(query=original_query, result=augmented_prompt)

                logger.info("augmented prompt received. Replacing text")
                simulate_keystrokes(backspaces=backspaces_for_call)
                clipboard_copy(augmented_prompt, clear_after=self.clear_clipboard)
                try:
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
                    logger.debug("played notif sound (winsound)")
                except Exception as e_sound:
                    logger.warning(f"Could not play winsound notif, falling back to bell sound: {e_sound}")
                    print("\a", flush=True)
                    logger.debug("Played notif sound (system bell \a).")
            # This 'else' case is now handled by handle_llm_failure
        finally:
            self.is_request_in_flight = False
            logger.info("LLM request flight lock released.")
            self.keystroke_listener.clear_buffer()

    @Slot(str)
    def handle_llm_failure(self, error_message: str):
        """Handles the visual feedback when a prompt generation fails."""
        try:
            logger.warning(f"Failed to get augmented prompt, displaying error: {error_message}")
            error_display_text = f"[Prompt Failed: {error_message}]"
            backspaces_for_call = len(self.generating_text)
            simulate_keystrokes(error_display_text, backspaces_for_call)
        except Exception as e:
            logger.error(f"Error displaying failure message: {e}", exc_info=True)
        finally:
            self.is_request_in_flight = False
            logger.info("LLM request flight lock released after failure.")
            self.keystroke_listener.clear_buffer()

    @Slot(QSystemTrayIcon.ActivationReason)
    def on_tray_icon_activated(self, reason):
        """Handles activation events on the tray icon."""
        # Show dashboard on double-click, while right-click shows context menu
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            logger.debug("Tray icon double-clicked, showing manager.")
            self.show_snippet_manager()

    def _init_tray_icon(self):
        """Initializes the system tray icon and its context menu."""
        logger.debug("Initializing system tray icon.")
        self.tray_icon = QSystemTrayIcon(self)
        
        # Set icon
        try:

            try:
                # Check if running in a bundle and log the bundle directory
                bundle_dir = sys._MEIPASS
                logging.info(f"RUNNING IN BUNDLE. MEIPASS is: {bundle_dir}")
            except AttributeError:
                # Log the directory if running as a normal script
                bundle_dir = os.path.abspath(".")
                logging.info(f"RUNNING AS SCRIPT. Base path is: {bundle_dir}")

            icon_path = get_path_for_resource('logo.ico')
            logging.info(f"Attempting to load icon from generated path: {icon_path}")


            # Log whether the file actually exists at that path
            if os.path.exists(icon_path):
                logging.info("SUCCESS: Icon file was found at the specified path.")
                self.tray_icon.setIcon(QIcon(icon_path))
                
            else:
                logging.error("FAILURE: Icon file was NOT FOUND at the specified path.")
                std_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
                self.tray_icon.setIcon(std_icon)

            
        except Exception as e:
            logger.error(f"Failed to load tray icon: {e}", exc_info=True)

        # Create context menu
        self.menu = QMenu()

        # Add action to show snippet manager
        self.show_action = self.menu.addAction("PromptAssist Dashboard")
        self.show_action.triggered.connect(self.show_snippet_manager)

        self.menu.addSeparator()

        # Add quit action
        self.quit_action = self.menu.addAction("Quit")
        self.quit_action.triggered.connect(self.quit_application)

        self.tray_icon.setContextMenu(self.menu)

        # Connect the activated signal for double-click handling
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        self.tray_icon.show()
        logger.info("System tray icon is now visible.")

    def quit_application(self):
        """Quits the application."""
        logger.info("Quit action triggered. Shutting down.")
        QApplication.quit()

    def _handle_signal(self, signum, frame):
        logger.warning(f"Signal {signum} received. Shutting down.")
        self.quit_application()


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

