import json
import tkinter
from pathlib import Path
from tkinter import ttk
from tkinter import filedialog
from typing import TYPE_CHECKING

from source.translation import translate as _, translate_external
from source.mkw.ModSettings import SETTINGS_FILE_EXTENSION

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

        self.frame_action = FrameAction(self)
        self.frame_action.grid(row=10, column=1)

        # add at the end a message from the mod creator where he can put some additional note about the settings.
        if text := translate_external(
                self.mod_config,
                self.options.language.get(),
                self.mod_config.messages.get("settings_description", {}).get("text", {})
        ):
            self.label_description = ttk.Label(self, text=text, foreground="gray")
            self.label_description.grid(row=20, column=1)

    def restart(self):
        """
        Restart the window
        """

        self.destroy()
        self.__init__(self.mod_config, self.options)


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
            checkbox = ttk.Checkbutton(self, text=f"{text} {settings_data.suffix}", variable=enabled_variable)

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

        from source.mkw.ModSettings.SettingsType.Choices import Choices
        from source.mkw.ModSettings.SettingsType.Boolean import Boolean
        from source.mkw.ModSettings.SettingsType.String import String

        self.columnconfigure(1, weight=1)

        for index, (settings_name, settings_data) in enumerate({
            "TEST_PREVIEW_FORMATTING": String(preview="track_formatting"),
            "TEST_PREVIEW_SELECTING": String(preview="track_selecting"),
            "TEST_PREVIEW_SORTING": String(preview="track_sorting"),

            "TEST_STRING": String(),
            "TEST_CHOICES": Choices(["test1", "test2", "test3"]),
            "TEST_BOOLEAN": Boolean(),
        }.items()):
            frame = ttk.LabelFrame(self, text=settings_name)
            frame.root = self.root
            frame.grid(row=index, column=1, sticky="NEWS")
            settings_data.tkinter_show(frame)


class FrameAction(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.root = master.root

        self.button_import_settings = ttk.Button(self, text=_("IMPORT_SETTINGS"), width=20,
                                                 command=self.import_settings)
        self.button_import_settings.grid(row=1, column=1)
        self.button_export_settings = ttk.Button(self, text=_("EXPORT_SETTINGS"), width=20,
                                                 command=self.export_settings)
        self.button_export_settings.grid(row=1, column=2)

    def import_settings(self) -> None:
        """
        Import a settings values file into the settings
        """

        path = filedialog.askopenfilename(
            title=_("IMPORT_SETTINGS"),
            filetypes=[(_("SETTINGS_FILE"), f"*{SETTINGS_FILE_EXTENSION}")]
        )

        # si le fichier n'a pas été choisi, ignore
        if path == "": return
        path = Path(path)

        with open(path, "r", encoding="utf8") as file:
            values_dict: dict[str, dict] = json.load(file)

        self.root.mod_config.global_settings.import_values(values_dict["global_settings"])
        self.root.mod_config.specific_settings.import_values(values_dict["specific_settings"])

        self.root.restart()  # restart the window to update the values

    def export_settings(self) -> None:
        """
        Export settings values into a file
        """

        path = filedialog.asksaveasfilename(
            title=_("EXPORT_SETTINGS"),
            filetypes=[(_("SETTINGS_FILE"), f"*{SETTINGS_FILE_EXTENSION}")]
        )

        # si le fichier n'a pas été choisi, ignore
        if path == "": return
        # s'il manque une extension au fichier, ignore
        if not path.endswith(SETTINGS_FILE_EXTENSION): path += SETTINGS_FILE_EXTENSION
        path = Path(path)

        with open(path, "w", encoding="utf8") as file:
            json.dump(
                {
                    "global_settings": self.root.mod_config.global_settings.export_values(),
                    "specific_settings": self.root.mod_config.specific_settings.export_values(),
                },
                file,
                ensure_ascii=False,
                indent=4
            )
