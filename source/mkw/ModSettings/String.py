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

    def __init__(self, preview: str = None, enabled: bool = False,
                 default: str | None = None, text: dict[str, str] = None, description: dict[str, str] = None):
        self._value: str = default if default is not None else ""
        self.default = default
        self.enabled = enabled

        self.text = text if text is not None else {}
        self.description = description if description is not None else {}
        self.preview: str | None = preview

    def tkinter_show(self, master, checkbox) -> None:
        super().tkinter_show(master, checkbox)

        master.grid_rowconfigure(1, weight=1)
        master.grid_columnconfigure(1, weight=1)

        value_variable = tkinter.StringVar(master, value=self._value)
        value_variable.trace_add("write", lambda *_: setattr(self, "_value", value_variable.get()))

        entry = ttk.Entry(master, textvariable=value_variable)
        entry.grid(row=1, column=1, sticky="EW")

        if self.preview is not None:
            button = ttk.Button(
                master, text="...", width=3,
                command=lambda: AbstractPreviewWindow.get(self.preview)(
                    master.master.master.master.mod_config, value_variable
                )
            )
            button.grid(row=1, column=2, sticky="EW")

