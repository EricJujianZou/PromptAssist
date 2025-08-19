import sys
from PySide6.QtWidgets import QApplication
from .core.application import Application 
import logging
import logging.handlers # For rotating file handler
import os

# Determine the application's root directory or a suitable logs directory
# In a production app, this might be in user's AppData or a system log directory.
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOG_FILE_PATH = os.path.join(LOG_DIR, 'app.log')

def setup_logging():
    """Configures logging for the application."""
    log_level = logging.DEBUG # Set to INFO for production, DEBUG for development
    log_format = '%(asctime)s - %(name)s - [%(levelname)s] - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Prevent multiple handlers if this function is called again (e.g., in tests or reloads)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Console Handler (StreamHandler)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    console_handler.setLevel(log_level) # Or a different level for console, e.g., logging.INFO
    root_logger.addHandler(console_handler)

    # File Handler (RotatingFileHandler for better log management)
    # Rotates logs when they reach 5MB, keeping up to 5 backup logs.
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE_PATH, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    file_handler.setLevel(log_level) # Typically log everything to file
    root_logger.addHandler(file_handler)

    # For PySide6/Qt specific logging (optional, can be noisy)
    # logging.getLogger("PySide6").setLevel(logging.WARNING)


if __name__ == "__main__":
    setup_logging() # Call the setup function

    logger = logging.getLogger(__name__)
    logger.info("Application starting...")
    logger.debug(f"Logging to console and to file: {LOG_FILE_PATH}")

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    try:
        snippet_app = Application() 
        exit_code = app.exec()
        logger.info(f"Application exited with code {exit_code}.")
        sys.exit(exit_code)
    except Exception as e:
        logger.critical(f"Unhandled exception at top level: {e}", exc_info=True)
        sys.exit(1)
















