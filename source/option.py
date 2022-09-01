import json
from pathlib import Path

from source.utils import restart_program


class OptionLoadingError(Exception):
    def __init__(self):
        super().__init__(f"An error occurred while loading options. Try deleting the option.json file.")


class Option:
    """
    Class representing a single option. It mimic a TkinterVar to make binding easier
    """

    __slots__ = ("options", "_value", "reboot_on_change")

    def __init__(self, options: "Options", value: any, reboot_on_change: bool = False):
        self.options = options
        self._value = value
        self.reboot_on_change = reboot_on_change

    def get(self) -> any:
        """
        :return: the value of the option
        """
        return self._value

    def set(self, value, ignore_reboot: bool = False) -> None:
        """
        Set the value of the option and save the settings.
        :param value: the new value of the option
        :param ignore_reboot: should the installer ignore the reboot if the settings need it ?
        """
        self._value = value
        self.options.save()
        if self.reboot_on_change and not ignore_reboot: restart_program()


class Options:
    """
    Class representing a group of Options
    """

    __slots__ = ("_path", "_options")

    def __init__(self, path, **options):
        self._path: Path = Path(path)

        self._options: dict[str, Option] = {
            "language": Option(self, value="en", reboot_on_change=True),
            "threads": Option(self, value=8),
            "mystuff_pack_selected": Option(self, value=None),
            "mystuff_packs": Option(self, value={}),
            "extension": Option(self, value="WBFS"),
            "developer_mode": Option(self, value=False),
        }

        for option_name, option_value in options.items():
            self._options[option_name].set(option_value, ignore_reboot=True)

    def __getattr__(self, key: str) -> any:
        """
        get an options value from its key
        :param key: the option name
        :return: the value of the option
        """
        return self._options[key]

    def save(self) -> None:
        """
        save the options to the file
        :return: None
        """
        with self._path.open("w") as file:
            json.dump(self.to_dict(), file, indent=4, ensure_ascii=False)

    def to_dict(self) -> dict[str, any]:
        """
        Return the dictionary form of the options
        :return:
        """
        return {key: option.get() for key, option in self._options.items()}

    @classmethod
    def from_dict(cls, path: Path, option_dict: dict) -> "Options":
        """
        Create a Option from a dict if the parameters are in the default_options
        :param path: path to the option file
        :param option_dict: dict containing the configuration
        :return: Option
        """
        return cls(path, **option_dict)

    @classmethod
    def from_file(cls, option_file: str | Path) -> "Options":
        """
        Loads the option from a file. If the option file does not exist, only load default configuration
        :param option_file: the option file
        :return: Option
        """
        option_file = Path(option_file)
        try: data = json.loads(option_file.read_text(encoding="utf8")) if option_file.exists() else {}
        except Exception as exc: raise OptionLoadingError() from exc
        return cls.from_dict(option_file, data)

