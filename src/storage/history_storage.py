import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class HistoryStorage:
    """Handles loading, saving, and managing prompt generation history."""
    def __init__(self, file_name="history.json", max_entries=100):
        try:
            app_data_dir = os.getenv('APPDATA')
            if not app_data_dir:
                app_data_dir = os.path.expanduser('~')
            
            self.storage_dir = os.path.join(app_data_dir, 'Expandr')
            if not os.path.exists(self.storage_dir):
                os.makedirs(self.storage_dir)
        except Exception as e:
            logger.error(f"Could not create or access history directory: {e}. Falling back to local directory.")
            self.storage_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            if not os.path.exists(self.storage_dir):
                os.makedirs(self.storage_dir)

        self.file_path = os.path.join(self.storage_dir, file_name)
        self.max_entries = max_entries
        self.history = []
        self._load()

    def _load(self):
        """Loads history from the JSON file."""
        if not os.path.exists(self.file_path):
            logger.info("History file not found. A new one will be created.")
            return

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
                logger.info(f"History loaded from {self.file_path}")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading history from {self.file_path}: {e}. Starting with empty history.")
            self.history = []

    def _save(self):
        """Saves the current history to the JSON file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=4)
            logger.debug(f"History saved to {self.file_path}")
        except IOError as e:
            logger.error(f"Failed to save history to {self.file_path}: {e}")

    def add_entry(self, query: str, result: str):
        """Adds a new entry to the history and saves."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "query": query,
            "result": result
        }
        
        # Insert new entry at the beginning of the list
        self.history.insert(0, entry)
        
        # Trim the history if it exceeds the maximum number of entries
        if len(self.history) > self.max_entries:
            self.history = self.history[:self.max_entries]
            
        self._save()
        logger.info(f"Added new entry to history: Query - '{query[:30]}...'")

    def get_all(self):
        """Returns all history entries."""
        return self.history

    def clear(self):
        """Clears all history entries and saves."""
        self.history = []
        self._save()
        logger.info("History has been cleared.")
