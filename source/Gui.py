from distutils.version import StrictVersion
from tkinter import filedialog, ttk, messagebox
from tkinter import *
import traceback
import requests
import zipfile
import json
import os

from source.Game import Game, RomAlreadyPatched, InvalidGamePath, InvalidFormat, in_thread, VERSION_FILE_URL
from source.Option import Option


with open("./translation.json", encoding="utf-8") as f:
    translation_dict = json.load(f)


class Gui:
    def __init__(self):
        """
        Initialize program Gui
        """
        self.root = Tk()

        self.option = Option()
        self.option.load_from_file("./option.json")
        self.game = Game(gui=self)
        self.game.ctconfig.load_ctconfig_file("./ct_config.json")

        self.is_dev_version = False  # Is this installer version a dev ?
        self.stringvar_language = StringVar(value=self.option.language)
        self.stringvar_game_format = StringVar(value=self.option.format)
        self.boolvar_disable_download = BooleanVar(value=self.option.disable_download)
        self.boolvar_del_track_after_conv = BooleanVar(value=self.option.del_track_after_conv)
        self.boolvar_dont_check_for_update = BooleanVar(value=self.option.dont_check_for_update)
        self.intvar_process_track = IntVar(value=self.option.process_track)
        self.boolvar_use_1star_track = BooleanVar(value=True)
        self.boolvar_use_2star_track = BooleanVar(value=True)
        self.boolvar_use_3star_track = BooleanVar(value=True)
        self.stringvar_mark_track_from_version = StringVar(value="None")
        self.stringvar_sort_track_by = StringVar(value="name")
        self.boolvar_use_debug_mode = BooleanVar(value=False)
        self.stringvar_mystuff_folder = StringVar(value=None)

        self.root.title(self.translate("MKWFaraphel Installer"))
        self.root.resizable(False, False)
        self.root.iconbitmap(bitmap="./icon.ico")

        if not(self.boolvar_dont_check_for_update.get()): self.check_update()

        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.menu_language = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.translate("Language"), menu=self.menu_language)
        self.menu_language.add_radiobutton(label="Français", variable=self.stringvar_language, value="fr", command=lambda: self.option.edit("language", "fr", need_restart=True))
        self.menu_language.add_radiobutton(label="English", variable=self.stringvar_language, value="en", command=lambda: self.option.edit("language", "en", need_restart=True))

        self.menu_format = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.translate("Format"), menu=self.menu_format)
        self.menu_format.add_radiobutton(label=self.translate("FST (Directory)"), variable=self.stringvar_game_format, value="FST", command=lambda: self.option.edit("format", "FST"))
        self.menu_format.add_radiobutton(label="ISO", variable=self.stringvar_game_format, value="ISO", command=lambda: self.option.edit("format", "ISO"))
        self.menu_format.add_radiobutton(label="CISO", variable=self.stringvar_game_format, value="CISO", command=lambda: self.option.edit("format", "CISO"))
        self.menu_format.add_radiobutton(label="WBFS", variable=self.stringvar_game_format, value="WBFS", command=lambda: self.option.edit("format", "WBFS"))

        self.menu_trackselection = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.translate("Track selection"), menu=self.menu_trackselection)
        self.menu_trackselection.add_checkbutton(label=self.translate("Select"," 1 ","star"), variable=self.boolvar_use_1star_track)
        self.menu_trackselection.add_checkbutton(label=self.translate("Select"," 2 ","stars"), variable=self.boolvar_use_2star_track)
        self.menu_trackselection.add_checkbutton(label=self.translate("Select"," 3 ","stars"), variable=self.boolvar_use_3star_track)
        self.menu_trackselection.add_separator()
        self.menu_marktrackversion = Menu(self.menu_trackselection, tearoff=0)
        self.menu_trackselection.add_cascade(label=self.translate("Mark all tracks from version"), menu=self.menu_marktrackversion)
        self.menu_marktrackversion.add_radiobutton(label=self.translate("None"), variable=self.stringvar_mark_track_from_version, value="None")
        for version in self.game.ctconfig.all_version:
            self.menu_marktrackversion.add_radiobutton(label=f"v{version}", variable=self.stringvar_mark_track_from_version, value=version)
        self.menu_sort_track_by = Menu(self.menu_trackselection, tearoff=0)
        self.menu_trackselection.add_cascade(label=self.translate("Sort track by"), menu=self.menu_sort_track_by)
        for param_name, param in [("Name", "name"), ("Version", "since_version"), ("Author", "author"), ("Score", "score"), ("Warning", "warning")]:
            self.menu_sort_track_by.add_radiobutton(label=param_name, variable=self.stringvar_sort_track_by, value=param)

        self.menu_advanced = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.translate("Advanced"), menu=self.menu_advanced)
        self.menu_advanced.add_checkbutton(label=self.translate("Disable downloads"), variable=self.boolvar_disable_download, command=lambda: self.option.edit("disable_download", self.boolvar_disable_download))
        self.menu_advanced.add_checkbutton(label=self.translate("Delete track after wu8 to szs conversion"), variable=self.boolvar_del_track_after_conv, command=lambda: self.option.edit("del_track_after_conv", self.boolvar_del_track_after_conv))
        self.menu_advanced.add_checkbutton(label=self.translate("Don't check for update"), variable=self.boolvar_dont_check_for_update, command=lambda: self.option.edit("dont_check_for_update", self.boolvar_dont_check_for_update))
        self.menu_advanced.add_checkbutton(label=self.translate("Use debug mode"), variable=self.boolvar_use_debug_mode)

        def select_mystuff_folder(index, init=False):
            self.stringvar_mystuff_folder.set(None)
            if not init:
                mystuff_dir = filedialog.askdirectory()
                if mystuff_dir: self.stringvar_mystuff_folder.set(mystuff_dir)
            self.menu_advanced.entryconfig(index, label=f"Apply MyStuff Folder ({self.stringvar_mystuff_folder.get()!r} selected)")

        self.menu_advanced.add_command(command=lambda index=self.menu_advanced.index("end")+1: select_mystuff_folder(index))
        select_mystuff_folder(self.menu_advanced.index("end"), init=True)

        self.menu_advanced.add_separator()
        self.menu_advanced.add_command(label=self.translate("Number of track conversion process", " :"))
        self.menu_advanced.add_radiobutton(label=self.translate("1 ", "process"), variable=self.intvar_process_track, value=1, command=lambda: self.option.edit("process_track", 1))
        self.menu_advanced.add_radiobutton(label=self.translate("2 ", "process"), variable=self.intvar_process_track, value=2, command=lambda: self.option.edit("process_track", 2))
        self.menu_advanced.add_radiobutton(label=self.translate("4 ", "process"), variable=self.intvar_process_track, value=4, command=lambda: self.option.edit("process_track", 4))
        self.menu_advanced.add_radiobutton(label=self.translate("8 ", "process"), variable=self.intvar_process_track, value=8, command=lambda: self.option.edit("process_track", 8))

        self.frame_language = Frame(self.root)
        self.frame_language.grid(row=1, column=1, sticky="E")

        self.frame_game_path = LabelFrame(self.root, text=self.translate("Original game"))
        self.frame_game_path.grid(row=2, column=1)

        entry_game_path = Entry(self.frame_game_path, width=50)
        entry_game_path.grid(row=1, column=1, sticky="NEWS")

        def select_path():
            path = filedialog.askopenfilename(filetypes=((self.translate("Wii game"),
                                                          r"*.iso *.wbfs main.dol *.wia *.ciso"),))
            if os.path.exists(path):
                entry_game_path.delete(0, END)
                entry_game_path.insert(0, path)

        Button(self.frame_game_path, text="...", relief=RIDGE, command=select_path).grid(row=1, column=2, sticky="NEWS")

        self.frame_game_path_action = Frame(self.frame_game_path)  # Extract and do everything button
        self.frame_game_path_action.grid(row=2, column=1, columnspan=2, sticky="NEWS")
        self.frame_game_path_action.columnconfigure(1, weight=1)

        @in_thread
        def use_path(): nothread_use_path()

        def nothread_use_path():
            self.frame_action.grid_forget()
            try:
                self.game.set_path(entry_game_path.get())
                self.progress(show=True, indeter=True, statut=self.translate("Extracting the game..."))
                self.game.extract()
                self.frame_action.grid(row=3, column=1, sticky="NEWS")
            except RomAlreadyPatched:
                messagebox.showerror(self.translate("Error"), self.translate("This game is already modded"))
                raise RomAlreadyPatched
            except InvalidGamePath:
                messagebox.showerror(self.translate("Error"), self.translate("The file path in invalid"))
                raise InvalidGamePath
            except InvalidFormat:
                messagebox.showerror(self.translate("Error"), self.translate("This game's format is invalid"))
                raise InvalidFormat
            except:
                self.log_error()
                raise Exception
            finally:
                self.progress(show=False)

        self.button_game_extract = Button(self.frame_game_path_action, text=self.translate("Extract file"),
                                          relief=RIDGE, command=use_path)
        self.button_game_extract.grid(row=1, column=1, sticky="NEWS")

        @in_thread
        def do_everything():
            nothread_use_path()
            self.game.nothread_patch_file()
            self.game.nothread_install_mod()

        self.button_do_everything = Button(self.frame_game_path_action, text=self.translate("Do everything"), relief=RIDGE, command=do_everything)
        self.button_do_everything.grid(row=1, column=2, sticky="NEWS")

        self.frame_action = LabelFrame(self.root, text=self.translate("Action"))

        self.button_prepare_file = Button(self.frame_action, text=self.translate("Prepare files"), relief=RIDGE, command=lambda: self.game.patch_file(), width=45)
        self.button_prepare_file.grid(row=1, column=1, columnspan=2, sticky="NEWS")
        self.button_install_mod = Button(self.frame_action, text=self.translate("Install mod"), relief=RIDGE, command=lambda: self.game.install_mod(), width=45)
        # Install mod button will only appear after prepare file step

        self.progressbar = ttk.Progressbar(self.root)
        self.progresslabel = Label(self.root)

    def check_update(self) -> None:
        """
        Check if an update is available
        """
        try:
            github_version_data = requests.get(VERSION_FILE_URL, allow_redirects=True).json()
            with open("./version", "rb") as f: local_version_data = json.load(f)

            local_version = StrictVersion(f"{local_version_data['version']}.{local_version_data['subversion']}")
            github_version = StrictVersion(f"{github_version_data['version']}.{github_version_data['subversion']}")

            if github_version > local_version: # if github version is newer than local version
                if messagebox.askyesno(
                        self.translate("Update available !"),
                        self.translate("An update is available, do you want to install it ?",
                                       f"\n\nVersion : {local_version} -> {github_version}\n"
                                       f"Changelog :\n{github_version_data['changelog']}")):

                    if not (os.path.exists("./Updater/Updater.exe")):
                        dl = requests.get(github_version_data["updater_bin"], allow_redirects=True)
                        with open("./download.zip", "wb") as file:
                            print(self.translate("Downloading the Updater..."))
                            file.write(dl.content)
                            print(self.translate("end of the download, extracting..."))

                        with zipfile.ZipFile("./download.zip") as file:
                            file.extractall("./Updater/")
                            print(self.translate("finished extracting"))

                        os.remove("./download.zip")
                        print(self.translate("starting application..."))
                        os.startfile(os.path.realpath("./Updater/Updater.exe"))

            elif local_version > github_version:
                self.is_dev_version = True

        except requests.ConnectionError:
            messagebox.showwarning(self.translate("Warning"),
                                   self.translate("Can't connect to internet. Download will be disabled."))
            self.option.disable_download = True

        except:
            self.log_error()

    def log_error(self) -> None:
        """
        When an error occur, will show it in a messagebox and write it in error.log
        """
        error = traceback.format_exc()
        with open("./error.log", "a") as f:
            f.write(f"---\n"
                    f"For game version : {self.game.ctconfig.version}\n"
                    f"./file/ directory : {os.listdir('./file/')}"
                    f"GAME/files/ information : {self.game.path, self.game.region}"
                    f"{error}\n")
        messagebox.showerror(self.translate("Error"), self.translate("An error occured", " :", "\n", error, "\n\n"))

    def progress(self, show: bool = None, indeter: bool = None, step: int = None,
                 statut: str = None, max: int = None, add: int = None) -> None:
        """
        configure the progress bar shown when doing a task
        :param show: show or hide the progress bar
        :param indeter: if indeter, the progress bar will do a infinite loop animation
        :param step: set the progress of the bar
        :param statut: text shown under the progress bar
        :param max: set the maximum step
        :param add: add to step of the progress bar
        """
        if indeter is True:
            self.progressbar.config(mode="indeterminate")
            self.progressbar.start(50)
        elif indeter is False:
            self.progressbar.config(mode="determinate")
            self.progressbar.stop()
        if show is True:
            self.state_button(enable=False)
            self.progressbar.grid(row=100, column=1, sticky="NEWS")
            self.progresslabel.grid(row=101, column=1, sticky="NEWS")
        elif show is False:
            self.state_button(enable=True)
            self.progressbar.grid_forget()
            self.progresslabel.grid_forget()

        if statut: self.progresslabel.config(text=statut)
        if step: self.progressbar["value"] = step
        if max:
            self.progressbar["maximum"] = max
            self.progressbar["value"] = 0
        if add: self.progressbar.step(add)

    def state_button(self, enable: bool = True) -> None:
        """
        used to enable or disable button when doing task
        :param enable: are the button enabled ?
        """
        button = [
            self.button_game_extract,
            self.button_install_mod,
            self.button_prepare_file,
            self.button_do_everything
        ]
        for widget in button:
            if enable:
                widget.config(state=NORMAL)
            else:
                widget.config(state=DISABLED)

    def translate(self, *texts, lang: str = None) -> str:
        """
        translate text into an another language in translation.json file
        :param texts: all text to convert
        :param lang: force a destination language to convert track
        :return: translated text
        """
        if lang is None: lang = self.stringvar_language.get()
        elif lang == "F": lang = "fr"
        elif lang == "G": lang = "ge"
        elif lang == "I": lang = "it"
        elif lang == "S": lang = "sp"

        if lang in translation_dict:
            _lang_trad = translation_dict[lang]
            translated_text = ""
            for text in texts:
                if text in _lang_trad:
                    translated_text += _lang_trad[text]
                else:
                    translated_text += text
            return translated_text

        return "".join(texts)  # if no translation language is found

    def is_using_official_config(self) -> bool:
        """
        :return: True if the parameter is the official one, False if it is customized
        """
        return (
            self.boolvar_use_1star_track.get() is True and
            self.boolvar_use_2star_track.get() is True and
            self.boolvar_use_3star_track.get() is True and
            self.stringvar_sort_track_by.get() == "name"
        )
