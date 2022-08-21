import tkinter
from tkinter import ttk

from dataclasses import dataclass, field
from source.mkw.ModSettings import AbstractModSettings
from source.translation import translate as _


@dataclass(init=False)
class Choices(AbstractModSettings):
    """
    This setting type allow you to input a string text.
    You can optionally add a "preview" to allow the user to use a window to select the value.
    """

    type = "boolean"

    def tkinter_show(self, master, checkbox) -> None:
        super().tkinter_show(master, checkbox)
        variable = self.tkinter_variable(tkinter.BooleanVar)

        radiobutton_on = ttk.Radiobutton(master, text=_("DISABLED"), variable=variable, value=False)
        radiobutton_on.grid(row=1, column=1, sticky="E")
        radiobutton_off = ttk.Radiobutton(master, text=_("ENABLED"), variable=variable, value=True)
        radiobutton_off.grid(row=1, column=2, sticky="E")
