import json
from pathlib import Path

from source import restart_program


class Option:
    __slots__ = ("_path", "_options")

    reboot_on_change: list[any] = ["language"]
    default_options: dict[str, any] = {
        "language": "en"
    }

    def __init__(self, language=None):
        self._path: Path | None = None
        self._options: dict[str, any] = self.default_options.copy()
        if language is not None: self._options["language"] = language

    def __getitem__(self, key: str) -> any:
        """
        get an options value from its key
        :param key: the option name
        :return: the value of the option
        """
        return self._options[key]

    def __setitem__(self, key: str, value: any) -> None:
        """
        change the value of an options for a key, if the options have been loaded from a file, save it inside
        if the option is in the reboot_on_change list, reboot the program
        :param key: the name of the option to edit
        :param value: the value of the option
        :return:
        """
        self._options[key] = value
        if self._path: self.save()
        if key in self.reboot_on_change: restart_program()

    def save(self, option_file: Path | str = None) -> None:
        """
        save the options to the file
        :return: None
        """
        if option_file is None: option_file = self._path
        if isinstance(option_file, str): option_file = Path(option_file)

        with option_file.open("w") as file:
            json.dump(self._options, file, indent=4, ensure_ascii=False)

    @classmethod
    def from_dict(cls, option_dict: dict) -> "Option":
        """
        Create a Option from a dict if the parameters are in the default_options
        :param option_dict: dict containing the configuration
        :return: Option
        """
        kwargs = {}
        for key in cls.default_options.keys():
            if "key" in option_dict: kwargs[key] = option_dict[key]

        return cls(**kwargs)

    @classmethod
    def from_file(cls, option_file: str | Path) -> "Option":
        """
        Loads the option from a file. If the option file does not exist, only load default configuration
        :param option_file: the option file
        :return: Option
        """
        if isinstance(option_file, str): option_file = Path(option_file)

        if not option_file.exists(): obj = cls()
        else: obj = cls.from_dict(json.loads(option_file.read_text(encoding="utf8")))

        obj._path = option_file
        return obj
