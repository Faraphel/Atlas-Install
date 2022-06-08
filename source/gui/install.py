import tkinter
from pathlib import Path
import json
from tkinter import ttk


from source.translation import translate as _
from source import event


# Main window for the installer
class Window(tkinter.Tk):
    @event.register
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

            master.add_cascade(label="Language", menu=self)

            for file in Path("./assets/language/").iterdir():
                self.add_command(label=json.loads(file.read_text(encoding="utf8"))["name"])

    # Track configuration menu
    class TrackConfiguration(tkinter.Menu):
        def __init__(self, master: tkinter.Menu):
            super().__init__(master, tearoff=False)

            master.add_cascade(label="Track Configuration", menu=self)
            self.add_command(label="Change configuration")

    # Advanced menu
    class Advanced(tkinter.Menu):
        def __init__(self, master: tkinter.Menu):
            super().__init__(master, tearoff=False)

            master.add_cascade(label="Advanced", menu=self)
            self.add_command(label="Debug mode")

    # Help menu
    class Help(tkinter.Menu):
        def __init__(self, master: tkinter.Menu):
            super().__init__(master, tearoff=False)

            master.add_cascade(label="Help", menu=self)
            self.add_command(label="Discord")
            self.add_command(label="Github Wiki")


# Select game frame
class SourceGame(ttk.LabelFrame):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master, text="Original Game")

        self.entry = ttk.Entry(self, width=50)
        self.entry.grid(row=1, column=1, sticky="nsew")

        ttk.Button(self, text="...", width=2).grid(row=1, column=2, sticky="nsew")


# Select game destination frame
class DestinationGame(ttk.LabelFrame):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master, text="Game Destination")

        self.entry = ttk.Entry(self, width=50)
        self.entry.grid(row=1, column=1, sticky="nsew")

        ttk.Button(self, text="...", width=2).grid(row=1, column=2, sticky="nsew")


# Install button
class ButtonInstall(ttk.Button):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master, text="Install", command=self.install)

    def install(self):
        ...


# Progress bar
class ProgressBar(ttk.Frame):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master)

        self.progress_bar = ttk.Progressbar(self)
        self.progress_bar.grid(row=1, column=1, sticky="nsew")

        self.description = tkinter.Label(self, text="test")
        self.description.grid(row=2, column=1, sticky="nsew")


# Combobox to select the pack
class SelectPack(ttk.Combobox):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master)

        for pack in Path("./Pack/").iterdir():
            self.insert(tkinter.END, pack.name)
