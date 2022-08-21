import tkinter
from tkinter import ttk
from typing import TYPE_CHECKING

from source.translation import translate as _, translate_external
from source.mkw import ModSettings

if TYPE_CHECKING:
    from source.mkw.ModConfig import ModConfig
    from source.mkw.ModSettings import AbstractModSettings
    from source.option import Options


class Window(tkinter.Toplevel):
    def __init__(self, mod_config: "ModConfig", options: "Options"):
        super().__init__()
        self.root = self
        self.resizable(False, False)
        self.grab_set()

        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        self.mod_config = mod_config
        self.options = options

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

        if self.options.developer_mode.get():
            self.frame_testing_settings = FrameTesting(
                self.panel_window,
                _("TESTING_MOD_SETTINGS")
            )

        # add at the end a message from the mod creator where he can put some additional note about the settings.
        if text := translate_external(
                self.mod_config,
                self.options.language.get(),
                self.mod_config.messages.get("settings_description", {}).get("text", {})
        ):
            self.label_description = ttk.Label(self, text="\n" + text, foreground="gray")
            self.label_description.grid(row=2, column=1)


class NotebookSettings(ttk.Notebook):
    def __init__(self, master):
        super().__init__(master, width=500)
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
        language = self.root.options.language.get()

        for index, (settings_name, settings_data) in enumerate(settings.items()):
            text = translate_external(self.root.mod_config, language, settings_data.text)
            description = translate_external(self.root.mod_config, language, settings_data.description)

            enabled_variable = tkinter.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(self, text=text, variable=enabled_variable)

            frame = ttk.LabelFrame(self, labelwidget=checkbox)
            frame.grid(row=index, column=1, sticky="NEWS")
            frame.columnconfigure(1, weight=1)

            action_frame = ttk.Frame(frame)
            action_frame.root = self.root
            action_frame.grid(row=1, column=1, sticky="NEWS")
            settings_data.tkinter_show(action_frame, enabled_variable)

            if description:
                description_label = ttk.Label(frame, text=description, wraplength=450,
                                              foreground="gray", justify=tkinter.CENTER)
                description_label.grid(row=2, column=1)


class FrameTesting(ttk.Frame):
    def __init__(self, master, text: str):
        super().__init__(master)
        master.add(self, text=text)
        self.root = self.master.root

        self.columnconfigure(1, weight=1)

        for index, (settings_name, settings_data) in enumerate({
            "TEST_PREVIEW_FORMATTING": ModSettings.String.String(preview="track_formatting"),
            "TEST_PREVIEW_SELECTING": ModSettings.String.String(preview="track_selecting"),
            "TEST_PREVIEW_SORTING": ModSettings.String.String(preview="track_sorting"),

            "TEST_STRING": ModSettings.String.String(),
            "TEST_CHOICES": ModSettings.Choices.Choices(["test1", "test2", "test3"]),
            "TEST_BOOLEAN": ModSettings.Boolean.Boolean(),
        }.items()):
            frame = ttk.LabelFrame(self, text=settings_name)
            frame.root = self.root
            frame.grid(row=index, column=1, sticky="NEWS")
            settings_data.tkinter_show(frame)
