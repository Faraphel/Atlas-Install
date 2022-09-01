import enum
import shutil
from pathlib import Path
import json
import tkinter
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import webbrowser
from typing import Generator

from source.gui import better_gui_error, mystuff, mod_settings
from source.mkw.Game import Game
from source.mkw.ModConfig import ModConfig
from source.option import Options
from source.progress import Progress
from source.translation import translate as _, translate_external
from source import plugins
from source import *
from source.utils import threaded
import os

from source.mkw.collection.Extension import Extension


class InstallerState(enum.Enum):
    IDLE = 0
    INSTALLING = 1


# Main window for the installer
class Window(tkinter.Tk):
    def __init__(self, options: Options):
        super().__init__()
        self.root = self

        self.mod_config: ModConfig | None = None
        self.options: Options = options

        self.source_path = tkinter.StringVar()
        self.destination_path = tkinter.StringVar()

        self.title(_("TITLE_INSTALL"))
        self.resizable(False, False)

        self.icon = tkinter.PhotoImage(file="./assets/icon.png")
        self.iconphoto(True, self.icon)

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
        plugins.initialise()
        self.after(0, self.run_after)
        self.mainloop()

    @staticmethod
    def run_after() -> None:
        """
        Run after the installer has been initialised, can be used to add plugins
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

    def progress_function(self, func_gen: Generator[Progress, None, None]) -> None:
        """
        Run a generator function that yield status for the progress bar
        """
        # get the generator data yield by the generator function
        for progress in func_gen:
            if progress.title is not None: self.progress_bar.set_title(progress.title)
            if progress.part is not None: self.progress_bar.part(progress.part)
            if progress.set_part is not None: self.progress_bar.set_part(progress.set_part)
            if progress.max_part is not None: self.progress_bar.set_max_part(progress.max_part)

            if progress.description is not None: self.progress_bar.set_description(progress.description)
            if progress.step is not None: self.progress_bar.step(progress.step)
            if progress.set_step is not None: self.progress_bar.set_step(progress.set_step)
            if progress.max_step is not None: self.progress_bar.set_max_step(progress.max_step)
            if progress.determinate is not None: self.progress_bar.set_determinate(progress.determinate)


# Menu bar
class Menu(tkinter.Menu):
    def __init__(self, master):
        super().__init__(master)
        self.root = master.root

        self.language = self.Language(self)
        self.advanced = self.Advanced(self)
        self.help = self.Help(self)

    # Language menu
    class Language(tkinter.Menu):
        def __init__(self, master: tkinter.Menu):
            super().__init__(master, tearoff=False)
            self.root = master.root
        
            master.add_cascade(label=_("MENU_LANGUAGE_SELECTION"), menu=self)

            self.lang_variable = tkinter.StringVar(value=self.root.options.language.get())

            for file in Path("./assets/language/").iterdir():
                lang_json = json.loads(file.read_text(encoding="utf8"))
                self.add_radiobutton(
                    label=lang_json["name"],
                    value=file.stem,
                    variable=self.lang_variable,
                    command=(lambda value: (lambda: self.root.options.language.set(value)))(file.stem),
                )

    # Advanced menu
    class Advanced(tkinter.Menu):
        def __init__(self, master: tkinter.Menu):
            super().__init__(master, tearoff=False)
            self.root = master.root

            master.add_cascade(label=_("MENU_ADVANCED"), menu=self)
            self.add_command(
                label=_("MENU_ADVANCED_MYSTUFF"),
                command=lambda: mystuff.Window(self.root.mod_config, self.root.options)
            )
            self.threads_used = self.ThreadsUsed(self)
            self.add_command(label=_("MENU_ADVANCED_EMPTY_CACHE"), command=self.empty_cache)

            self.add_separator()

            self.variable_developer_mode = tkinter.BooleanVar(value=self.root.options.developer_mode.get())
            self.add_checkbutton(
                label=_("MENU_ADVANCED_DEVELOPER_MODE"),
                variable=self.variable_developer_mode,
                command=lambda: self.root.options.developer_mode.set(self.variable_developer_mode.get())
            )

        @staticmethod
        def empty_cache():
            cache_path: Path = Path("./.cache/")
            cache_size: int = sum(file.stat().st_size / Go for file in cache_path.rglob("*"))

            if messagebox.askokcancel(_("WARNING"), _("WARNING_EMPTY_CACHE") % cache_size):
                shutil.rmtree("./.cache/", ignore_errors=True)

        class ThreadsUsed(tkinter.Menu):
            def __init__(self, master: tkinter.Menu):
                super().__init__(master, tearoff=False)
                self.root = master.root

                master.add_cascade(label=_("MENU_ADVANCED_THREADS"), menu=self)

                self.variable = tkinter.IntVar(value=self.root.options.threads.get())

                for i in [1, 2, 4, 8, 12, 16]:
                    self.add_radiobutton(
                        label=_("MENU_ADVANCED_THREADS_SELECTION") % i,
                        value=i,
                        variable=self.variable,
                        command=(lambda amount: (lambda: self.root.options.threads.set(amount)))(i),
                    )

    # Help menu
    class Help(tkinter.Menu):
        def __init__(self, master: tkinter.Menu):
            super().__init__(master, tearoff=False)
            self.root = master.root

            master.add_cascade(label=_("MENU_HELP"), menu=self)
            self.menu_id = self.master.index(tkinter.END)

            self.add_command(label="Discord", command=lambda: webbrowser.open(discord_url))
            self.add_command(label="GitHub", command=lambda: webbrowser.open(github_wiki_url))
            self.add_command(label="ReadTheDocs", command=lambda: webbrowser.open(readthedocs_url))

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
        super().__init__(master, text=_("TEXT_SOURCE_GAME"))
        self.root = master.root
        
        self.columnconfigure(1, weight=1)

        self.entry = ttk.Entry(self, width=55, textvariable=self.root.source_path)
        self.entry.grid(row=1, column=1, sticky="nsew")

        self.button = ttk.Button(self, text="...", width=2, command=self.select)
        self.button.grid(row=1, column=2, sticky="nsew")

    def select(self) -> None:
        """
        Select the source game
        :return:
        """
        raw_path = tkinter.filedialog.askopenfilename(
            title=_("TEXT_SELECT_SOURCE_GAME"),
            filetypes=[(_("TEXT_WII_GAMES"), "*.iso *.ciso *.wbfs *.dol")],
        )

        # if the user didn't select any file, return None
        if raw_path == "": return
        path = Path(raw_path)

        # if the user didn't select a correct file, return None
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

        # if the selected path is an extracted game, use 2 directory upper
        if path.suffix == ".dol": path = path.parent.parent

        self.root.destination_game.set_path(path.parent)

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
        super().__init__(master, text=_("TEXT_GAME_DESTINATION"))
        self.root = master.root
        
        self.columnconfigure(1, weight=1)

        self.entry = ttk.Entry(self, textvariable=self.root.destination_path)
        self.entry.grid(row=1, column=1, sticky="nsew")

        self.output_type = ttk.Combobox(self, width=5, values=[extension.name for extension in Extension])
        self.output_type.bind("<<ComboboxSelected>>", lambda _: self.root.options.extension.set(self.output_type.get()))
        self.output_type.set(self.root.options.extension.get())
        self.output_type.grid(row=1, column=2, sticky="nsew")

        self.button = ttk.Button(self, text="...", width=2, command=self.select)
        self.button.grid(row=1, column=3, sticky="nsew")

    def select(self) -> None:
        """
        Select the source game
        :return:
        """
        raw_path = tkinter.filedialog.askdirectory(
            title=_("TEXT_SELECT_GAME_DESTINATION"),
        )

        # if the user didn't select any directory, return None
        if raw_path == "": return
        path = Path(raw_path)

        path.mkdir(mode=0o777, parents=True, exist_ok=True)

        self.set_path(path)

    def set_path(self, path: Path):
        if not os.access(path, os.W_OK):
            messagebox.showwarning(_("WARNING"), _("WARNING_DESTINATION_NOT_WRITABLE"))

        self.entry.delete(0, tkinter.END)
        self.entry.insert(0, str(path.absolute()))

    def set_state(self, state: InstallerState) -> None:
        """
        Set the progress bar state when the installer change state
        :param state: state of the installer
        :return:
        """
        for child in self.winfo_children():
            match state:
                case InstallerState.IDLE:
                    if child == self.output_type: child.config(state="readonly")
                    else: child.config(state="normal")
                case InstallerState.INSTALLING: child.config(state="disabled")


# Install button
class ButtonInstall(ttk.Button):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master, text=_("TEXT_INSTALL"), command=self.install)
        self.root = master.root

    @threaded
    @better_gui_error
    def install(self):
        try:
            self.root.set_state(InstallerState.INSTALLING)

            # check if the user entered a source path. If the string is ".", then the user didn't input any path
            source_path = Path(self.root.source_path.get())
            if not source_path.exists() or str(source_path) == ".":
                messagebox.showerror(_("ERROR"), _("ERROR_INVALID_SOURCE_GAME") % source_path)
                return

            # check if the user entered a destination path. If the string is ".", then the user didn't input any path
            destination_path = Path(self.root.destination_path.get())
            if not destination_path.exists() or str(destination_path) == ".":
                messagebox.showerror(_("ERROR"), _("ERROR_INVALID_GAME_DESTINATION") % source_path)
                return

            available_space_local = shutil.disk_usage(".").free
            available_space_destination = shutil.disk_usage(destination_path).free

            # if there is no more space on the installer drive, show a warning
            if available_space_local < minimum_space_available:
                if not messagebox.askokcancel(
                    _("WARNING"),
                    _("WARNING_LOW_SPACE_CONTINUE") % (Path(".").resolve().drive, available_space_local/Go)
                ):
                    return

            # if there is no more space on the destination drive, show a warning
            elif available_space_destination < minimum_space_available:
                if not messagebox.askokcancel(
                    _("WARNING"),
                    _("WARNING_LOW_SPACE_CONTINUE") % (destination_path.resolve().drive, available_space_destination/Go)
                ): return

            if system == "lin64":  # if linux
                if os.getuid() != 0:  # if the user is not root
                    if not messagebox.askokcancel(_("WARNING"), _("WARNING_NOT_ROOT")):
                        return

                if not os.access("./", os.W_OK | os.X_OK):
                    # check if writing (for the /.cache/) and execution (for /tools/) are allowed
                    if not messagebox.askokcancel(_("WARNING"), _("WARNING_INSTALLER_PERMISSION")):
                        return

            game = Game(source_path)
            output_type = Extension[self.root.options.extension.get()]

            self.root.progress_function(
                game.install_mod(
                    dest=destination_path,
                    mod_config=self.root.mod_config,
                    output_type=output_type,
                    options=self.root.options
                )
            )

            message: str = translate_external(
                self.root.mod_config,
                self.root.options.language.get(),
                self.root.mod_config.messages.get("installation_completed", {}).get("text", {})
            )

            messagebox.showinfo(
                _("TEXT_INSTALLATION_COMPLETED"),
                f"{_('TEXT_INSTALLATION_FINISHED_SUCCESSFULLY')}" + (
                    f"\n{_('TEXT_MESSAGE_FROM_AUTHOR')} :\n\n{message}" if message != "" else ""
                )
            )

        finally:
            self.root.set_state(InstallerState.IDLE)

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
        self.root = master.root

        # make the element fill the whole frame
        self.columnconfigure(1, weight=1)

        self.progress_bar_part = ttk.Progressbar(self, orient="horizontal")
        self.progress_bar_part.grid(row=1, column=1, sticky="nsew")

        self.title = ttk.Label(self, text="", anchor=tkinter.CENTER, justify=tkinter.CENTER,
                               font=("TkDefaultFont", 10), wraplength=350)
        self.title.grid(row=2, column=1, sticky="nsew")

        self.progress_bar_step = ttk.Progressbar(self, orient="horizontal")
        self.progress_bar_step.grid(row=3, column=1, sticky="nsew")

        self.description = ttk.Label(self, text="", anchor=tkinter.CENTER, justify=tkinter.CENTER,
                                     font=("TkDefaultFont", 10), wraplength=350)
        self.description.grid(row=4, column=1, sticky="nsew")

    def set_state(self, state: InstallerState) -> None:
        """
        Set the progress bar state when the installer change state
        :param state: state of the installer
        :return:
        """
        match state:
            case InstallerState.IDLE: self.grid_remove()
            case InstallerState.INSTALLING: self.grid()

    def set_title(self, title: str): self.title.config(text=title)
    def set_max_part(self, maximum: int): self.progress_bar_part.configure(maximum=maximum)
    def set_part(self, value: int): self.progress_bar_part.configure(value=value)
    def part(self, value: int = 1): self.progress_bar_part.step(value)

    def set_description(self, desc: str) -> None: self.description.config(text=desc)
    def set_max_step(self, maximum: int) -> None: self.progress_bar_step.configure(maximum=maximum)
    def set_step(self, value: int) -> None: self.progress_bar_step.configure(value=value)
    def step(self, value: int = 1) -> None: self.progress_bar_step.step(value)

    def set_determinate(self, value: bool) -> None:
        """
        Set the progress bar determinate value
        :param value: the value
        :return:
        """

        if value:
            self.progress_bar_step.configure(mode="determinate")
            self.progress_bar_step.stop()

        else:
            self.progress_bar_step.configure(mode="indeterminate", maximum=100)
            self.progress_bar_step.start(50)

        self.progress_bar_step.update()


# Combobox to select the pack
class SelectPack(ttk.Frame):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master)
        self.root = master.root

        self.combobox = ttk.Combobox(self)
        self.combobox.grid(row=1, column=1, sticky="NEWS")

        self.button_settings = ttk.Button(self, text="...", width=2, command=self.open_mod_configuration)
        self.button_settings.grid(row=1, column=2, sticky="NEWS")

        self.packs: list[Path] = []

        self.refresh_packs()
        self.select(index=0)

        self.combobox.bind("<<ComboboxSelected>>", lambda _: self.select())

    def open_mod_configuration(self) -> None:
        mod_settings.Window(self.root.mod_config, self.root.options)

    def refresh_packs(self) -> None:
        """
        Refresh the list of packs
        :return:
        """
        self.packs = []

        for pack in Path("./Pack/").iterdir():
            if self.is_valid_pack(pack):
                self.packs.append(pack)

        self.combobox["values"] = [pack.name for pack in self.packs]

    def select(self, index: int = None) -> None:
        """
        When the selection is changed
        :index: the index of the selection. If none, use the selected index
        :return:
        """
        index = index if index is not None else self.combobox.current()
        pack = self.packs[index]
        self.set_path(pack)
        self.combobox.set(pack.name)

    @better_gui_error
    def set_path(self, pack: Path) -> None:
        """
        Set the pack to install
        :param pack: the pack
        :return:
        """
        self.root.mod_config = ModConfig.from_file(pack / "mod_config.json")

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
            case InstallerState.IDLE:
                self.combobox.config(state="readonly")
                self.button_settings.config(state="normal")
            case InstallerState.INSTALLING:
                self.combobox.config(state="disabled")
                self.button_settings.config(state="disabled")
