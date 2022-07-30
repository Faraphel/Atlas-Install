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

        self.checkbutton_override_random_new = ttk.Checkbutton(self, text=_("OVERRIDE_RANDOM_NEW"))
        self.frame_override_random_new = ttk.LabelFrame(self, labelwidget=self.checkbutton_override_random_new)
        self.frame_override_random_new.grid(row=1, column=1, sticky="NEWS")

        variable = tkinter.StringVar(self)
        variable.trace_add("write", lambda *_: setattr(self, "value", variable.get()))
        self.entry_override_random_new_cup = ttk.Entry(self.frame_override_random_new, width=70, textvariable=variable)
        self.entry_override_random_new_cup.grid(row=1, column=1, sticky="NEWS")

        self.button_preview_override_random_new = ttk.Button(self.frame_override_random_new, text="...", width=3)
        self.button_preview_override_random_new.configure(command=lambda: track_formatting.Window.ask_for_template(
            mod_config=self.master.master.mod_config,
            variable=variable,
            template=self.entry_override_random_new_cup.get(),
        ))
        self.button_preview_override_random_new.grid(row=1, column=2, sticky="NEWS")


class FrameSpecificSettings(ttk.Frame):
    def __init__(self, master: ttk.Notebook):
        super().__init__(master)
        master.add(self, text=_("SPECIFIC_MOD_SETTINGS"))

        for index, (settings_name, settings_data) in enumerate(self.master.master.mod_config.settings.items()):
            frame = ttk.LabelFrame(self, text=settings_name)
            frame.grid(row=index, column=1, sticky="NEWS")

            settings_data.tkinter_show(frame)
