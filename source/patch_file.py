from tkinter import messagebox
from threading import Thread
import subprocess
import shutil
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

            tracks = []
            with open("./ct_config.json", encoding="utf-8") as f:
                ctconfig = json.load(f)
            for cup in ctconfig["cup"].values():
                if not (cup["locked"]): tracks.extend(cup["courses"].values())
            tracks.extend(ctconfig["tracks_list"])
            total_track = len(tracks)

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
                               creationflags=CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)

            for file in glob.glob(self.path_mkwf+"/files/Scene/UI/MenuSingle_?.szs"):
                self.patch_bmg(file)

            if os.path.exists("./file/auto-add"): shutil.rmtree("./file/auto-add")
            if not(os.path.exists(self.path_mkwf + "/tmp/")): os.makedirs(self.path_mkwf + "/tmp/")
            subprocess.run(["./tools/szs/wszst", "AUTOADD", get_nodir(self.path_mkwf) + "/files/Race/Course/",
                           "--DEST", get_nodir(self.path_mkwf) + "/tmp/auto-add/"],
                           creationflags=CREATE_NO_WINDOW, cwd=get_dir(self.path_mkwf),
                           check=True, stdout=subprocess.PIPE)
            shutil.move(self.path_mkwf + "/tmp/auto-add/", "./file/auto-add/")
            shutil.rmtree(self.path_mkwf + "/tmp/")

            max_process = 8
            process_list = {}
            error_count, error_max = 0, 3

            for i, track in enumerate(tracks):
                track_file = track["name"]
                if "prefix" in track: track_file = track["prefix"] + " " + track_file
                if "suffix" in track: track_file = track_file + " (" + track["suffix"] + ")"
                track_wu8_file = f"./file/Track-WU8/{track_file}.wu8"
                track_szs_file = f"./file/Track/{track_file}.szs"

                while True:
                    if len(process_list) < max_process:
                        process_list[track_szs_file] = None
                        self.Progress(statut=self.translate("Conversion des courses")+f"\n({i + 1}/{total_track})\n" +
                                             "\n".join([get_nodir(file) for file in process_list.keys()]), add=1)

                        if not(os.path.exists(track_wu8_file)):
                            dl_code = self.get_github_file(track_wu8_file)
                            if dl_code == -1:
                                error_count += 1
                                if error_count > error_max:  # Too much track wasn't correctly converted
                                    messagebox.showerror(
                                        self.translate("Erreur"),
                                        self.translate("Trop de course ont eu une erreur du téléchargement."))
                                    return
                                else:
                                    messagebox.showwarning(self.translate("Attention"),
                                                           self.translate(
                                                               "Impossible de télécharger cette course ! (") +
                                                           str(error_count) + "/" + str(error_max) + ")")

                        if os.path.exists(track_szs_file):
                            if os.path.getsize(track_szs_file) < 1000:  # File under this size are corrupted
                                os.remove(track_szs_file)

                        if not(os.path.exists(track_szs_file)):
                            process_list[track_szs_file] = subprocess.Popen([
                                "./tools/szs/wszst", "NORMALIZE", track_wu8_file, "--DEST",
                                "./file/Track/%N.szs", "--szs", "--overwrite", "--autoadd-path",
                                "./file/auto-add/"], creationflags=CREATE_NO_WINDOW, stderr=subprocess.PIPE)
                        break
                    else:
                        for process in process_list:
                            if process_list[process] is not None:
                                returncode = process_list[process].poll()
                                if returncode is None: pass  # if the process is still running
                                else: # process ended
                                    stderr = process_list[process].stderr.read()
                                    if b"wszst: ERROR" in stderr:  # Error occured
                                        process_list.pop(process)
                                        print(process, stderr)
                                        os.remove(process)
                                        error_count += 1
                                        if error_count > error_max:  # Too much track wasn't correctly converted
                                            messagebox.showerror(
                                                self.translate("Erreur"),
                                                self.translate("Trop de course ont eu une erreur de conversion."))
                                            return
                                        else: # if the error max hasn't been reach
                                            messagebox.showwarning(
                                                self.translate("Attention"),
                                                self.translate("La course ") +
                                                process +
                                                self.translate(" n'a pas été correctement converti. (") +
                                                str(error_count) + "/"+str(error_max)+")")
                                            break

                                    else:
                                        process_list.pop(process)
                                        break
                            else:
                                process_list.pop(process)
                                break

            self.button_install_mod.grid(row=2, column=1, sticky="NEWS")
            self.listbox_outputformat.grid(row=2, column=2, sticky="NEWS")

        except: self.log_error()
        finally: self.Progress(show=False)


    t = Thread(target=func)
    t.setDaemon(True)
    t.start()
    return t
