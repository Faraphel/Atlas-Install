import tkinter
from tkinter import ttk

from source.mkw.ModSettings import AbstractModSettings
from source.translation import translate as _


class Choices(AbstractModSettings):
    """
    This setting type allow you to input a string text.
    You can optionally add a "preview" to allow the user to use a window to select the value.
    """

    type = "check"

    def __init__(self, enabled: bool = False,
                 default: bool | None = None, text: dict[str, str] = None, description: dict[str, str] = None):
        self._value = default if default is not None else False
        self.default = default
        self.description = description if description is not None else {}
        self.enabled = enabled

        self.text = text if text is not None else {}

    def tkinter_show(self, master, checkbox) -> None:
        super().tkinter_show(master, checkbox)

        value_variable = tkinter.BooleanVar(master, value=self._value)
        value_variable.trace_add("write", lambda *_: setattr(self, "_value", value_variable.get()))

        radiobutton_on = ttk.Radiobutton(master, text=_("DISABLED"), variable=value_variable, value=False)
        radiobutton_on.grid(row=1, column=1, sticky="E")
        radiobutton_off = ttk.Radiobutton(master, text=_("ENABLED"), variable=value_variable, value=True)
        radiobutton_off.grid(row=1, column=2, sticky="E")
