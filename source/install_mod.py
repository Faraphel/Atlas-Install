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
        try:
            with open("./fs.json") as f:
                fs = json.load(f)

            # This part is used to estimate the max_step
            extracted_file = []
            max_step, step = 1, 0

            def count_rf(path):
                nonlocal max_step
                max_step += 1
                if get_extension(path) == "szs":
                    if not (os.path.realpath(path) in extracted_file):
                        extracted_file.append(os.path.realpath(path))
                        max_step += 1

            for fp in fs:
                for f in glob.glob(self.game.path + "/files/" + fp, recursive=True):
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
            max_step += 4  # PATCH main.dol and PATCH lecode.bin, converting, changing ID
            self.Progress(show=True, indeter=False, statut=self.translate("Installing mod"), max=max_step, step=0)

            def replace_file(path, file, subpath="/"):
                self.Progress(statut=self.translate("Editing", "\n", get_nodir(path)), add=1)
                extension = get_extension(path)

                if extension == "szs":
                    if not (os.path.realpath(path) in extracted_file):
                        subprocess.run(["./tools/szs/wszst", "EXTRACT", get_nodir(path), "-d", get_nodir(path) + ".d",
                                        "--overwrite"], creationflags=CREATE_NO_WINDOW, cwd=get_dir(path),
                                       check=True, stdout=subprocess.PIPE)
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
                for f in glob.glob(self.game.path + "/files/" + fp, recursive=True):
                    if type(fs[fp]) == str:
                        replace_file(path=f, file=fs[fp])
                    elif type(fs[fp]) == dict:
                        for nf in fs[fp]:
                            if type(fs[fp][nf]) == str:
                                replace_file(path=f, subpath=nf, file=fs[fp][nf])
                            elif type(fs[fp][nf]) == list:
                                for ffp in fs[fp][nf]: replace_file(path=f, subpath=nf, file=ffp)

            for file in extracted_file:
                self.Progress(statut=self.translate("Recompilating", "\n", get_nodir(file)), add=1)
                subprocess.run(["./tools/szs/wszst", "CREATE", get_nodir(file) + ".d", "-d", get_nodir(file),
                                "--overwrite"], creationflags=CREATE_NO_WINDOW, cwd=get_dir(file),
                               check=True, stdout=subprocess.PIPE)
                if os.path.exists(file + ".d"): shutil.rmtree(file + ".d")

            self.Progress(statut=self.translate("Patch main.dol"), add=1)
            subprocess.run(["./tools/szs/wstrt", "patch", get_nodir(self.game.path) + "/sys/main.dol", "--clean-dol",
                            "--add-lecode"], creationflags=CREATE_NO_WINDOW, cwd=get_dir(self.game.path),
                           check=True, stdout=subprocess.PIPE)

            self.Progress(statut=self.translate("Patch lecode.bin"), add=1)

            shutil.copytree("./file/Track/", self.game.path+"/files/Race/Course/", dirs_exist_ok=True)
            if not(os.path.exists(self.game.path+"/tmp/")): os.makedirs(self.game.path+"/tmp/")
            filecopy("./file/CTFILE.txt", self.game.path+"/tmp/CTFILE.txt")
            filecopy("./file/lpar-default.txt", self.game.path + "/tmp/lpar-default.txt")
            filecopy(f"./file/lecode-{self.game.region}.bin", self.game.path + f"/tmp/lecode-{self.game.region}.bin")

            subprocess.run(
                ["./tools/szs/wlect", "patch", f"./tmp/lecode-{self.game.region}.bin", "-od",
                 f"./files/rel/lecode-{self.game.region}.bin", "--track-dir", "./files/Race/Course/",
                 "--move-tracks", "./files/Race/Course/", "--le-define", "./tmp/CTFILE.txt", "--lpar",
                 "./tmp/lpar-default.txt", "--overwrite"],
                creationflags=CREATE_NO_WINDOW, cwd=self.game.path, check=True, stdout=subprocess.PIPE)

            shutil.rmtree(self.game.path + "/tmp/")

            outputformat = self.stringvar_game_format.get()
            self.Progress(statut=self.translate("Converting to", " ", outputformat), add=1)

            if outputformat in ["ISO", "WBFS", "CISO"]:
                path_game_format: str = os.path.realpath(self.game.path + "/../MKWFaraphel." + outputformat.lower())
                subprocess.run(["./tools/wit/wit", "COPY", get_nodir(self.game.path), "--DEST",
                               get_nodir(path_game_format), f"--{outputformat.lower()}", "--overwrite"],
                               creationflags=CREATE_NO_WINDOW, cwd=get_dir(path_game_format),
                               check=True, stdout=subprocess.PIPE)
                shutil.rmtree(self.game.path)
                self.game.path = path_game_format

                self.Progress(statut=self.translate("Changing game's ID"), add=1)
                subprocess.run(["./tools/wit/wit", "EDIT", get_nodir(self.game.path), "--id",
                                f"RMC{self.game.region_ID}60", "--name",
                                f"Mario Kart Wii Faraphel {self.ctconfig.version}", "--modify", "ALL"],
                               creationflags=CREATE_NO_WINDOW, cwd=get_dir(self.game.path),
                               check=True, stdout=subprocess.PIPE)

            messagebox.showinfo(self.translate("End"), self.translate("The mod has been installed !"))

        except: self.log_error()
        finally: self.Progress(show=False)

    t = Thread(target=func)
    t.setDaemon(True)
    t.start()
    return t