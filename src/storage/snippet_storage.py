import os
#this is to handle file paths and dir
import json
import logging
logger = logging.getLogger(__name__)

class SnippetStorage:
    #init is special method constructor. Initialize object attributes
    #"self" muist be included in param because unlike java compiler 
    # doesn't add it for you to use in all methods
    def __init__(self):
        try:
            app_data_dir = os.getenv('APPDATA')
            if not app_data_dir:
                # Fallback to user's home directory if APPDATA is not available
                app_data_dir = os.path.expanduser('~')
                logger.warning("APPDATA environment variable not found. Using home directory.")
            
            self.config_dir = os.path.join(app_data_dir, 'PromptAssist')
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
                logger.info(f"Created settings directory: {self.config_dir}")
        except Exception as e:
            # If creating a directory in AppData fails, fall back to a local directory
            logger.error(f"Could not create or access settings directory in AppData: {e}. Falling back to local directory.")
            self.config_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)

        self.config_path = os.path.join(self.config_dir, 'config.json')
        self.snippets = self._load()

    def _load(self):
        try:
            #with open is basically auto open + close otgether
            with open(self.config_path, 'r') as file:
                #the json.load function 
                # returns dictionary which is kind of like java hashmap key value pair
                return json.load(file)
        except FileNotFoundError:
            #return default snippet
            return {
                "::emailStarter": """Hello, \n I hope this email finds you well.
                I am writing this email because """
            }
    def save(self, command, text):
        self.snippets[command] = text
        with open(self.config_path, 'w') as file:
            json.dump(self.snippets, file, indent = 4)

    def delete (self, command):
        if command in self.snippets:
            del self.snippets[command]
            self._save_to_file()

    def _save_to_file(self):
        #save entire dictionary to file
        with open(self.config_path, 'w') as file:
            json.dump(self.snippets, file, indent=4)
