from tkinter import *
from tkinter import messagebox, filedialog, ttk
from threading import Thread
import subprocess
import shutil
import json
import glob
import os

def filecopy(src, dst):
    with open(src, "rb") as f1:
        with open(dst, "wb") as f2:
            f2.write(f1.read()) # could be buffered

get_filename = lambda file: ".".join(file.split(".")[:-1])
get_nodir = lambda file: file.split("/")[-1].split("\\")[-1]
get_extension = lambda file: file.split(".")[-1]

class ClassApp():
    def __init__(self):
        self.root = Tk()
        self.root.title("MKWFaraphel Installateur")
        self.root.resizable(False, False)

        self.frame_game_path = LabelFrame(self.root, text="Jeu original")
        self.frame_game_path.grid(row=1,column=1)

        self.path_mkwf = None

        entry_game_path = Entry(self.frame_game_path,width=50)
        entry_game_path.grid(row=1,column=1,sticky="NEWS")

        def select_path():
            path = filedialog.askopenfilename(filetypes = (("Jeu Wii", r"*.iso *.wbfs main.dol *.wia *.ciso"),))
            if os.path.exists(path):
                entry_game_path.delete(0, END)
                entry_game_path.insert(0, path)
        Button(self.frame_game_path, text="...", relief=RIDGE, command=select_path).grid(row=1,column=2,sticky="NEWS")

        def use_path():
            def func():
                self.frame_action.grid_forget()
                path = entry_game_path.get()
                if not(os.path.exists(path)):
                    messagebox.showerror("Erreur", "Le chemin de fichier est invalide")
                    return

                extension = get_extension(path)
                if extension.upper() == "DOL":
                    if messagebox.askyesno("Attention", "Ce dossier sera écrasé si vous installer le mod !\n" +\
                                           "Êtes-vous sûr de vouloir l'utiliser ?"):
                        self.path_mkwf = os.path.realpath(path + "/../../")
                elif extension.upper() in ["ISO", "WBFS", "WIA", "CSIO"]:
                    self.path_mkwf, i = os.path.realpath(path + "/../MKWiiFaraphel"), 1

                    while True:
                        if not(os.path.exists(self.path_mkwf)): break
                        self.path_mkwf, i = os.path.realpath(path + f"/../MKWiiFaraphel ({i})"), i+1

                    self.Progress(show=True, indeter=True, statut="Extraction du jeu...")
                    subprocess.call(["./tools/wit/wit", "EXTRACT", path, "--DEST", self.path_mkwf])
                    self.Progress(show=False)

                else:
                    messagebox.showerror("Erreur", "Le type de fichier n'est pas reconnu")
                    self.Progress(show=False)
                    return

                if os.path.exists(self.path_mkwf + "/files/rel/lecode-PAL.bin"):
                    messagebox.showwarning("Attention", "Cette ROM est déjà moddé,"+\
                                                        "il est déconseillé de l'utiliser pour installer le mod")

                self.frame_action.grid(row=2, column=1,sticky="NEWS")
                self.Progress(show=False)


            t=Thread(target=func)
            t.setDaemon(True)
            t.start()


        self.button_game_extract = Button(self.frame_game_path, text="Extraire le fichier", relief=RIDGE, command=use_path)
        self.button_game_extract.grid(row=2,column=1,columnspan=2,sticky="NEWS")

        self.frame_action = LabelFrame(self.root, text="Action")

        self.button_prepare_file = Button(self.frame_action, text="Preparer les fichiers", relief=RIDGE, command=self.patch_file, width=45)
        self.button_prepare_file.grid(row=1, column=1, sticky="NEWS")
        self.button_install_mod = Button(self.frame_action, text="Installer le mod", relief=RIDGE, command=self.install_mod, width=45)
        # Le boutton d'installation du mod n'est affiché qu'après avoir préparer les fichiers

        self.progressbar = ttk.Progressbar(self.root)
        self.progresslabel = Label(self.root)


    def Progress(self, show=None, indeter=None, step=None, statut=None, max=None, add=None):
        if indeter == True:
            self.progressbar.config(mode="indeterminate")
            self.progressbar.start(50)
        elif indeter == False: self.progressbar.config(mode="determinate")
        if show == True:
            self.StateButton(enable=False)
            self.progressbar.grid(row=100, column=1, sticky="NEWS")
            self.progresslabel.grid(row=101, column=1, sticky="NEWS")

        elif show == False:
            self.StateButton(enable=True)
            self.progressbar.grid_forget()
            self.progresslabel.grid_forget()

        if statut: self.progresslabel.config(text=statut)
        if step: self.progressbar["value"] = step
        if max:
            self.progressbar["maximum"] = max
            self.progressbar["value"] = 0
        if add: self.progressbar.step(add)


    def StateButton(self, enable=True):
        button = [
            self.button_game_extract,
            self.button_install_mod,
            self.button_prepare_file
        ]
        for widget in button:
            if enable: widget.config(state=NORMAL)
            else: widget.config(state=DISABLED)


    def patch_file(self):
        def func():
            if os.path.exists("./file/Track-WU8/"): total_track = len(os.listdir("./file/Track-WU8/"))
            else: total_track = 0
            with open("./convert_file.json") as f: fc = json.load(f)
            max_step = len(fc["img"])+len(fc["bmg"])+total_track
            self.Progress(show=True, indeter=False, statut="Conversion des fichiers", max=max_step, step=0)

            for i, file in enumerate(fc["img"]):
                self.Progress(statut=f"Conversion des images\n({i+1}/{len(fc['img'])}) {file}", add=1)
                if not(os.path.exists("./file/"+get_filename(file))):
                    subprocess.call(["./tools/szs/wimgt", "ENCODE", "./file/"+file, "-x", fc["img"][file]])

            for i, file in enumerate(fc["bmg"]):
                self.Progress(statut=f"Conversion des textes\n({i+1}/{len(fc['bmg'])}) {file}", add=1)
                if not(os.path.exists("./file/"+get_filename(file)+".bmg")):
                    subprocess.call(["./tools/szs/wbmgt", "ENCODE", "./file/"+file])

            if not(os.path.exists("./file/auto-add/")):
                subprocess.call(["./tools/szs/wszst", "AUTOADD", self.path_mkwf+"/files/Race/Course/", "--DEST", "./file/auto-add/"])

            if os.path.exists("./file/Track-WU8/"):
                for i, file in enumerate(os.listdir("./file/Track-WU8/")):
                    self.Progress(statut=f"Conversion des courses\n({i+1}/{total_track}) {file}", add=1)
                    subprocess.call(["./tools/szs/wszst", "NORMALIZE", "./file/Track-WU8/"+file, "--DEST", "./file/Track/%N.szs",
                                     "--szs", "--overwrite", "--autoadd-path", "./file/auto-add/"])
                shutil.rmtree("./file/Track-WU8/")

            self.Progress(show=False)
            self.button_install_mod.grid(row=2,column=1,sticky="NEWS")

        t=Thread(target=func)
        t.setDaemon(True)
        t.start()


    def install_mod(self):
        def func():
            with open("./fs.json") as f: fs = json.load(f)

            ### This part is used to estimate the max_step
            extracted_file = []
            max_step, step = 0, 0

            def count_rf(path, file, subpath="/"):
                nonlocal max_step
                max_step += 1
                extension = get_extension(path)
                if extension == "szs":
                    if not(os.path.realpath(path) in extracted_file):
                        extracted_file.append(os.path.realpath(path))
                        max_step += 1

            for fp in fs:
                for f in glob.glob(self.path_mkwf + "/files/" + fp, recursive=True):
                    if type(fs[fp]) == str: count_rf(path=f, file=fs[fp])
                    elif type(fs[fp]) == dict:
                        for nf in fs[fp]:
                            if type(fs[fp][nf]) == str: count_rf(path=f, subpath=nf, file=fs[fp][nf])
                            elif type(fs[fp][nf]) == list:
                                for ffp in fs[fp][nf]: count_rf(path=f, subpath=nf, file=ffp)
            ###
            extracted_file = []
            max_step += 2 # PATCH main.dol et PATCH lecode.bin
            self.Progress(show=True, indeter=False, statut="Installation du mod", max=max_step, step=0)



            def replace_file(path, file, subpath="/"):
                self.Progress(statut=f"Modification de\n{get_nodir(path)+subpath+file}", add=1)
                #print(path, subpath, file)
                extension = get_extension(path)

                if extension == "szs":
                    if not(os.path.realpath(path) in extracted_file):
                        subprocess.call(["./tools/szs/wszst", "EXTRACT", path, "-d", path+".d", "--overwrite"])
                        extracted_file.append(os.path.realpath(path))

                    szs_extract_path = path+".d"
                    if os.path.exists(szs_extract_path+subpath):
                        if subpath[-1] == "/": filecopy(f"./file/{file}", szs_extract_path+subpath+file)
                        else: filecopy(f"./file/{file}", szs_extract_path+subpath)

                elif path[-1] == "/": filecopy(f"./file/{file}", path+file)
                else: filecopy(f"./file/{file}", path)

            for fp in fs:
                for f in glob.glob(self.path_mkwf + "/files/" + fp, recursive=True):
                    if type(fs[fp]) == str: replace_file(path=f, file=fs[fp])
                    elif type(fs[fp]) == dict:
                        for nf in fs[fp]:
                            if type(fs[fp][nf]) == str: replace_file(path=f, subpath=nf, file=fs[fp][nf])
                            elif type(fs[fp][nf]) == list:
                                for ffp in fs[fp][nf]: replace_file(path=f, subpath=nf, file=ffp)


            for file in extracted_file:
                self.Progress(statut=f"Recompilation de\n{file}", add=1)
                subprocess.call(["./tools/szs/wszst", "CREATE", file+".d", "-d", file, "--overwrite"])
                if os.path.exists(file+".d"): shutil.rmtree(file+".d")

            self.Progress(statut=f"Patch main.dol", add=1)
            subprocess.call(["./tools/szs/wstrt", "patch", self.path_mkwf+"/sys/main.dol", "--clean-dol", "--add-lecode"])
            self.Progress(statut=f"Patch lecode-PAL.bin", add=1)
            subprocess.call(
                ["./tools/szs/wlect", "patch", "./file/lecode-PAL.bin", "-od", self.path_mkwf+"/files/rel/lecode-PAL.bin",
                "--track-dir", self.path_mkwf+"/files/Race/Course/", "--copy-tracks", "./file/Track/",
                "--move-tracks", self.path_mkwf+"/files/Race/Course/", "--le-define",
                "./file/CTFILE.txt", "--lpar", "./file/lpar-default.txt", "--overwrite"])

            self.Progress(show=False)
            messagebox.showinfo("", "L'installation est terminé !")

        t = Thread(target=func)
        t.setDaemon(True)
        t.start()

# TODO: Langue
# TODO: Icones
# TODO: Update
# TODO: Changer l'ID
# TODO: Convertir en ISO / WBFS... après l'installation
App = ClassApp()
mainloop()