import tkinter
from tkinter import ttk
from source.translation import translate as _


ModConfig: any


class Window(tkinter.Toplevel):
    def __init__(self, mod_config: "ModConfig"):
        super().__init__()

        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        self.mod_config = mod_config

        self.panel_window = ttk.Notebook(self)
        self.panel_window.grid(row=1, column=1, sticky="NEWS")

        self.frame_global_settings = FrameGlobalSettings(self.panel_window)
        self.frame_specific_settings = FrameSpecificSettings(self.panel_window)


class FrameGlobalSettings(ttk.Frame):
    def __init__(self, master: ttk.Notebook):
        super().__init__(master)
        master.add(self, text=_("GLOBAL_MOD_SETTINGS"))

        # TODO: overwrite new tracks entry


class FrameSpecificSettings(ttk.Frame):
    def __init__(self, master: ttk.Notebook):
        super().__init__(master)
        master.add(self, text=_("SPECIFIC_MOD_SETTINGS"))
