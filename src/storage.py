import os
#this is to handle file paths and dir
import json

class SnippetStorage:
    #init is special method constructor. Initialize object attributes
    #"self" muist be included in param because unlike java compiler 
    # doesn't add it for you to use in all methods
    def __init__(self):
        appdata_dir = os.getenv('APPDATA')

        #making subfolder for app
        self.config_dir = os.path.join(appdata_dir, 'snippet_app')
        self.config_path = os.path.join(self.config_dir, 'config.json')
        os.makedirs(self.config_dir, exist_ok=True)
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
