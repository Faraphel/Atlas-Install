from tkinter import messagebox
from threading import Thread
import subprocess
import shutil
import json
import glob
import os

from .definition import *


def install_mod(self):
    def func():
        with open("./fs.json") as f:
            fs = json.load(f)

        # This part is used to estimate the max_step
        extracted_file = []
        max_step, step = 1, 0

        def count_rf(path):
            nonlocal max_step
            max_step += 1
            extension = get_extension(path)
            if extension == "szs":
                if not (os.path.realpath(path) in extracted_file):
                    extracted_file.append(os.path.realpath(path))
                    max_step += 1

        for fp in fs:
            for f in glob.glob(self.path_mkwf + "/files/" + fp, recursive=True):
                if type(fs[fp]) == str:
                    count_rf(path=f)
                elif type(fs[fp]) == dict:
                    for nf in fs[fp]:
                        if type(fs[fp][nf]) == str:
                            count_rf(path=f)
                        elif type(fs[fp][nf]) == list:
                            for ffp in fs[fp][nf]: count_rf(path=f)
        ###
        extracted_file = []
        max_step += 4  # PATCH main.dol et PATCH lecode.bin, conversion, changement d'ID
        self.Progress(show=True, indeter=False, statut=self.translate("Installation du mod"), max=max_step, step=0)

        def replace_file(path, file, subpath="/"):
            self.Progress(statut=self.translate("Modification de")+f"\n{get_nodir(path)}", add=1)
            # print(path, subpath, file)
            extension = get_extension(path)

            if extension == "szs":
                if not (os.path.realpath(path) in extracted_file):
                    subprocess.call(["./tools/szs/wszst", "EXTRACT", path, "-d", path + ".d", "--overwrite"]
                                    , creationflags=CREATE_NO_WINDOW)
                    extracted_file.append(os.path.realpath(path))

                szs_extract_path = path + ".d"
                if os.path.exists(szs_extract_path + subpath):
                    if subpath[-1] == "/":
                        filecopy(f"./file/{file}", szs_extract_path + subpath + file)
                    else:
                        filecopy(f"./file/{file}", szs_extract_path + subpath)

            elif path[-1] == "/":
                filecopy(f"./file/{file}", path + file)
            else:
                filecopy(f"./file/{file}", path)

        for fp in fs:
            for f in glob.glob(self.path_mkwf + "/files/" + fp, recursive=True):
                if type(fs[fp]) == str:
                    replace_file(path=f, file=fs[fp])
                elif type(fs[fp]) == dict:
                    for nf in fs[fp]:
                        if type(fs[fp][nf]) == str:
                            replace_file(path=f, subpath=nf, file=fs[fp][nf])
                        elif type(fs[fp][nf]) == list:
                            for ffp in fs[fp][nf]: replace_file(path=f, subpath=nf, file=ffp)

        for file in extracted_file:
            self.Progress(statut=self.translate("Recompilation de")+f"\n{get_nodir(file)}", add=1)
            subprocess.call(["./tools/szs/wszst", "CREATE", file + ".d", "-d", file,
                             "--overwrite"], creationflags=CREATE_NO_WINDOW)
            if os.path.exists(file + ".d"): shutil.rmtree(file + ".d")

        self.Progress(statut=self.translate("Patch main.dol"), add=1)
        subprocess.call(["./tools/szs/wstrt", "patch", self.path_mkwf + "/sys/main.dol", "--clean-dol",
                         "--add-lecode"], creationflags=CREATE_NO_WINDOW)

        self.Progress(statut=self.translate("Patch lecode-PAL.bin"), add=1)

        subprocess.call(
            ["./tools/szs/wlect", "patch", "./file/lecode-PAL.bin", "-od", self.path_mkwf + "/files/rel/lecode-PAL.bin",
             "--track-dir", self.path_mkwf + "/files/Race/Course/", "--copy-tracks", "./file/Track/",
             "--move-tracks", self.path_mkwf + "/files/Race/Course/", "--le-define",
             "./file/CTFILE.txt", "--lpar", "./file/lpar-default.txt", "--overwrite"], creationflags=CREATE_NO_WINDOW)

        outputformat = self.listbox_outputformat.get()
        self.Progress(statut=self.translate("Conversion en")+f" {outputformat}", add=1)

        if outputformat in ["ISO", "WBFS", "CISO"]:
            self.path_mkwf_format = os.path.realpath(self.path_mkwf + "/../MKWFaraphel." + outputformat.lower())
            subprocess.call(["./tools/wit/wit", "COPY", self.path_mkwf, "--DEST",
                             self.path_mkwf_format, f"--{outputformat.lower()}", "--overwrite"]
                            , creationflags=CREATE_NO_WINDOW)
            shutil.rmtree(self.path_mkwf)

            self.Progress(statut=self.translate("Changement de l'ID du jeu"), add=1)
            subprocess.call(["./tools/wit/wit", "EDIT", self.path_mkwf_format, "--id", "RMCP60"]
                            , creationflags=CREATE_NO_WINDOW)

        self.Progress(show=False)
        messagebox.showinfo(self.translate("Fin"), self.translate("L'installation est terminé !"))

    t = Thread(target=func)
    t.setDaemon(True)
    t.start()
