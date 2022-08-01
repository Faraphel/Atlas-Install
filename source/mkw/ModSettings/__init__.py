import tkinter
from tkinter import ttk
from abc import ABC, abstractmethod


class InvalidSettingsType(Exception):
    def __init__(self, settings_type: str):
        super().__init__(f"Error : Type of mod settings '{settings_type}' not found.")


class AbstractModSettings(ABC):
    """
    Base class for every different type of ModSettings
    """

    type: str  # type name of the settings
    enabled: bool  # is the settings enabled
    _value: str  # value for the settings

    @abstractmethod
    def __init__(self, value: str = None, preview: str = None, enabled: bool = False):
        ...

    @property
    def value(self) -> "any | None":
        """
        If the option is enabled, return the value, else return None
        :return:
        """
        return self._value if self.enabled else None

    @abstractmethod
    def tkinter_show(self, master: ttk.LabelFrame, checkbox) -> None:
        """
        Show the option inside a tkinter widget
        :master: master widget
        :checkbox: checkbox inside the labelframe allowing to enable or disable the setting
        """
        master.grid_rowconfigure(1, weight=1)
        master.grid_columnconfigure(1, weight=1)

        enabled_variable = tkinter.BooleanVar(master, value=self.enabled)
        enabled_variable.trace_add("write", lambda *_: setattr(self, "enabled", enabled_variable.get()))
        checkbox.configure(variable=enabled_variable)
        ...

    @classmethod
    def get(cls, settings_dict: dict) -> dict[str, "AbstractModSettings"]:
        """
        Load all the settings in mod_settings_dict
        :param settings_dict: dictionary containing all the settings defined for the mod
        """
        settings: dict[str, AbstractModSettings] = {}

        for settings_name, settings_data in settings_dict.items():
            for subclass in filter(lambda subclass: subclass.type == settings_data["type"], cls.__subclasses__()):
                settings_data.pop("type")
                settings[settings_name] = subclass(**settings_data)
                break
            else: raise InvalidSettingsType(settings_name)

        return settings


# these import load the different ModSettings, and so get_mod_settings will be able to fetch them with __subclasses__
from source.mkw.ModSettings import Choices, String
