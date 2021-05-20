from tkinter import *
from tkinter import messagebox, filedialog, ttk
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
if not(os.path.exists("./file/Track/")):
    os.makedirs("./file/Track/")

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
            self.frame_action.grid_forget()
            path = entry_game_path.get()
            if not(os.path.exists(path)): return messagebox.showerror("Erreur", "Le chemin de fichier est invalide")
            extension = path.split(".")[-1]
            if extension.upper() == "DOL":
                if messagebox.askyesno("Attention", "Ce dossier sera écrasé si vous installer le mod !\n" +\
                                       "Êtes-vous sûr de vouloir l'utiliser ?"):
                    self.path_mkwf = os.path.realpath(path + "/../../")
            elif extension.upper() in ["ISO", "WBFS", "WIA", "CSIO"]:
                self.path_mkwf, i = os.path.realpath(path + "/../MKWiiFaraphel"), 1

                while True:
                    if not(os.path.exists(self.path_mkwf)): break
                    self.path_mkwf, i = os.path.realpath(path + f"/../MKWiiFaraphel ({i})"), i+1
                subprocess.call(["./tools/wit/wit", "EXTRACT", path, "-d", self.path_mkwf])

            else: return messagebox.showerror("Erreur", "Le type de fichier n'est pas reconnu")

            if os.path.exists(self.path_mkwf + "/files/rel/lecode-PAL.bin"):
                messagebox.showwarning("Attention", "Cette ROM est déjà moddé,"+\
                                                    "il est déconseillé de l'utiliser pour installer le mod")

            self.frame_action.grid(row=2, column=1,sticky="NEWS")

        Button(self.frame_game_path, text="Extraire le fichier", relief=RIDGE, command=use_path)\
            .grid(row=2,column=1,columnspan=2,sticky="NEWS")

        self.frame_action = LabelFrame(self.root, text="Action")

        Button(self.frame_action, text="Installer le mod", relief=RIDGE, command=self.install_mod, width=45
               ).grid(row=1,column=1,sticky="NEWS")


    def patch_file(self):
        with open("./convert_file.json") as f: fc = json.load(f)
        for file in fc["img"]:
            print(get_filename(file))
            if not(os.path.exists("./file/"+get_filename(file))):
                subprocess.call(["./tools/szs/wimgt", "ENCODE", "./file/"+file, "-x", fc["img"][file]])

        for file in fc["bmg"]:
            if not(os.path.exists("./file/"+get_filename(file)+".bmg")):
                subprocess.call(["./tools/szs/wbmgt", "ENCODE", "./file/"+file])

        if os.path.exists("./file/Track-WU8/"):
            subprocess.call(["./tools/szs/wszst", "NORMALIZE", "./file/Track-WU8/*.wu8", "-d", "./file/Track/%N.szs", "--szs",
                             "--overwrite", "--autoadd-path", self.path_mkwf+"/files/Race/Course/"])
            shutil.rmtree("./file/Track-WU8/")


    def install_mod(self):
        self.patch_file()

        with open("./fs.json") as f: fs = json.load(f)
        extracted_file = []

        def replace_file(path, file, subpath="/"):
            print(path, subpath, file)
            extension = path.split(".")[-1]

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


        print(extracted_file)
        for file in extracted_file:
            subprocess.call(["./tools/szs/wszst", "CREATE", file+".d", "-d", file, "--overwrite"])
            if os.path.exists(file+".d"): shutil.rmtree(file+".d")

        subprocess.call(["./tools/szs/wstrt", "patch", self.path_mkwf+"/sys/main.dol", "--clean-dol", "--add-lecode"])
        subprocess.call(
            ["./tools/szs/wlect", "patch", "./file/lecode-PAL.bin", "-od", self.path_mkwf+"/files/rel/lecode-PAL.bin",
            "--track-dir", self.path_mkwf+"/files/Race/Course/", "--copy-tracks", "./file/Track/",
            "--move-tracks", self.path_mkwf+"/files/Race/Course/", "--le-define",
            "./file/CTFILE.txt", "--lpar", "./file/lpar-default.txt", "--overwrite"])

        messagebox.showinfo("", "L'installation est terminé !")

# TODO: Langue
# TODO: Icones
# TODO: Update
# TODO: Progress bar
# TODO: Changer l'ID
App = ClassApp()
mainloop()