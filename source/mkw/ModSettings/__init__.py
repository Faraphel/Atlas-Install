import tkinter
from tkinter import ttk
from abc import ABC, abstractmethod

from source.translation import translate as _


class InvalidSettingsType(Exception):
    def __init__(self, settings_type: str):
        super().__init__(_("TYPE_MOD_SETTINGS", " '", settings_type, "' ", "NOT_FOUND"))


class AbstractModSettings(ABC):
    """
    Base class for every different type of ModSettings
    """

    type: str  # type name of the settings
    text: dict[str]  # text to display in the settings window depending on the language
    enabled: bool  # is the settings enabled
    default: str | None  # default value of the settings (used is disabled)
    _value: any  # value for the settings

    @property
    def value(self) -> "any | None":
        """
        If the option is enabled, return the value, else return the default value
        :return: value if the setting is enabled, default otherwise
        """
        return self._value if self.enabled else self.default

    @property
    def is_modified(self) -> bool:
        """
        Return if the settings have been modified compared the the default value
        """
        return self.value == self.default

    @abstractmethod
    def tkinter_show(self, master: ttk.LabelFrame, enabled_variable: tkinter.BooleanVar) -> None:
        """
        Show the option inside a tkinter widget
        :master: master widget
        :checkbox: checkbox inside the labelframe allowing to enable or disable the setting
        """
        enabled_variable.set(self.enabled)
        enabled_variable.trace_add("write", lambda *_: setattr(self, "enabled", enabled_variable.get()))
        ...

    @classmethod
    def get(cls, settings_data: dict) -> "AbstractModSettings":
        """
        Load all the settings in mod_settings_dict
        :param settings_data: dictionary containing all the settings defined for the mod
        """
        for subclass in filter(lambda subclass: subclass.type == settings_data["type"], cls.__subclasses__()):
            settings_data.pop("type")
            return subclass(**settings_data)
        else: raise InvalidSettingsType(settings_data["type"])


# these import load the different ModSettings, and so get_mod_settings will be able to fetch them with __subclasses__
from source.mkw.ModSettings import Choices, String, Check
