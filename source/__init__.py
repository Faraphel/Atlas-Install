from tkinter import *
from tkinter import messagebox, filedialog, ttk
from threading import Thread
import subprocess
import glob
import os

from .definition import *
from .check_update import check_update
from .translate import translate

def __init__(self):
    try:

        self.root = Tk()

        self.load_option()
        self.stringvar_language = StringVar(value=self.option["language"])
        self.stringvar_game_format = StringVar(value=self.option["format"])
        self.boolvar_disable_download = BooleanVar(value=self.option["disable_download"])
        self.boolvar_del_track_after_conv = BooleanVar(value=self.option["del_track_after_conv"])
        self.boolvar_dont_check_for_update = BooleanVar(value=self.option["dont_check_for_update"])
        self.boolvar_dont_check_track_sha1 = BooleanVar(value=self.option["dont_check_track_sha1"])
        self.intvar_process_track = IntVar(value=self.option["process_track"])

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
                try:
                    self.frame_action.grid_forget()
                    path = entry_game_path.get()
                    if not (os.path.exists(path)):
                        messagebox.showerror(self.translate("Error"), self.translate("The file path in invalid"))
                        return

                    extension = get_extension(path)
                    if extension.upper() == "DOL":
                        if messagebox.askyesno(self.translate("Warning"),
                                               self.translate("This directory will be overwritten if you install the "
                                                              "mod !\n Are you sure you want to use it ?")):
                            self.path_mkwf = os.path.realpath(path + "/../../")
                        else: return
                    elif extension.upper() in ["ISO", "WBFS", "CSIO"]:
                        # Fiding a directory name that dosen't already exist
                        directory_name, i = "MKWiiFaraphel", 1
                        while True:
                            self.path_mkwf = os.path.realpath(path + f"/../{directory_name}")
                            if not(os.path.exists(self.path_mkwf)): break
                            directory_name, i = f"MKWiiFaraphel ({i})", i + 1

                        self.Progress(show=True, indeter=True, statut=self.translate("Extracting the game..."))
                        subprocess.call(["./tools/wit/wit", "EXTRACT", get_nodir(path), "--DEST", directory_name]
                                        , creationflags=CREATE_NO_WINDOW, cwd=get_dir(path))

                        if os.path.exists(self.path_mkwf + "/DATA"): self.path_mkwf += "/DATA"

                        self.Progress(show=False)

                    else:
                        messagebox.showerror(self.translate("Error"), self.translate("This file type is not supported"))
                        self.Progress(show=False)
                        return

                    if glob.glob(self.path_mkwf + "/files/rel/lecode-???.bin"): # if a LECODE file is already here
                        messagebox.showwarning(self.translate("Warning"),
                                               self.translate("This game is already modded, it is not recommended to "
                                                              "use it to install the mod"))

                    try:
                        with open(self.path_mkwf + "/setup.txt") as f: setup = f.read()
                        setup = setup[setup.find("!part-id = ")+len("!part-id = "):]
                        self.original_game_ID = setup[:setup.find("\n")]
                    except:
                        messagebox.showwarning(self.translate("Warning"),
                                               self.transate("Can't find game region.\nPAL region will be used."))
                        self.original_game_ID = "RMCP01"
                    try:
                        self.original_region_ID = self.original_game_ID[3]
                        self.original_region = region_ID[self.original_region_ID]
                    except: self.original_region = "PAL"

                    self.frame_action.grid(row=3, column=1, sticky="NEWS")

                except: self.log_error()
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
