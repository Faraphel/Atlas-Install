import shutil
import tkinter
from pathlib import Path
import json
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import webbrowser

from source.translation import translate as _
from source import event
from source import *
import os


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
            self.add_command(label="Discord", command=lambda: webbrowser.open(discord_url))
            self.add_command(label="Github Wiki", command=lambda: webbrowser.open(github_wiki_url))


# Select game frame
class SourceGame(ttk.LabelFrame):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master, text="Original Game")

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

        self.master.destination_game.set_path(path.parent / "MKWF.iso")


# Select game destination frame
class DestinationGame(ttk.LabelFrame):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master, text="Game Destination")

        self.entry = ttk.Entry(self, width=50)
        self.entry.grid(row=1, column=1, sticky="nsew")

        self.button = ttk.Button(self, text="...", width=2, command=self.select)
        self.button.grid(row=1, column=2, sticky="nsew")

    def select(self) -> None:
        """
        Select the source game
        :return:
        """
        path = Path(tkinter.filedialog.asksaveasfilename(
            title=_("SELECT_DESTINATION_GAME"),
            filetypes=[(_("WII GAMES"), "*.iso *.wbfs *.dol")],
        ))

        path.parent.mkdir(mode=0o777, parents=True, exist_ok=True)

        self.set_path(path)

    def set_path(self, path: Path):
        if not os.access(path.parent, os.W_OK):
            messagebox.showwarning(_("WARNING"), _("WARNING_DESTINATION_GAME_NOT_WRITABLE"))

        self.entry.delete(0, tkinter.END)
        self.entry.insert(0, str(path.absolute()))


# Install button
class ButtonInstall(ttk.Button):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master, text="Install", command=self.install)

    def install(self):
        # get space remaining on the C: drive
        if shutil.disk_usage(".").free < minimum_space_available:
            if not messagebox.askokcancel(_("WARNING"), _("WARNING_NOT_ENOUGH_SPACE_CONTINUE")): return


# Progress bar
class ProgressBar(ttk.LabelFrame):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master)

        # make the element fill the whole frame
        self.columnconfigure(1, weight=1)

        self.progress_bar = ttk.Progressbar(self, orient="horizontal")
        self.progress_bar.grid(row=1, column=1, sticky="nsew")

        self.description = ttk.Label(self, text="no process running", anchor="center", font=("TkDefaultFont", 10))
        self.description.grid(row=2, column=1, sticky="nsew")


# Combobox to select the pack
class SelectPack(ttk.Combobox):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master)

        for pack in Path("./Pack/").iterdir():
            self.insert(tkinter.END, pack.name)
