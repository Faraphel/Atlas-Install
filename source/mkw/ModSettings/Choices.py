import tkinter
from dataclasses import field, dataclass
from tkinter import ttk

from source.mkw.ModSettings import AbstractModSettings


@dataclass(init=False)
class Choices(AbstractModSettings):
    """
    This setting type allow you to input a string text.
    You can optionally add a "preview" to allow the user to use a window to select the value.
    """

    type = "choices"

    def __init__(self, choices: list[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.choices = choices if choices is not None else []

    def tkinter_show(self, master, checkbox) -> None:
        super().tkinter_show(master, checkbox)
        variable = self.tkinter_variable(tkinter.StringVar)
        master.grid_columnconfigure(1, weight=1)

        combobox = ttk.Combobox(master, values=self.choices, textvariable=variable)
        combobox.grid(row=1, column=1, sticky="EW")
