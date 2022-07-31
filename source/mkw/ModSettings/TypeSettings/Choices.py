import tkinter
from tkinter import ttk
from source.mkw.ModSettings.TypeSettings import AbstractTypeSettings


class Choices(AbstractTypeSettings):
    """
    This setting type allow you to input a string text.
    You can optionally add a "preview" to allow the user to use a window to select the value.
    """

    type = "choices"

    def __init__(self, choices: list[str], value: str = None, enabled: bool = False):
        self.value = value if value is not None else choices[0]
        self.enabled = enabled
        self.choices = choices

    def tkinter_show(self, master: ttk.LabelFrame, checkbox) -> None:
        super().tkinter_show(master, checkbox)

        value_variable = tkinter.StringVar(master, value=self.value)
        value_variable.trace_add("write", lambda *_: setattr(self, "value", value_variable.get()))

        combobox = ttk.Combobox(master, values=self.choices, textvariable=value_variable)
        combobox.grid(row=1, column=1, sticky="EW")
