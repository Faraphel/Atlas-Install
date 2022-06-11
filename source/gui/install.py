import enum
import shutil
import tkinter
from pathlib import Path
import json
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import webbrowser
from typing import Generator

from source.gui import better_gui_error
from source.mkw.Game import Game
from source.mkw.ModConfig import ModConfig
from source.translation import translate as _
from source import event
from source import *
import os


class SourceGameError(Exception):
    def __init__(self, path: Path | str):
        super().__init__(f"Invalid path for source game : {path}")


class DestinationGameError(Exception):
    def __init__(self, path: Path | str):
        super().__init__(f"Invalid path for destination game : {path}")


class InstallerState(enum.Enum):
    IDLE = 0
    INSTALLING = 1


# Main window for the installer
class Window(tkinter.Tk):
    def __init__(self):
        super().__init__()

        self.title(_("INSTALLER_TITLE"))
        self.resizable(False, False)
        self.iconbitmap("./assets/icon.ico")

        # menu bar
        self.menu = Menu(self)
        self.config(menu=self.menu)

        # main frame
        self.select_pack = SelectPack(self)
        self.select_pack.grid(row=1, column=1, sticky="w")

        self.source_game = SourceGame(self)
        self.source_game.grid(row=2, column=1, sticky="nsew")

        self.destination_game = DestinationGame(self)
        self.destination_game.grid(row=3, column=1, sticky="nsew")

        self.button_install = ButtonInstall(self)
        self.button_install.grid(row=4, column=1, sticky="nsew")

        self.progress_bar = ProgressBar(self)
        self.progress_bar.grid(row=5, column=1, sticky="nsew")

        self.set_state(InstallerState.IDLE)

    def run(self) -> None:
        """
        Run the installer
        """
        event.initialise_plugins()
        self.after(0, self.run_after)
        self.mainloop()

    @event.register
    def run_after(self) -> None:
        """
        Run after the installer has been initialised, can be used to add plugins
        :return:
        """
        return None

    def set_state(self, state: InstallerState) -> None:
        """
        Set the progress bar state when the installer change state
        :param state: state of the installer
        :return:
        """
        for child in self.winfo_children():
            getattr(child, "set_state", lambda *_: "pass")(state)

    def progress_function(self, func_gen: Generator) -> None:
        """
        Run a generator function that yield status for the progress bar
        :return:
        """
        # get the generator data yield by the generator function
        for step_data in func_gen:
            if "description" in step_data: self.progress_bar.set_description(step_data["description"])
            if "maximum" in step_data: self.progress_bar.set_maximum(step_data["maximum"])
            if "step" in step_data: self.progress_bar.step(step_data["step"])
            if "value" in step_data: self.progress_bar.set_value(step_data["value"])
            if "determinate" in step_data: self.progress_bar.set_determinate(step_data["determinate"])

    def get_mod_config(self) -> ModConfig:
        """
        Get the mod configuration
        :return: Get the mod configuration
        """
        return self.select_pack.mod_config

    def get_source_path(self) -> Path:
        """
        Get the path of the source game
        :return: path of the source game
        """
        return self.source_game.get_path()

    def get_destination_path(self) -> Path:
        """
        Get the path of the destination game
        :return: path of the destination game
        """
        return self.destination_game.get_path()


