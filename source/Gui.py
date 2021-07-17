from tkinter import *
from tkinter import messagebox, filedialog, ttk
from threading import Thread
import subprocess
import traceback
import glob
import os

from .definition import *
from .CT_Config import *
from .Option import *
from .Game import *


with open("./translation.json", encoding="utf-8") as f:
    translation_dict = json.load(f)


def restart():
    subprocess.Popen([sys.executable] + sys.argv, creationflags=CREATE_NO_WINDOW, cwd=os.getcwd())
    exit()


class Gui():
    def __init__(self):
        self.root = Tk()

        self.option = Option()
        self.option.load_from_file("./option.json")
        self.ctconfig = CT_Config()
        self.ctconfig.load_ctconfig_file("./ct_config.json")

        self.is_dev_version = False  # Is this installer version a dev ?
        self.stringvar_language = StringVar(value=self.option.language)
        self.stringvar_game_format = StringVar(value=self.option.format)
        self.boolvar_disable_download = BooleanVar(value=self.option.disable_download)
        self.boolvar_del_track_after_conv = BooleanVar(value=self.option.del_track_after_conv)
        self.boolvar_dont_check_for_update = BooleanVar(value=self.option.dont_check_for_update)
        self.boolvar_dont_check_track_sha1 = BooleanVar(value=self.option.dont_check_track_sha1)
        self.intvar_process_track = IntVar(value=self.option.process_track)
        self.boolvar_use_1star_track = BooleanVar(value=True)
        self.boolvar_use_2star_track = BooleanVar(value=True)
        self.boolvar_use_3star_track = BooleanVar(value=True)
        self.stringvar_mark_track_from_version = StringVar(value="None")

        self.root.title(self.translate("MKWFaraphel Installer"))
        self.root.resizable(False, False)
        self.root.iconbitmap(bitmap="./icon.ico")

        if not(self.boolvar_dont_check_for_update.get()): self.check_update()

        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.menu_language = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.translate("Language"), menu=self.menu_language)
        self.menu_language.add_radiobutton(label="Français", variable=self.stringvar_language, value="fr", command=lambda: self.option.edit("language", "fr", restart=True))
        self.menu_language.add_radiobutton(label="English", variable=self.stringvar_language, value="en", command=lambda: self.option.edit("language", "en", restart=True))

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
        for version in self.ctconfig.all_version:
            self.menu_marktrackversion.add_radiobutton(label=f"v{version}", variable=self.stringvar_mark_track_from_version, value=version)

        self.menu_advanced = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.translate("Advanced"), menu=self.menu_advanced)
        self.menu_advanced.add_checkbutton(label=self.translate("Disable downloads"), variable=self.boolvar_disable_download, command=lambda: self.option.edit("disable_download", self.boolvar_disable_download))
        self.menu_advanced.add_checkbutton(label=self.translate("Delete track after wu8 to szs conversion"), variable=self.boolvar_del_track_after_conv, command=lambda: self.option.edit("del_track_after_conv", self.boolvar_del_track_after_conv))
        self.menu_advanced.add_checkbutton(label=self.translate("Don't check for update"), variable=self.boolvar_dont_check_for_update, command=lambda: self.option.edit("dont_check_for_update", self.boolvar_dont_check_for_update))
        self.menu_advanced.add_checkbutton(label=self.translate("Don't check track's sha1"), variable=self.boolvar_dont_check_track_sha1, command=lambda: self.option.edit("dont_check_track_sha1",self.boolvar_dont_check_track_sha1))

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

        def use_path():
            def func():
                self.frame_action.grid_forget()
                try:
                    self.game = Game(path = entry_game_path.get())
                    self.progress(show=True, indeter=True, statut=self.translate("Extracting the game..."))
                    self.game.extract_game()
                    self.frame_action.grid(row=3, column=1, sticky="NEWS")
                except InvalidGamePath:
                    messagebox.showerror(self.translate("Error"), self.translate("The file path in invalid"))
                except InvalidFormat:
                    messagebox.showerror(self.translate("Error"), self.translate("This game's format is invalid"))
                except:
                    self.log_error()
                finally:
                    self.progress(show=False)

            t = Thread(target=func)
            t.setDaemon(True)
            t.start()
            return t

        self.button_game_extract = Button(self.frame_game_path_action, text=self.translate("Extract file"),
                                          relief=RIDGE, command=use_path)
        self.button_game_extract.grid(row=1, column=1, sticky="NEWS")

        def do_everything():
            def func():
                use_path().join()
                self.game.patch_file(gui).join()
                self.game.install_mod(self).join()

            if messagebox.askyesno(self.translate("Experimental functionality"),
                self.translate("This will extract the selected ROM, prepare files and install mod. "
                               "Do you wish to continue ?")):
                t = Thread(target=func)
                t.setDaemon(True)
                t.start()

        self.button_do_everything = Button(self.frame_game_path_action, text=self.translate("Do everything"), relief=RIDGE, command=do_everything)
        self.button_do_everything.grid(row=1, column=2, sticky="NEWS")


        self.frame_action = LabelFrame(self.root, text=self.translate("Action"))

        self.button_prepare_file = Button(self.frame_action, text=self.translate("Prepare files"), relief=RIDGE, command=lambda: self.game.patch_file(self), width=45)
        self.button_prepare_file.grid(row=1, column=1, columnspan=2, sticky="NEWS")
        self.button_install_mod = Button(self.frame_action, text=self.translate("Install mod"), relief=RIDGE, command=lambda: self.game.install_mod(self), width=45)
        # Install mod button will only appear after prepare file step

        self.progressbar = ttk.Progressbar(self.root)
        self.progresslabel = Label(self.root)


    def check_update(self):
        try:
            gitversion = requests.get(VERSION_FILE_URL, allow_redirects=True).json()
            with open("./version", "rb") as f:
                locversion = json.load(f)

            if ((float(gitversion["version"]) > float(locversion["version"])) or  # if github version is newer than
                    (float(gitversion["version"]) == float(locversion["version"])) and  # local version
                    float(gitversion["subversion"]) > float(locversion["subversion"])):
                if messagebox.askyesno(
                        self.translate("Update available !"),
                        self.translate("An update is available, do you want to install it ?",
                                       f"\n\nVersion : {locversion['version']}.{locversion['subversion']} -> "
                                       f"{gitversion['version']}.{gitversion['subversion']}\n"
                                       f"Changelog :\n{gitversion['changelog']}")):

                    if not (os.path.exists("./Updater/Updater.exe")):
                        dl = requests.get(gitversion["updater_bin"], allow_redirects=True)
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

                if ((float(gitversion["version"]) < float(locversion["version"])) or  # if local version is newer than
                        (float(gitversion["version"]) == float(locversion["version"])) and  # github version
                        float(gitversion["subversion"]) < float(locversion["subversion"])):
                    self.is_dev_version = True

        except requests.ConnectionError:
            messagebox.showwarning(self.translate("Warning"),
                                   self.translate("Can't connect to internet. Download will be disabled."))
            self.option.disable_download = True

        except:
            self.log_error()


    def log_error(func):
        try:
            func()
        except Exception:
            error = traceback.format_exc()
            with open("./error.log", "a") as f:
                f.write(f"---\n{error}\n")
            messagebox.showerror(self.translate("Error"), self.translate("An error occured", " :", "\n", error, "\n\n"))


    def translate(self, *texts, lang=None):
        if lang is None:
            lang = self.stringvar_language.get()
        elif lang == "F":
            lang = "fr"
        elif lang == "G":
            lang = "ge"
        elif lang == "I":
            lang = "it"
        elif lang == "S":
            lang = "sp"

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


    def progress(self, show=None, indeter=None, step=None, statut=None, max=None, add=None):
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


    def state_button(self, enable=True):
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
