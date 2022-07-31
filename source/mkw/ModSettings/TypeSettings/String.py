import tkinter
from tkinter import ttk

from source.mkw.ModSettings.TypeSettings import AbstractTypeSettings
from source.gui.preview import get_preview_window_class


class String(AbstractTypeSettings):
    """
    This setting type allow you to input a string text.
    You can optionally add a "preview" to allow the user to use a window to select the value.
    """

    type = "string"

    def __init__(self, value: str = None, preview: str = None, enabled: bool = False):
        self.value: str = value if value is not None else ""
        self.enabled = enabled
        self.preview: str | None = preview

    def tkinter_show(self, master: ttk.LabelFrame, checkbox) -> None:
        super().tkinter_show(master, checkbox)

        value_variable = tkinter.StringVar(master, value=self.value)
        value_variable.trace_add("write", lambda *_: setattr(self, "value", value_variable.get()))

        entry = ttk.Entry(master, textvariable=value_variable)
        entry.grid(row=1, column=1, sticky="NEWS")

        if self.preview is not None:
            button = ttk.Button(
                master, text="...", width=3,
                command=lambda: get_preview_window_class(
                    self.preview
                )(master.master.master.master.mod_config, value_variable)
            )
            button.grid(row=1, column=2, sticky="NEWS")
