import tkinter
from tkinter import ttk

from source.mkw.ModSettings.TypeSettings import AbstractTypeSettings


class String(AbstractTypeSettings):
    """
    This setting type allow you to input a string text.
    You can optionally add a "preview" to allow the user to use a window to select the value.
    """

    type = "string"

    def __init__(self, value=None, preview: str = None):
        self.value: str = value if value is not None else ""
        self.preview: str | None = preview

    def tkinter_show(self, master) -> None:
        variable = tkinter.StringVar(master, value=self.value)
        variable.trace_add("write", lambda *_: setattr(self, "value", variable.get()))

        entry = ttk.Entry(master, width=100, textvariable=variable)
        entry.grid(row=1, column=1, sticky="NEWS")

        button = ttk.Button(master, text="...", width=3)
        button.grid(row=1, column=2, sticky="NEWS")
