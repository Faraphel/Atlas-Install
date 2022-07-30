import tkinter
from tkinter import ttk
from source.mkw.ModSettings.TypeSettings import AbstractTypeSettings


class Choices(AbstractTypeSettings):
    """
    This setting type allow you to input a string text.
    You can optionally add a "preview" to allow the user to use a window to select the value.
    """

    type = "choices"

    def __init__(self, choices: list[str], value: str = None):
        self.value = value if value is not None else choices[0]
        self.choices = choices

    def tkinter_show(self, master) -> None:
        variable = tkinter.StringVar(master, value=self.value)
        variable.trace_add("write", lambda *_: setattr(self, "value", variable.get()))

        combobox = ttk.Combobox(master, width=100, values=self.choices, textvariable=variable)
        combobox.grid(row=1, column=1)
