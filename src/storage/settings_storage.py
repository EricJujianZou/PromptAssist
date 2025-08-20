import os
import json
import logging

logger = logging.getLogger(__name__)

class SettingsStorage:
    """Handles loading and saving application settings from a JSON file."""
    def __init__(self, file_name="settings.json"):
        try:
            # Prefer AppData for storing user-specific configuration
            app_data_dir = os.getenv('APPDATA')
            if not app_data_dir:
                # Fallback to user's home directory if APPDATA is not available
                app_data_dir = os.path.expanduser('~')
                logger.warning("APPDATA environment variable not found. Using home directory.")
            
            self.storage_dir = os.path.join(app_data_dir, 'PromptAssist')
            if not os.path.exists(self.storage_dir):
                os.makedirs(self.storage_dir)
                logger.info(f"Created settings directory: {self.storage_dir}")
        except Exception as e:
            # If creating a directory in AppData fails, fall back to a local directory
            logger.error(f"Could not create or access settings directory in AppData: {e}. Falling back to local directory.")
            self.storage_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            if not os.path.exists(self.storage_dir):
                os.makedirs(self.storage_dir)

        self.file_path = os.path.join(self.storage_dir, file_name)
        self.settings = self._get_defaults()
        self._load()

    def _get_defaults(self):
        """Returns a dictionary with the default application settings."""
        return {
            "theme": "Dark",
            "clear_clipboard_on_paste": False,
            "blacklisted_apps": [
                "powershell.exe",
                "cmd.exe",
                "putty.exe",
                "WindowsTerminal.exe"
            ]
        }

    def _load(self):
        """Loads settings from the JSON file, merging them with defaults."""
        if not os.path.exists(self.file_path):
            logger.info("Settings file not found. Creating with default settings.")
            self._save()
            return

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                disk_settings = json.load(f)
                # Update defaults with loaded settings to ensure new default keys are added
                self.settings.update(disk_settings)
                logger.info(f"Settings loaded from {self.file_path}")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading settings from {self.file_path}: {e}. Using default settings.")
            # Reset to defaults if the file is corrupt
            self.settings = self._get_defaults()

    def _save(self):
        """Saves the current settings to the JSON file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
            logger.debug(f"Settings saved to {self.file_path}")
        except IOError as e:
            logger.error(f"Failed to save settings to {self.file_path}: {e}")

    def get(self, key, default=None):
        """Gets a setting value by key, returning a default if not found."""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Sets a setting value by key and immediately saves to disk."""
        self.settings[key] = value
        self._save()
