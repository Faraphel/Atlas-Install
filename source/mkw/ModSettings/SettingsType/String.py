from source.mkw.ModSettings.AbstractModSettings import AbstractModSettings
from source.gui.preview import AbstractPreviewWindow


class String(AbstractModSettings):
    """
    This setting type allow you to input a string text.
    You can optionally add a "preview" to allow the user to use a window to select the value.
    """

    type = "string"

    def __init__(self, preview: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.preview = preview

    def tkinter_show(self, master, checkbox=None) -> None:
        import tkinter
        from tkinter import ttk

        super().tkinter_show(master, checkbox)
        variable = self.tkinter_variable(tkinter.StringVar)

        text = self.default if self.default is not None else ""
        text = text if self._value is None else self._value
        variable.set(text)

        master.grid_columnconfigure(1, weight=1)

        entry = ttk.Entry(master, textvariable=variable)
        entry.grid(row=1, column=1, sticky="EW")

        if self.preview is not None:
            button = ttk.Button(
                master, text="...", width=3,
                command=lambda: AbstractPreviewWindow.get(self.preview)(master.root.mod_config, variable)
            )
            button.grid(row=1, column=2, sticky="EW")

        self.tkinter_bind(master, checkbox)
