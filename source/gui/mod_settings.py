import tkinter
from tkinter import ttk
from source.translation import translate as _
from source.gui.preview import track_formatting


ModConfig: any
AbstractModSettings: any


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

        self.frame_global_settings = FrameSettings(
            self.panel_window,
            _("GLOBAL_MOD_SETTINGS"),
            self.mod_config.global_settings
        )
        self.frame_specific_settings = FrameSettings(
            self.panel_window,
            _("SPECIFIC_MOD_SETTINGS"),
            self.mod_config.specific_settings
        )


class FrameSettings(ttk.Frame):
    def __init__(self, master: ttk.Notebook, text: str, settings: dict[str, "AbstractModSettings"]):
        """
        Create a frame where settings will be displayed
        :param master: master window
        :param text: text of the frame (shown in the notebook)
        :param settings: dictionary with the settings to show
        """
        super().__init__(master)
        master.add(self, text=text)

        self.columnconfigure(1, weight=1)

        for index, (settings_name, settings_data) in enumerate(settings.items()):
            checkbox = ttk.Checkbutton(self, text=settings_name)
            frame = ttk.LabelFrame(self, labelwidget=checkbox)
            frame.grid(row=index, column=1, sticky="NEWS")

            settings_data.tkinter_show(frame, checkbox)
