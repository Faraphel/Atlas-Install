import tkinter
from tkinter import ttk
from typing import TYPE_CHECKING

from source.translation import translate as _, translate_external

if TYPE_CHECKING:
    from source.mkw.ModConfig import ModConfig
    from source.mkw.ModSettings import AbstractModSettings


class Window(tkinter.Toplevel):
    def __init__(self, mod_config: "ModConfig"):
        super().__init__()
        self.root = self.master.root
        self.resizable(False, False)
        self.grab_set()

        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        self.mod_config = mod_config

        self.panel_window = NotebookSettings(self)
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


class NotebookSettings(ttk.Notebook):
    def __init__(self, master):
        super().__init__(master)
        self.root = self.master.root


class FrameSettings(ttk.Frame):
    def __init__(self, master, text: str, settings: dict[str, "AbstractModSettings"]):
        """
        Create a frame where settings will be displayed
        :param master: master window
        :param text: text of the frame (shown in the notebook)
        :param settings: dictionary with the settings to show
        """
        super().__init__(master)
        master.add(self, text=text)
        self.root = self.master.root

        self.columnconfigure(1, weight=1)

        def get_event_checkbox(enabled_variable: tkinter.BooleanVar):
            """
            Return the event for any child of a frmae when clicked
            """
            return lambda event: enabled_variable.set(True)

        for index, (settings_name, settings_data) in enumerate(settings.items()):
            text = translate_external(
                self.master.master.mod_config,
                self.root.options["language"],
                settings_data.text,
            )

            enabled_variable = tkinter.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(self, text=text, variable=enabled_variable)
            frame = ttk.LabelFrame(self, labelwidget=checkbox)
            frame.grid(row=index, column=1, sticky="NEWS")

            settings_data.tkinter_show(frame, enabled_variable)

            # if any of the label child are clicked, automatically enable the option
            for child in frame.winfo_children():
                child.bind("<Button-1>", get_event_checkbox(enabled_variable))
