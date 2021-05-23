from threading import Thread
import subprocess
import json
import os

from .definition import *


def patch_file(self):
    def func():
        if os.path.exists("./file/Track-WU8/"):
            total_track = len(os.listdir("./file/Track-WU8/"))
        else:
            total_track = 0
        with open("./convert_file.json") as f:
            fc = json.load(f)
        max_step = len(fc["img"]) + len(fc["bmg"]) + total_track + 1
        self.Progress(show=True, indeter=False, statut="Conversion des fichiers", max=max_step, step=0)

        for i, file in enumerate(fc["img"]):
            self.Progress(statut=f"Conversion des images\n({i + 1}/{len(fc['img'])}) {file}", add=1)
            if not (os.path.exists("./file/" + get_filename(file))):
                subprocess.call(["./tools/szs/wimgt", "ENCODE", "./file/" + file, "-x", fc["img"][file]]
                                , creationflags=CREATE_NO_WINDOW)

        for i, file in enumerate(fc["bmg"]):
            self.Progress(statut=f"Conversion des textes\n({i + 1}/{len(fc['bmg'])}) {file}", add=1)
            if not (os.path.exists("./file/" + get_filename(file) + ".bmg")):
                subprocess.call(["./tools/szs/wbmgt", "ENCODE", "./file/" + file]
                                , creationflags=CREATE_NO_WINDOW)

        if not (os.path.exists("./file/auto-add/")):
            subprocess.call(["./tools/szs/wszst", "AUTOADD", self.path_mkwf + "/files/Race/Course/", "--DEST",
                             "./file/auto-add/"], creationflags=CREATE_NO_WINDOW)

        max_process = 8
        process_list = {}

        for i, file in enumerate(os.listdir("./file/Track-WU8/")):
            while True:
                if len(process_list) < max_process:
                    process_list[file] = None
                    self.Progress(statut=f"Conversion des courses\n({i + 1}/{total_track})\n" +
                                         "\n".join(process_list.keys()), add=1)

                    if not (os.path.exists("./file/Track/" + get_filename(file) + ".szs")):
                        process_list[file] = subprocess.Popen([
                            "./tools/szs/wszst", "NORMALIZE", "./file/Track-WU8/" + file, "--DEST",
                            "./file/Track/%N.szs", "--szs", "--overwrite", "--autoadd-path",
                            "./file/auto-add/"], creationflags=CREATE_NO_WINDOW)
                    break
                else:
                    for process in process_list:
                        if process_list[process] is not None:
                            if not (process_list[process].poll() is None):
                                process_list.pop(process)
                                break
                        else:
                            process_list.pop(process)
                            break

        self.Progress(statut="Création de LE-CODE", add=1)
        self.create_lecode_config()

        self.Progress(show=False)
        self.button_install_mod.grid(row=2, column=1, sticky="NEWS")
        self.listbox_outputformat.grid(row=2, column=2, sticky="NEWS")

    t = Thread(target=func)
    t.setDaemon(True)
    t.start()