# Menu bar
class Menu(tkinter.Menu):
    def __init__(self, master):
        super().__init__(master)

        self.language = self.Language(self)
        self.track_configuration = self.TrackConfiguration(self)
        self.advanced = self.Advanced(self)
        self.help = self.Help(self)

    # Language menu
    class Language(tkinter.Menu):
        def __init__(self, master: tkinter.Menu):
            super().__init__(master, tearoff=False)

            master.add_cascade(label=_("LANGUAGE_SELECTION"), menu=self)

            for file in Path("./assets/language/").iterdir():
                self.add_command(label=json.loads(file.read_text(encoding="utf8"))["name"])

    # Track configuration menu
    class TrackConfiguration(tkinter.Menu):
        def __init__(self, master: tkinter.Menu):
            super().__init__(master, tearoff=False)

            master.add_cascade(label=_("TRACK_CONFIGURATION"), menu=self)
            self.add_command(label="Change configuration")

    # Advanced menu
    class Advanced(tkinter.Menu):
        def __init__(self, master: tkinter.Menu):
            super().__init__(master, tearoff=False)

            master.add_cascade(label=_("ADVANCED_CONFIGURATION"), menu=self)
            self.add_command(label="Debug mode")

    # Help menu
    class Help(tkinter.Menu):
        def __init__(self, master: tkinter.Menu):
            super().__init__(master, tearoff=False)

            master.add_cascade(label="Help", menu=self)
            self.menu_id = self.master.index(tkinter.END)

            self.add_command(label="Discord", command=lambda: webbrowser.open(discord_url))
            self.add_command(label="Github Wiki", command=lambda: webbrowser.open(github_wiki_url))

    def set_installation_state(self, state: InstallerState) -> bool:
        """
        Set the installation state of the installer
        :param state: The state to set the installer to
        :return: True if the state was set, False if not
        """

    def set_state(self, state: InstallerState) -> None:
        """
        Set the progress bar state when the installer change state
        :param state: state of the installer
        :return:
        """
        # get the last child id of the menu

        for child_id in range(1, self.index(tkinter.END) + 1):
            # don't modify the state of the help menu
            if child_id == self.help.menu_id: continue

            match state:
                case state.IDLE: self.entryconfigure(child_id, state=tkinter.NORMAL)
                case state.INSTALLING: self.entryconfigure(child_id, state=tkinter.DISABLED)


# Select game frame
class SourceGame(ttk.LabelFrame):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master, text="Original Game File")

        self.entry = ttk.Entry(self, width=50)
        self.entry.grid(row=1, column=1, sticky="nsew")

        self.button = ttk.Button(self, text="...", width=2, command=self.select)
        self.button.grid(row=1, column=2, sticky="nsew")

    def select(self) -> None:
        """
        Select the source game
        :return:
        """
        path = Path(tkinter.filedialog.askopenfilename(
            title=_("SELECT_SOURCE_GAME"),
            filetypes=[(_("WII GAMES"), "*.iso *.wbfs *.dol")],
        ))
        # if the user didn't select any file, return None
        if not path.exists():
            messagebox.showerror(_("ERROR"), _("ERROR_INVALID_SOURCE_GAME"))
            return

        self.set_path(path)

    def set_path(self, path: Path) -> None:
        """
        Set the source game path
        :param path:
        :return:
        """
        self.entry.delete(0, tkinter.END)
        self.entry.insert(0, str(path.absolute()))

        self.master.destination_game.set_path(path.parent)

    def get_path(self) -> Path:
        """
        Get the source game path
        :return: the game path
        """
        path = Path(self.entry.get())
        if not path.exists(): raise SourceGameError(path)
        return path

    def set_state(self, state: InstallerState) -> None:
        """
        Set the progress bar state when the installer change state
        :param state: state of the installer
        :return:
        """
        for child in self.winfo_children():
            match state:
                case InstallerState.IDLE: child.config(state="normal")
                case InstallerState.INSTALLING: child.config(state="disabled")


# Select game destination frame
class DestinationGame(ttk.LabelFrame):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master, text="Game Directory Destination")

        self.entry = ttk.Entry(self, width=50)
        self.entry.grid(row=1, column=1, sticky="nsew")

        self.button = ttk.Button(self, text="...", width=2, command=self.select)
        self.button.grid(row=1, column=2, sticky="nsew")

    def select(self) -> None:
        """
        Select the source game
        :return:
        """
        path = Path(tkinter.filedialog.askdirectory(
            title=_("SELECT_DESTINATION_GAME"),
        ))

        path.mkdir(mode=0o777, parents=True, exist_ok=True)

        self.set_path(path)

    def set_path(self, path: Path):
        if not os.access(path, os.W_OK):
            messagebox.showwarning(_("WARNING"), _("WARNING_DESTINATION_GAME_NOT_WRITABLE"))

        self.entry.delete(0, tkinter.END)
        self.entry.insert(0, str(path.absolute()))

    def get_path(self) -> Path:
        """
        Get the destination game path
        :return: the game path
        """
        path = Path(self.entry.get())
        if not path.exists(): raise DestinationGameError(path)
        return path

    def set_state(self, state: InstallerState) -> None:
        """
        Set the progress bar state when the installer change state
        :param state: state of the installer
        :return:
        """
        for child in self.winfo_children():
            match state:
                case InstallerState.IDLE: child.config(state="normal")
                case InstallerState.INSTALLING: child.config(state="disabled")


