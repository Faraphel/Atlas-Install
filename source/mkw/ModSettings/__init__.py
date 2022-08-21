from abc import ABC, abstractmethod
from typing import Type, TYPE_CHECKING

from source.translation import translate as _

if TYPE_CHECKING:
    import tkinter


class InvalidSettingsType(Exception):
    def __init__(self, settings_type: str):
        super().__init__(_("TYPE_MOD_SETTINGS", " '", settings_type, "' ", "NOT_FOUND"))


class AbstractModSettings(ABC):
    """
    Base class for every different type of ModSettings
    """

    type: str  # type name of the settings

    def __init__(self, text: dict[str, str] = None, description: dict[str, str] = None, enabled: bool = False,
                 default: str | None = None, value: any = None):

        self.text = text if text is not None else {}  # text to display in the window settings.
        self.description = description if description is not None else {}  # desc to display in the window settings.

        self.enabled = enabled  # is the settings enabled
        self.default: str | None = default  # default value of the settings (used is disabled)
        self._value: any = value if value is not None else default  # value for the settings

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
    def tkinter_show(self, master, enabled_variable: "tkinter.BooleanVar" = None) -> None:
        """
        Show the option inside a tkinter widget
        :master: master widget
        :checkbox: checkbox inside the labelframe allowing to enable or disable the setting
        """
        import tkinter
        if enabled_variable is None: enabled_variable = tkinter.BooleanVar()

        enabled_variable.set(self.enabled)
        enabled_variable.trace_add("write", lambda *_: setattr(self, "enabled", enabled_variable.get()))
        ...

    def tkinter_variable(self, vartype: Type["tkinter.Variable"]) -> "tkinter.Variable":
        """
        Create a tkinter variable that is linked to the ModSettings value
        :param vartype: the type of variable (boolean, int string)
        :return: the tkinter variable
        """
        variable = vartype(value=self._value)
        variable.trace_add("write", lambda *_: setattr(self, "_value", variable.get()))
        return variable

    @staticmethod
    def tkinter_bind(master, enabled_variable: "tkinter.BooleanVar" = None) -> None:
        """
        Bind all widget of the master so that clicking on the frame enable automatically the option
        :param master: the frame containing the elements
        :param enabled_variable: the variable associated with the enable state
        :return:
        """
        if enabled_variable is None: return

        for child in master.winfo_children():
            child.bind("<Button-1>", lambda e: enabled_variable.set(True))


def get(settings_data: dict) -> "AbstractModSettings":
    """
    Load all the settings in mod_settings_dict
    :param settings_data: dictionary containing all the settings defined for the mod
    """
    for subclass in filter(lambda subclass: subclass.type == settings_data["type"],
                           AbstractModSettings.__subclasses__()):
        settings_data.pop("type")
        return subclass(**settings_data)
    else: raise InvalidSettingsType(settings_data["type"])


# these import load the different ModSettings, and so get_mod_settings will be able to fetch them with __subclasses__
from source.mkw.ModSettings import Choices, String, Boolean
