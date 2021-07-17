import json
import os


class Option:
    def __init__(self):
        self.language = "en"
        self.format = "FST"
        self.disable_download = False
        self.del_track_after_conv = False
        self.dont_check_for_update = False
        self.dont_check_track_sha1 = False
        self.process_track = 8

    def load_from_json(self, option_json: dict):
        for key, value in option_json.items():    # load all value in the json as class attribute
            setattr(self, key, value)

    def load_from_file(self, option_file: str = "./option.json"):
        if os.path.exists(option_file):
            with open(option_file, encoding="utf-8") as file:
                file_json = json.load(file)
                self.load_from_json(file_json)

    def save_to_file(self, option_file: str = "./option.json"):
        option_json: dict = self.__dict__  # this return all attribute of the class as a dict
        with open(option_file, "w", encoding="utf-8") as file:
            json.dump(option_json, file, ensure_ascii=False)

    def edit(self, option, value, need_restart=False, gui=None):
        if type(value) in [str, int, bool]: setattr(self, option, value)
        else: setattr(self, option, value.get())
        self.save_to_file()
        if need_restart: gui.restart()
