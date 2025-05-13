import threading
import time
import win32gui
import win32process
from PySide6.QtCore import QObject

from .keystroke_listener import KeystrokeListener # For type hinting

class FocusTracker:
    def __init__(self, keystroke_listener, blacklisted_apps=None):
        """
        Initializes the FocusTracker.

        :param keystroke_listener: An instance of KeystrokeListener to interact with.
        :param blacklisted_apps: A list of application executable names to ignore for buffer clearing.
        """
        self.keystroke_listener: KeystrokeListener = keystroke_listener # With type hint
        self.keystroke_listener = keystroke_listener
        self.blacklisted_apps = blacklisted_apps if blacklisted_apps is not None else []
        self.last_active_window = None
        self._running = False
        self.thread = None


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
    def _focus_tracker_loop(self):

        """Main tracking loop for focus changes"""
        print("Focus tracker started")

        while self._running:
            try:
                current_app_name = self._get_current_app_name()
                current_window_handle = win32gui.GetForegroundWindow()

                if current_window_handle != self.last_active_window:
                    print(f"FocusTracker: Focus changed. New app: '{current_app_name if current_app_name else 'Unknown'}'")
                    self.last_active_window = current_window_handle

                    if current_app_name and current_app_name in self.blacklisted_apps:
                        print(f"FocusTracker: App '{current_app_name}' is blacklisted. Buffer not cleared.")
                        pass
                    else:
                        print("FocusTracker: Buffer cleared due to focus change.")
                        self.keystroke_listener.clear_buffer()
            except Exception as e:
                print("Error in focus tracker loop:", e)
            time.sleep(0.5)
        print("Focus tracker stopped")

    def start(self):
        """Starts the focus tracking thread."""
        if not self._running:
            self._running = True
            self.thread = threading.Thread(target=self._focus_tracker_loop, daemon=True) #daemon means background thread, will not block program exit
            self.thread.start()
            print("Focus tracker thread started")
        else:
            print("Focus tracker thread already running")
    
    def stop(self):
        """Stops the focus tracking thread."""
        if self._running:
            self._running = False
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=1.0)

            print("Focus tracker thread stopped")



