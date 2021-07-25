import json
import os


class Option:
    def __init__(self):
        """
        class for Option
        """
        self.language = "en"
        self.format = "FST"
        self.disable_download = False
        self.del_track_after_conv = False
        self.dont_check_for_update = False
        self.dont_check_track_sha1 = False
        self.process_track = 8

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
        if need_restart: gui.restart()

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

