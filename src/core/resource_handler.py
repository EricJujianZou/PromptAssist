import sys
import os

def get_path_for_resource(relative_path):
    """
    Get the absolute path to a resource, whether in development or packaged by PyInstaller.
    """
    try:
        # PyInstaller creates a temporary folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Not running as a PyInstaller executable, so use the script's directory
        base_path = os.path.abspath(os.path.dirname(__file__))
    
    return os.path.join(base_path, relative_path)