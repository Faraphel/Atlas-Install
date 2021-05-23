from tkinter import *
from tkinter import messagebox, filedialog, ttk
from threading import Thread
import subprocess
import os

from .definition import *
from .check_update import check_update


def __init__(self):
    self.root = Tk()
    self.root.title("MKWFaraphel Installateur")
    self.root.resizable(False, False)
    self.root.iconbitmap(bitmap="./icon.ico")

    self.frame_game_path = LabelFrame(self.root, text="Jeu original")
    self.frame_game_path.grid(row=1, column=1)

    check_update()
    self.path_mkwf = None

    entry_game_path = Entry(self.frame_game_path, width=50)
    entry_game_path.grid(row=1, column=1, sticky="NEWS")

    def select_path():
        path = filedialog.askopenfilename(filetypes=(("Jeu Wii", r"*.iso *.wbfs main.dol *.wia *.ciso"),))
        if os.path.exists(path):
            entry_game_path.delete(0, END)
            entry_game_path.insert(0, path)

    Button(self.frame_game_path, text="...", relief=RIDGE, command=select_path).grid(row=1, column=2, sticky="NEWS")

    def use_path():
        def func():
            self.frame_action.grid_forget()
            path = entry_game_path.get()
            if not (os.path.exists(path)):
                messagebox.showerror("Erreur", "Le chemin de fichier est invalide")
                return

            extension = get_extension(path)
            if extension.upper() == "DOL":
                if messagebox.askyesno("Attention", "Ce dossier sera écrasé si vous installer le mod !\n" + \
                                                    "Êtes-vous sûr de vouloir l'utiliser ?"):
                    self.path_mkwf = os.path.realpath(path + "/../../")
            elif extension.upper() in ["ISO", "WBFS", "WIA", "CSIO"]:
                self.path_mkwf, i = os.path.realpath(path + "/../MKWiiFaraphel"), 1

                while True:
                    if not (os.path.exists(self.path_mkwf)): break
                    self.path_mkwf, i = os.path.realpath(path + f"/../MKWiiFaraphel ({i})"), i + 1

                self.Progress(show=True, indeter=True, statut="Extraction du jeu...")
                subprocess.call(["./tools/wit/wit", "EXTRACT", path, "--DEST", self.path_mkwf]
                                , creationflags=CREATE_NO_WINDOW)
                self.Progress(show=False)

            else:
                messagebox.showerror("Erreur", "Le type de fichier n'est pas reconnu")
                self.Progress(show=False)
                return

            if os.path.exists(self.path_mkwf + "/files/rel/lecode-PAL.bin"):
                messagebox.showwarning("Attention", "Cette ROM est déjà moddé, " + \
                                       "il est déconseillé de l'utiliser pour installer le mod")

            self.frame_action.grid(row=2, column=1, sticky="NEWS")
            self.Progress(show=False)

        t = Thread(target=func)
        t.setDaemon(True)
        t.start()

    self.button_game_extract = Button(self.frame_game_path, text="Extraire le fichier", relief=RIDGE, command=use_path)
    self.button_game_extract.grid(row=2, column=1, columnspan=2, sticky="NEWS")

    self.frame_action = LabelFrame(self.root, text="Action")

    self.button_prepare_file = Button(self.frame_action, text="Preparer les fichiers", relief=RIDGE,
                                      command=self.patch_file, width=45)
    self.button_prepare_file.grid(row=1, column=1, columnspan=2, sticky="NEWS")
    self.button_install_mod = Button(self.frame_action, text="Installer le mod", relief=RIDGE, command=self.install_mod,
                                     width=35)
    self.listbox_outputformat = ttk.Combobox(self.frame_action, values=["Dossier", "ISO", "WBFS", "CISO"], width=5)
    self.listbox_outputformat.set("Dossier")
    # Le boutton d'installation du mod n'est affiché qu'après avoir préparer les fichiers

    self.progressbar = ttk.Progressbar(self.root)
    self.progresslabel = Label(self.root)
