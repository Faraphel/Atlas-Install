import tkinter
from tkinter import ttk
from abc import ABC, abstractmethod


class AbstractTypeSettings(ABC):
    type: str  # type name of the settings
    value: str  # value for the settings
    enabled: bool  # is the settings enabled

    @abstractmethod
    def __init__(self, value: str = None, preview: str = None, enabled: bool = False):
        ...

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


from source.mkw.ModSettings.TypeSettings import String, Choices
