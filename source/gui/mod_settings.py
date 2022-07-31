import tkinter
from tkinter import ttk
from source.translation import translate as _
from source.gui.preview import track_formatting


ModConfig: any


class Window(tkinter.Toplevel):
    def __init__(self, mod_config: "ModConfig"):
        super().__init__()
        self.resizable(False, False)
        self.grab_set()

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

        self.columnconfigure(1, weight=1)

        for index, (settings_name, settings_data) in enumerate(self.master.master.mod_config.global_settings.items()):
            checkbox = ttk.Checkbutton(self, text=settings_name)
            frame = ttk.LabelFrame(self, labelwidget=checkbox)
            frame.grid(row=index, column=1, sticky="NEWS")

            settings_data.tkinter_show(frame, checkbox)


class FrameSpecificSettings(ttk.Frame):
    def __init__(self, master: ttk.Notebook):
        super().__init__(master)
        master.add(self, text=_("SPECIFIC_MOD_SETTINGS"))

        self.columnconfigure(1, weight=1)

        for index, (settings_name, settings_data) in enumerate(self.master.master.mod_config.specific_settings.items()):
            checkbox = ttk.Checkbutton(self, text=settings_name)
            frame = ttk.LabelFrame(self, labelwidget=checkbox)
            frame.grid(row=index, column=1, sticky="NEWS")

            settings_data.tkinter_show(frame, checkbox)
