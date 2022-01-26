from distutils.version import StrictVersion
from tkinter import filedialog, ttk, messagebox
from tkinter import *
import webbrowser
import traceback
import requests
import zipfile
import glob
import json

from source.Error import *
from source.definition import *


class Main:
    def __init__(self, common) -> None:
        """
        Initialize program Gui
        """
        self.root = Tk()
        self.root.resizable(False, False)
        self.root.iconbitmap(bitmap="./icon.ico")

        self.common = common
        self.menu_bar = None

        self.available_packs = self.get_available_packs()
        if not self.available_packs:
            messagebox.showerror(
                self.common.translate("Error"),
                self.common.translate("There is no pack in the ./Pack/ directory.")
            )
            self.quit()

        self.is_dev_version = False  # Is this installer version a dev ?
        self.is_track_configuration_edited = False
        self.stringvar_ctconfig = StringVar(value=self.available_packs[0])
        self.stringvar_language = StringVar(value=self.common.option.language)
        self.stringvar_game_format = StringVar(value=self.common.option.format)
        self.boolvar_dont_check_for_update = BooleanVar(value=self.common.option.dont_check_for_update)
        self.intvar_process_track = IntVar(value=self.common.option.process_track)

        self.root.title(self.common.translate("MKWFaraphel Installer"))

        self.boolvar_use_debug_mode = BooleanVar(value=False)
        self.boolvar_force_unofficial_mode = BooleanVar(value=False)

        self.stringvar_mystuff_folder = StringVar(value=None)

        if not self.boolvar_dont_check_for_update.get(): self.check_update()

        # GUI
        # Mod selector
        self.frame_ctconfig = LabelFrame(self.root, text=self.common.translate("Mod"))
        self.frame_ctconfig.grid(row=1, column=1, sticky="NWS")

        self.combobox_ctconfig_path = ttk.Combobox(
            self.frame_ctconfig,
            values=self.available_packs,
            textvariable=self.stringvar_ctconfig,
            width=30
        )
        self.combobox_ctconfig_path.grid(row=1, column=1, sticky="NEWS", columnspan=2)
        self.combobox_ctconfig_path.bind("<<ComboboxSelected>>", lambda x=None: self.reload_ctconfig())
        self.reload_ctconfig()

        # Jeu
        self.frame_game_path = LabelFrame(self.root, text=self.common.translate("Original game"))
        self.frame_game_path.grid(row=2, column=1)

        entry_game_path = Entry(self.frame_game_path, width=50)
        entry_game_path.grid(row=1, column=1, sticky="NEWS")

        def select_path():
            path = filedialog.askopenfilename(
                filetypes=((self.common.translate("Wii game"), r"*.iso *.wbfs main.dol *.wia *.ciso"),)
            )
            if os.path.exists(path):
                entry_game_path.delete(0, END)
                entry_game_path.insert(0, path)

        self.button_select_path = Button(self.frame_game_path, text="...", relief=RIDGE, command=select_path)
        self.button_select_path.grid(row=1, column=2, sticky="NEWS")

        self.frame_game_path_action = Frame(self.frame_game_path)  # Extract and do everything button
        self.frame_game_path_action.grid(row=2, column=1, columnspan=2, sticky="NEWS")
        self.frame_game_path_action.columnconfigure(1, weight=1)

        def use_path():
            try:
                game_path = entry_game_path.get()
                if not os.path.exists(game_path): raise InvalidGamePath

                self.common.game.set_path(game_path)
                self.progress(show=True, indeter=True, statut=self.common.translate("Extracting the game..."))
                self.common.game.extract()

            except RomAlreadyPatched:
                messagebox.showerror(self.common.translate("Error"), self.common.translate("This game is already modded"))
                raise RomAlreadyPatched
            except InvalidGamePath:
                messagebox.showerror(self.common.translate("Error"), self.common.translate("The file path in invalid"))
                raise InvalidGamePath
            except InvalidFormat:
                messagebox.showerror(self.common.translate("Error"), self.common.translate("This game's format is invalid"))
                raise InvalidFormat
            except Exception as e:
                self.log_error()
                raise e
            finally:
                self.progress(show=False)

        @in_thread
        def do_everything():
            use_path()
            self.common.game.patch_file()
            self.common.game.install_mod()

        self.button_do_everything = Button(
            self.frame_game_path_action,
            text=self.common.translate("Install mod"),
            relief=RIDGE,
            command=do_everything
        )
        self.button_do_everything.grid(row=1, column=1, columnspan=2, sticky="NEWS")

        self.progressbar = ttk.Progressbar(self.root)
        self.progresslabel = Label(self.root)


        if self.menu_bar: self.menu_bar.destroy()
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        #  LANGUAGE MENU
        self.menu_language = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.common.translate("Language"), menu=self.menu_language)
        self.menu_language.add_radiobutton(
            label="Français",
            variable=self.stringvar_language,
            value="fr",
            command=lambda: self.common.option.edit("language", "fr", need_restart=True)
        )
        self.menu_language.add_radiobutton(
            label="English",
            variable=self.stringvar_language,
            value="en",
            command=lambda: self.common.option.edit("language", "en", need_restart=True)
        )

        #  OUTPUT FORMAT MENU
        self.menu_format = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.common.translate("Format"), menu=self.menu_format)
        self.menu_format.add_radiobutton(
            label=self.common.translate("FST (Directory)"),
            variable=self.stringvar_game_format,
            value="FST", command=lambda:
            self.common.option.edit("format", "FST")
        )
        self.menu_format.add_radiobutton(
            label="ISO",
            variable=self.stringvar_game_format,
            value="ISO",
            command=lambda: self.common.option.edit("format", "ISO")
        )
        self.menu_format.add_radiobutton(
            label="CISO",
            variable=self.stringvar_game_format,
            value="CISO",
            command=lambda: self.common.option.edit("format", "CISO")
        )
        self.menu_format.add_radiobutton(
            label="WBFS",
            variable=self.stringvar_game_format,
            value="WBFS",
            command=lambda: self.common.option.edit("format", "WBFS")
        )

        #  ADVANCED MENU
        ## INSTALLER PARAMETER
        self.menu_advanced = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.common.translate("Advanced"), menu=self.menu_advanced)
        self.menu_advanced.add_checkbutton(
            label=self.common.translate("Don't check for update"),
            variable=self.boolvar_dont_check_for_update,
            command=lambda: self.common.option.edit(
                "dont_check_for_update",
                self.boolvar_dont_check_for_update
            )
        )
        self.menu_advanced.add_checkbutton(
            label=self.common.translate("Force \"unofficial\" mode"),
            variable=self.boolvar_force_unofficial_mode
        )

        self.menu_conv_process = Menu(self.menu_advanced, tearoff=0)
        self.menu_advanced.add_cascade(
            label=self.common.translate("Number of track conversion process"),
            menu=self.menu_conv_process
        )

        for process_number in range(1, 8+1):
            self.menu_conv_process.add_radiobutton(
                label=self.common.translate(f"{process_number} ", "process"),
                variable=self.intvar_process_track, value=process_number,
                command=lambda p=process_number: self.common.option.edit("process_track", p)
            )

        ## GAME PARAMETER
        self.menu_advanced.add_separator()

        self.menu_advanced.add_command(
            label=self.common.translate("Change track configuration"),
            command=self.common.show_gui_track_configuration
        )

        self.menu_advanced.add_checkbutton(
            label=self.common.translate("Use debug mode"),
            variable=self.boolvar_use_debug_mode
        )

        self.menu_mystuff = Menu(self.menu_advanced, tearoff=0)
        self.menu_advanced.add_cascade(label=self.common.translate("MyStuff"), menu=self.menu_mystuff)

        def add_menu_mystuff_command(stringvar: StringVar, label: str):
            self.menu_mystuff.add_command()
            index: int = self.menu_mystuff.index("end")

            def _func(init: bool = False):
                stringvar.set(None)
                if not init:
                    mystuff_dir = filedialog.askdirectory()
                    if mystuff_dir: stringvar.set(mystuff_dir)

                self.menu_mystuff.entryconfig(index, label=self.common.translate(
                    "Apply", " ", label, f" ({stringvar.get()!r} ", "selected", ")")
                                              )

            _func(init=True)
            self.menu_mystuff.entryconfig(index, command=_func)

            return _func

        add_menu_mystuff_command(self.stringvar_mystuff_folder, "MyStuff")

        #  HELP MENU
        self.menu_help = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.common.translate("Help"), menu=self.menu_help)
        self.menu_help.add_command(label="Github Wiki", command=lambda: webbrowser.open(GITHUB_HELP_PAGE_URL))
        self.menu_help.add_command(label="Discord", command=lambda: webbrowser.open(DISCORD_URL))

    def reload_ctconfig(self) -> None:
        self.common.ct_config.load_ctconfig_file(
            ctconfig_file=self.get_ctconfig_path_pack(self.stringvar_ctconfig.get())
        )

    def get_available_packs(self) -> list:
        available_packs = []

        for pack_ctconfig in glob.glob("./Pack/*/ct_config.json"):
            dirname = os.path.basename(os.path.dirname(pack_ctconfig))
            available_packs.append(dirname)

        return available_packs

    def get_ctconfig_path_pack(self, pack_name: str) -> str:
        return "./Pack/" + pack_name + "/ct_config.json"

    def check_update(self) -> None:
        """
        Check if an update is available
        """
        try:
            github_version_data = requests.get(VERSION_FILE_URL, allow_redirects=True, timeout=3).json()
            with open("./version", "rb") as f: local_version_data = json.load(f)

            local_version = StrictVersion(f"{local_version_data['version']}.{local_version_data['subversion']}")
            github_version = StrictVersion(f"{github_version_data['version']}.{github_version_data['subversion']}")

            if github_version > local_version:  # if github version is newer than local version
                if messagebox.askyesno(
                        self.common.translate("Update available !"),
                        self.common.translate("An update is available, do you want to install it ?",
                                       f"\n\nVersion : {local_version} -> {github_version}\n"
                                       f"Changelog :\n{github_version_data['changelog']}")):

                    if not (os.path.exists("./Updater/Updater.exe")):
                        dl = requests.get(github_version_data["updater_bin"], allow_redirects=True)
                        with open("./download.zip", "wb") as file:
                            print(self.common.translate("Downloading the Updater..."))
                            file.write(dl.content)
                            print(self.common.translate("end of the download, extracting..."))

                        with zipfile.ZipFile("./download.zip") as file:
                            file.extractall("./Updater/")
                            print(self.common.translate("finished extracting"))

                        os.remove("./download.zip")

                    print(self.common.translate("starting application..."))
                    os.startfile(os.path.realpath("./Updater/Updater.exe"))

            elif local_version > github_version:
                self.is_dev_version = True

        except requests.ConnectionError:
            messagebox.showwarning(self.common.translate("Warning"),
                                   self.common.translate("Can't connect to internet. Download will be disabled."))
            self.common.option.disable_download = True

        except:
            self.log_error()

    def log_error(self) -> None:
        """
        When an error occur, will show it in a messagebox and write it in error.log
        """
        error = traceback.format_exc()
        with open("./error.log", "a") as f:
            f.write(
                f"---\n"
                f"For game version : {self.common.ct_config.version}\n"
                f"./file/ directory : {os.listdir('./file/')}\n"
                f"ctconfig directory : {os.listdir(self.common.ct_config.pack_path)}\n"
                f"GAME/files/ information : {self.common.game.path, self.common.game.region}\n"
                f"{error}\n"
            )
        messagebox.showerror(
            self.common.translate("Error"),
            self.common.translate("An error occured", " :", "\n", error, "\n\n")
        )

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
            self.button_do_everything,
            self.button_select_path,
            self.combobox_ctconfig_path,
        ]
        for widget in button:
            if enable: widget.config(state=NORMAL)
            else: widget.config(state=DISABLED)

    def is_using_official_config(self) -> bool:
        """
        :return: True if the parameter is the official one, False if it is customized
        """
        return (
            self.boolvar_force_unofficial_mode.get() is False and
            self.is_track_configuration_edited is False
        )

    def quit(self) -> None:
        self.root.quit()
        self.root.destroy()
        sys.exit()

    def mainloop(self) -> None:
        self.root.mainloop()