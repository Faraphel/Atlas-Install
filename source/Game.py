from . import wszst
from .definition import *
from threading import Thread
import subprocess
import shutil
import json
import glob
import os

region_id_to_name = {
    "J": "JAP",
    "P": "PAL",
    "K": "KO",
    "E": "USA"
}


class InvalidGamePath(Exception):
    def __init__(self):
        super().__init__("This path is not valid !")


class InvalidFormat(Exception):
    def __init__(self):
        super().__init__("This game format is not supported !")


class Game:
    def __init__(self, path: str, region_ID: str = "P", game_ID: str = "RMCP01"):
        if not os.path.exists(path): raise InvalidGamePath()
        self.extension = get_extension(path).upper()
        self.path = path
        self.region = region_id_to_name[region_ID]
        self.region_ID = region_ID
        self.game_ID = game_ID

    def extract_game(self):
        if self.extension == "DOL":
            self.path = os.path.realpath(self.path + "/../../")  # main.dol is in PATH/sys/, so go back 2 dir upper

        elif self.extension in ["ISO", "WBFS", "CSIO"]:
            # Fiding a directory name that doesn't already exist
            directory_name, i = "MKWiiFaraphel", 1
            while True:
                path_dir = os.path.realpath(self.path + f"/../{directory_name}")
                if not (os.path.exists(path_dir)): break
                directory_name, i = f"MKWiiFaraphel ({i})", i + 1

            wszst.extract(self.path, path_dir)

            self.path = path_dir
            if os.path.exists(self.path + "/DATA"): self.path += "/DATA"
            self.extension = "DOL"

        else:
            raise InvalidFormat()

        if glob.glob(self.path + "/files/rel/lecode-???.bin"):  # if a LECODE file is already here
            raise Warning("ROM Already patched")  # warning already patched

        with open(self.path + "/setup.txt") as f: setup = f.read()
        setup = setup[setup.find("!part-id = ") + len("!part-id = "):]
        self.game_ID = setup[:setup.find("\n")]

        self.region_ID = self.game_ID[3]
        self.region = region_id_to_name[self.region_ID] if self.region_ID in region_id_to_name else self.region

    def patch_autoadd(self, auto_add_dir: str = "./file/auto-add"):
        if os.path.exists(auto_add_dir): shutil.rmtree(auto_add_dir)
        if not os.path.exists(self.path + "/tmp/"): os.makedirs(self.path + "/tmp/")
        subprocess.run(["./tools/szs/wszst", "AUTOADD", get_nodir(self.path) + "/files/Race/Course/",
                        "--DEST", get_nodir(self.path) + "/tmp/auto-add/"],
                       creationflags=CREATE_NO_WINDOW, cwd=get_dir(self.path),
                       check=True, stdout=subprocess.PIPE)
        shutil.move(self.path + "/tmp/auto-add/", auto_add_dir)
        shutil.rmtree(self.path + "/tmp/")

    def install_mod(self, gui):
        def func():
            try:
                with open("./fs.json") as f: fs = json.load(f)

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
                    for f in glob.glob(self.path + "/files/" + fp, recursive=True):
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
                # self.Progress(show=True, indeter=False, statut=self.translate("Installing mod"), max=max_step, step=0)

                def replace_file(path, file, subpath="/"):
                    # self.Progress(statut=self.translate("Editing", "\n", get_nodir(path)), add=1)
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
                    for f in glob.glob(self.path + "/files/" + fp, recursive=True):
                        if type(fs[fp]) == str:
                            replace_file(path=f, file=fs[fp])
                        elif type(fs[fp]) == dict:
                            for nf in fs[fp]:
                                if type(fs[fp][nf]) == str:
                                    replace_file(path=f, subpath=nf, file=fs[fp][nf])
                                elif type(fs[fp][nf]) == list:
                                    for ffp in fs[fp][nf]: replace_file(path=f, subpath=nf, file=ffp)

                for file in extracted_file:
                    # self.Progress(statut=self.translate("Recompilating", "\n", get_nodir(file)), add=1)
                    subprocess.run(["./tools/szs/wszst", "CREATE", get_nodir(file) + ".d", "-d", get_nodir(file),
                                    "--overwrite"], creationflags=CREATE_NO_WINDOW, cwd=get_dir(file),
                                   check=True, stdout=subprocess.PIPE)
                    if os.path.exists(file + ".d"): shutil.rmtree(file + ".d")

                # self.Progress(statut=self.translate("Patch main.dol"), add=1)
                subprocess.run(["./tools/szs/wstrt", "patch", get_nodir(self.path) + "/sys/main.dol", "--clean-dol",
                                "--add-lecode"], creationflags=CREATE_NO_WINDOW, cwd=get_dir(self.path),
                               check=True, stdout=subprocess.PIPE)

                # self.Progress(statut=self.translate("Patch lecode.bin"), add=1)

                shutil.copytree("./file/Track/", self.path+"/files/Race/Course/", dirs_exist_ok=True)
                if not(os.path.exists(self.path+"/tmp/")): os.makedirs(self.path+"/tmp/")
                filecopy("./file/CTFILE.txt", self.path+"/tmp/CTFILE.txt")
                filecopy("./file/lpar-default.txt", self.path + "/tmp/lpar-default.txt")
                filecopy(f"./file/lecode-{self.region}.bin", self.path + f"/tmp/lecode-{self.region}.bin")

                subprocess.run(
                    ["./tools/szs/wlect", "patch", f"./tmp/lecode-{self.region}.bin", "-od",
                     f"./files/rel/lecode-{self.region}.bin", "--track-dir", "./files/Race/Course/",
                     "--move-tracks", "./files/Race/Course/", "--le-define", "./tmp/CTFILE.txt", "--lpar",
                     "./tmp/lpar-default.txt", "--overwrite"],
                    creationflags=CREATE_NO_WINDOW, cwd=self.path, check=True, stdout=subprocess.PIPE)

                shutil.rmtree(self.path + "/tmp/")

                output_format = gui.stringvar_game_format.get()
                # self.Progress(statut=self.translate("Converting to", " ", output_format), add=1)

                if output_format in ["ISO", "WBFS", "CISO"]:
                    path_game_format: str = os.path.realpath(self.path + "/../MKWFaraphel." + output_format.lower())
                    subprocess.run(["./tools/wit/wit", "COPY", get_nodir(self.path), "--DEST",
                                   get_nodir(path_game_format), f"--{output_format.lower()}", "--overwrite"],
                                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(path_game_format),
                                   check=True, stdout=subprocess.PIPE)
                    shutil.rmtree(self.path)
                    self.path = path_game_format

                    # self.Progress(statut=self.translate("Changing game's ID"), add=1)
                    subprocess.run(["./tools/wit/wit", "EDIT", get_nodir(self.path), "--id",
                                    f"RMC{self.region_ID}60", "--name",
                                    f"Mario Kart Wii Faraphel {gui.ctconfig.version}", "--modify", "ALL"],
                                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(self.path),
                                   check=True, stdout=subprocess.PIPE)

                # messagebox.showinfo(self.translate("End"), self.translate("The mod has been installed !"))

            except: pass  # self.log_error()
            finally: pass  # self.Progress(show=False)

        t = Thread(target=func)
        t.setDaemon(True)
        t.start()
        return t

    def convert_to(self, format: str = "FST"):
        """
        :param format: game format (ISO, WBFS, ...)
        :return: converted game path
        """