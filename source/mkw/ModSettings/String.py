import tkinter
from tkinter import ttk

from source.mkw.ModSettings import AbstractModSettings
from source.gui.preview import AbstractPreviewWindow


class String(AbstractModSettings):
    """
    This setting type allow you to input a string text.
    You can optionally add a "preview" to allow the user to use a window to select the value.
    """

    type = "string"

    def __init__(self, value: str = None, preview: str = None, enabled: bool = False):
        self._value: str = value if value is not None else ""
        self.enabled = enabled
        self.preview: str | None = preview

    def tkinter_show(self, master: ttk.LabelFrame, checkbox) -> None:
        super().tkinter_show(master, checkbox)

        value_variable = tkinter.StringVar(master, value=self._value)
        value_variable.trace_add("write", lambda *_: setattr(self, "_value", value_variable.get()))

        entry = ttk.Entry(master, textvariable=value_variable)
        entry.grid(row=1, column=1, sticky="EW")

        if self.preview is not None:
            button = ttk.Button(
                master, text="...", width=3,
                command=lambda: AbstractPreviewWindow.get(
                    self.preview
                )(master.master.master.master.mod_config, value_variable)
            )
            button.grid(row=1, column=2, sticky="EW")
