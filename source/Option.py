import json
import os

from .definition import restart


class Option:
    def __init__(self, language: str = "en", format: str = "FST", dont_check_for_update: bool = False,
                 process_track: int = 8):
        """
        class for Option
        """
        self.language = language
        self.format = format
        self.dont_check_for_update = dont_check_for_update
        self.process_track = process_track

    def edit(self, option: str, value: any, need_restart: bool = False, gui=None) -> None:
        """
        Change the value of a parameter
        :param option: the name of the option to change
        :param value: the new value for the option
        :param need_restart: do this value need a restart ?
        :param gui: the gui object to restart
        """
        if type(value) in [str, int, bool]:
            setattr(self, option, value)
        else:
            setattr(self, option, value.get())
        self.save_to_file()
        if need_restart: restart()

    def load_from_file(self, option_file: str = "./option.json") -> None:
        """
        Load all options from a json file
        :param option_file: the file where to load option
        """
        if os.path.exists(option_file):
            with open(option_file, encoding="utf-8") as file:
                file_json = json.load(file)
                self.load_from_json(file_json)

    def load_from_json(self, option_json: dict) -> None:
        """
        Load all options from a dictionnary
        :param option_json: the dictionnary to load
        """
        for key, value in option_json.items():  # load all value in the json as class attribute
            setattr(self, key, value)

    def save_to_file(self, option_file: str = "./option.json") -> None:
        """
        Save all options to a file
        :param option_file: the file where to save option
        """
        option_json: dict = self.__dict__  # this return all attribute of the class as a dict
        with open(option_file, "w", encoding="utf-8") as file:
            json.dump(option_json, file, ensure_ascii=False)

