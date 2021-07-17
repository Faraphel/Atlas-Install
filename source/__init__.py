from tkinter import *
from tkinter import messagebox, filedialog, ttk
from threading import Thread
import subprocess
import glob
import os

from .definition import *
from .check_update import check_update
from .translate import translate
from .CT_Config import *
from .Game import *

def __init__(self):
    try:
        self.root = Tk()

        self.load_option()
        self.ctconfig = CT_Config()
        self.ctconfig.load_ctconfig_file("./ct_config.json")

        self.stringvar_language = StringVar(value=self.option["language"])
        self.stringvar_game_format = StringVar(value=self.option["format"])
        self.boolvar_disable_download = BooleanVar(value=self.option["disable_download"])
        self.boolvar_del_track_after_conv = BooleanVar(value=self.option["del_track_after_conv"])
        self.boolvar_dont_check_for_update = BooleanVar(value=self.option["dont_check_for_update"])
        self.boolvar_dont_check_track_sha1 = BooleanVar(value=self.option["dont_check_track_sha1"])
        self.intvar_process_track = IntVar(value=self.option["process_track"])
        self.boolvar_use_1star_track = BooleanVar(value=True)
        self.boolvar_use_2star_track = BooleanVar(value=True)
        self.boolvar_use_3star_track = BooleanVar(value=True)
        self.stringvar_mark_track_from_version = StringVar(value="None")

        self.root.title(self.translate("MKWFaraphel Installer"))
        self.root.resizable(False, False)
        self.root.iconbitmap(bitmap="./icon.ico")

        if not(self.boolvar_dont_check_for_update.get()): self.check_update()
        self.path_mkwf = None


        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.menu_language = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.translate("Language"), menu=self.menu_language)
        self.menu_language.add_radiobutton(label="Français", variable=self.stringvar_language, value="fr", command=lambda: self.change_option("language", "fr", restart=True))
        self.menu_language.add_radiobutton(label="English", variable=self.stringvar_language, value="en", command=lambda: self.change_option("language", "en", restart=True))

        self.menu_format = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.translate("Format"), menu=self.menu_format)
        self.menu_format.add_radiobutton(label=self.translate("FST (Directory)"), variable=self.stringvar_game_format, value="FST", command=lambda: self.change_option("format", "FST"))
        self.menu_format.add_radiobutton(label="ISO", variable=self.stringvar_game_format, value="ISO", command=lambda: self.change_option("format", "ISO"))
        self.menu_format.add_radiobutton(label="CISO", variable=self.stringvar_game_format, value="CISO", command=lambda: self.change_option("format", "CISO"))
        self.menu_format.add_radiobutton(label="WBFS", variable=self.stringvar_game_format, value="WBFS", command=lambda: self.change_option("format", "WBFS"))

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
        self.menu_advanced.add_checkbutton(label=self.translate("Disable downloads"), variable=self.boolvar_disable_download, command=lambda: self.change_option("disable_download", self.boolvar_disable_download))
        self.menu_advanced.add_checkbutton(label=self.translate("Delete track after wu8 to szs conversion"), variable=self.boolvar_del_track_after_conv, command=lambda: self.change_option("del_track_after_conv", self.boolvar_del_track_after_conv))
        self.menu_advanced.add_checkbutton(label=self.translate("Don't check for update"), variable=self.boolvar_dont_check_for_update, command=lambda: self.change_option("dont_check_for_update", self.boolvar_dont_check_for_update))
        self.menu_advanced.add_checkbutton(label=self.translate("Don't check track's sha1"), variable=self.boolvar_dont_check_track_sha1, command=lambda: self.change_option("dont_check_track_sha1",self.boolvar_dont_check_track_sha1))

        self.menu_advanced.add_separator()
        self.menu_advanced.add_command(label=self.translate("Number of track conversion process", " :"))
        self.menu_advanced.add_radiobutton(label=self.translate("1 ", "process"), variable=self.intvar_process_track, value=1, command=lambda: self.change_option("process_track", 1))
        self.menu_advanced.add_radiobutton(label=self.translate("2 ", "process"), variable=self.intvar_process_track, value=2, command=lambda: self.change_option("process_track", 2))
        self.menu_advanced.add_radiobutton(label=self.translate("4 ", "process"), variable=self.intvar_process_track, value=4, command=lambda: self.change_option("process_track", 4))
        self.menu_advanced.add_radiobutton(label=self.translate("8 ", "process"), variable=self.intvar_process_track, value=8, command=lambda: self.change_option("process_track", 8))


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
                    self.Progress(show=True, indeter=True, statut=self.translate("Extracting the game..."))
                    self.game.extract_game()
                    self.frame_action.grid(row=3, column=1, sticky="NEWS")
                except InvalidGamePath:
                    messagebox.showerror(self.translate("Error"), self.translate("The file path in invalid"))
                except InvalidFormat:
                    messagebox.showerror(self.translate("Error"), self.translate("This game's format is invalid"))
                except:
                    self.log_error()
                finally:
                    self.Progress(show=False)

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
                self.patch_file().join()
                self.install_mod().join()

            if messagebox.askyesno(self.translate("Experimental functionality"),
                self.translate("This will extract the selected ROM, prepare files and install mod. "
                               "Do you wish to continue ?")):
                t = Thread(target=func)
                t.setDaemon(True)
                t.start()

        self.button_do_everything = Button(self.frame_game_path_action, text=self.translate("Do everything"),
                                          relief=RIDGE, command=do_everything)
        self.button_do_everything.grid(row=1, column=2, sticky="NEWS")


        self.frame_action = LabelFrame(self.root, text=self.translate("Action"))

        self.button_prepare_file = Button(self.frame_action, text=self.translate("Prepare files"), relief=RIDGE,
                                          command=self.patch_file, width=45)
        self.button_prepare_file.grid(row=1, column=1, columnspan=2, sticky="NEWS")
        self.button_install_mod = Button(self.frame_action, text=self.translate("Install mod"), relief=RIDGE,
                                         command=self.install_mod, width=45)
        # Install mod button will only appear after prepare file step

        self.progressbar = ttk.Progressbar(self.root)
        self.progresslabel = Label(self.root)

    except:
        self.log_error()
