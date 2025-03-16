import keyboard
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtGui import QIcon
from storage import SnippetStorage
import sys
import signal

#QObject is the base class for all Qt objects
#inherit event loop and signal slot mechanism
class SnippetApp(QObject):
    command_typed = Signal(str) #signal to be emitted when command is typed
    #emit passed to any connected slots
    #Emit call returns immediately without waiting fo slots to finish processing

    def __init__(self):
        super().__init__()#initialize QObject from super class constructor
        self.storage = SnippetStorage()
        self._init_tray_icon()
        self._register_commands()
        self._init_keyboard_listener()
        self.command_typed.connect(self._replace_snippet)

        #signal handlers for termination
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _init_keyboard_listener(self):
        """Monitoring keystrokes in live time for commands"""
        self.buffer = ""
        keyboard.on_release(self._track_keystrokes)

    def _track_keystrokes(self, event):
        """Using buffer of typed characters and check for commands"""
        if event.event_type == "up":
            return
        char = event.name
        if char == "backspace":
            self.buffer=self.buffer[:-1]
        elif char == "space":
            #Check if buffer contains a registered command
            #When people finish typing they naturally press space 
            for cmd in self.storage.snippets:
                if self.buffer == cmd:
                    self.command_typed.emit(cmd)
                    self.buffer = "" #reset
                    break
        elif len(char) ==1:
            #ignoring modifiers
            self.buffer +=char
        
        #check if buffer is a command
        for cmd in self.storage.snippets:
            if self.buffer.endswith(cmd):
                self.command_typed.emit(cmd)
                self.buffer = ""
                break

    def _init_tray_icon(self):
        # Set up tray icon with quit option
        try: 
            self.tray_icon = QSystemTrayIcon(QIcon.fromTheme("application-exit"))
            self.tray_icon.setToolTip("Snippet App")
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
    #method to delete the command and instead insert the snippet. 
    def _replace_snippet(self, cmd):
        try:
            #delete the command
            print(f"deleting{len(cmd)} characters")
            for _ in range (len(cmd)):
                
                keyboard.press_and_release('backspace')
            #insert snippet text
            print (f"Inserting snippet: {self.storage.snippets[cmd]}")
            keyboard.write(self.storage.snippets[cmd])
        except KeyError:
            print (f"Error: snippet {cmd} not found")
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
if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) #app runs without window
    snippet_app = SnippetApp()
    sys.exit(app.exec())