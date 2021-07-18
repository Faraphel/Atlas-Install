import json
import os


def load_from_file(self, option_file: str = "./option.json"):
    if os.path.exists(option_file):
        with open(option_file, encoding="utf-8") as file:
            file_json = json.load(file)
            self.load_from_json(file_json)
