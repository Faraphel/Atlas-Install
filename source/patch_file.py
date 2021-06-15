from threading import Thread
import subprocess
import json
import glob
import os

from .definition import *


def patch_file(self):
    def func():
        try:
            if os.path.exists("./file/Track-WU8/"):
                total_track = len(os.listdir("./file/Track-WU8/"))
            else:
                total_track = 0
            with open("./convert_file.json") as f:
                fc = json.load(f)
            max_step = len(fc["img"]) + total_track + 3 + len("EGFIS")
            self.Progress(show=True, indeter=False, statut=self.translate("Conversion des fichiers"), max=max_step, step=0)

            self.Progress(statut=self.translate("Configuration de LE-CODE"), add=1)
            self.create_lecode_config()

            self.Progress(statut=self.translate("Création de ct_icon.png"), add=1)
            self.patch_ct_icon()

            self.Progress(statut=self.translate("Création des images descriptives"), add=1)
            self.patch_img_desc()

            for i, file in enumerate(fc["img"]):
                self.Progress(statut=self.translate("Conversion des images")+f"\n({i + 1}/{len(fc['img'])}) {file}", add=1)
                subprocess.run(["./tools/szs/wimgt", "ENCODE", "./file/" + file, "-x", fc["img"][file], "--overwrite"],
                               creationflags=CREATE_NO_WINDOW)

            for file in glob.glob(self.path_mkwf+"/files/Scene/UI/MenuSingle_?.szs"):
                self.patch_bmg(file)

            if not(os.path.exists("./file/auto-add/")):
                subprocess.run(["./tools/szs/wszst", "AUTOADD", self.path_mkwf + "/files/Race/Course/", "--DEST",
                               "./file/auto-add/"], creationflags=CREATE_NO_WINDOW)

            max_process = 8
            process_list = {}

            for i, file in enumerate(os.listdir("./file/Track-WU8/")):
                while True:
                    if len(process_list) < max_process:
                        process_list[file] = None
                        self.Progress(statut=self.translate("Conversion des courses")+f"\n({i + 1}/{total_track})\n" +
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

            self.Progress(show=False)
            self.button_install_mod.grid(row=2, column=1, sticky="NEWS")
            self.listbox_outputformat.grid(row=2, column=2, sticky="NEWS")

        except:
            self.log_error()

    t = Thread(target=func)
    t.setDaemon(True)
    t.start()
    return t