# Install button
class ButtonInstall(ttk.Button):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master, text="Install", command=self.install)

    @threaded
    @better_gui_error
    def install(self):
        try:
            self.master.set_state(InstallerState.INSTALLING)

            # check if the user entered a source path
            source_path = self.master.get_source_path()
            if str(source_path) == ".":
                messagebox.showerror(_("ERROR"), _("ERROR_INVALID_SOURCE_GAME"))
                return

            # check if the user entered a destination path
            destination_path = self.master.get_destination_path()
            if str(destination_path) == ".":
                messagebox.showerror(_("ERROR"), _("ERROR_INVALID_DESTINATION_GAME"))
                return

            # get space remaining on the C: drive
            if shutil.disk_usage(".").free < minimum_space_available:
                if not messagebox.askokcancel(_("WARNING"), _("WARNING_LOW_SPACE_CONTINUE")):
                    return

            game = Game(source_path)
            mod_config = self.master.get_mod_config()
            self.master.progress_function(game.install_mod(destination_path, mod_config))

        finally:
            self.master.set_state(InstallerState.IDLE)

    def set_state(self, state: InstallerState) -> None:
        """
        Set the progress bar state when the installer change state
        :param state: state of the installer
        :return:
        """
        match state:
            case InstallerState.IDLE: self.config(state="normal")
            case InstallerState.INSTALLING: self.config(state="disabled")


# Progress bar
class ProgressBar(ttk.LabelFrame):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master)

        # make the element fill the whole frame
        self.columnconfigure(1, weight=1)

        self.progress_bar = ttk.Progressbar(self, orient="horizontal")
        self.progress_bar.grid(row=1, column=1, sticky="nsew")

        self.description = ttk.Label(self, text="", anchor="center", font=("TkDefaultFont", 10))
        self.description.grid(row=2, column=1, sticky="nsew")

    def set_state(self, state: InstallerState) -> None:
        """
        Set the progress bar state when the installer change state
        :param state: state of the installer
        :return:
        """
        match state:
            case InstallerState.IDLE: self.grid_remove()
            case InstallerState.INSTALLING: self.grid()

    def set_description(self, desc: str) -> None:
        """
        Set the progress bar description
        :param desc: description
        :return:
        """
        self.description.config(text=desc)

    def set_maximum(self, maximum: int) -> None:
        """
        Set the progress bar maximum value
        :param maximum: the maximum value
        :return:
        """
        self.progress_bar.configure(maximum=maximum)

    def set_value(self, value: int) -> None:
        """
        Set the progress bar value
        :param value: the value
        :return:
        """
        self.progress_bar.configure(value=value)

    def step(self, value: int = 1) -> None:
        """
        Set the progress bar by the value
        :param value: the step
        :return:
        """
        self.progress_bar.step(value)

    def set_determinate(self, value: bool) -> None:
        """
        Set the progress bar determinate value
        :param value: the value
        :return:
        """
        self.progress_bar.configure(mode="determinate" if value else "indeterminate")


# Combobox to select the pack
class SelectPack(ttk.Combobox):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master)

        self.mod_config: ModConfig | None = None
        self.packs: list[Path] = []

        self.refresh_packs()
        self.select(index=0)

        self.bind("<<ComboboxSelected>>", lambda _: self.select())

    def refresh_packs(self) -> None:
        """
        Refresh the list of packs
        :return:
        """
        self.packs = []

        for pack in Path("./Pack/").iterdir():
            if self.is_valid_pack(pack):
                self.packs.append(pack)

        self["values"] = [pack.name for pack in self.packs]

    def select(self, index: int = None) -> None:
        """
        When the selection is changed
        :index: the index of the selection. If none, use the selected index
        :return:
        """
        index = index if index is not None else self.current()
        pack = self.packs[index]
        self.set_path(pack)
        self.set(pack.name)

    @better_gui_error
    def set_path(self, pack: Path) -> None:
        """
        Set the pack to install
        :param pack: the pack
        :return:
        """
        self.mod_config = ModConfig.from_file(pack / "mod_config.json")

    @classmethod
    def is_valid_pack(cls, path: Path) -> bool:
        """
        Check if the path is a valid pack
        :param path: the path
        :return: True if the path is a valid pack
        """
        return all([
            (path / "mod_config.json").exists(),
        ])

    def set_state(self, state: InstallerState) -> None:
        """
        Set the progress bar state when the installer change state
        :param state: state of the installer
        :return:
        """
        match state:
            case InstallerState.IDLE: self.config(state="readonly")
            case InstallerState.INSTALLING: self.config(state="disabled")
