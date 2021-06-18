from .definition import *
from tkinter import messagebox
import subprocess
import shutil
import json
import os


def count_track(self):
    tracks = []
    with open("./ct_config.json", encoding="utf-8") as f:
        ctconfig = json.load(f)
    for cup in ctconfig["cup"].values():
        if not (cup["locked"]): tracks.extend(cup["courses"].values())
    tracks.extend(ctconfig["tracks_list"])
    total_track = len(tracks)
    return tracks, total_track


def patch_autoadd(self):
    if os.path.exists("./file/auto-add"): shutil.rmtree("./file/auto-add")
    if not (os.path.exists(self.path_mkwf + "/tmp/")): os.makedirs(self.path_mkwf + "/tmp/")
    subprocess.run(["./tools/szs/wszst", "AUTOADD", get_nodir(self.path_mkwf) + "/files/Race/Course/",
                    "--DEST", get_nodir(self.path_mkwf) + "/tmp/auto-add/"],
                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(self.path_mkwf),
                   check=True, stdout=subprocess.PIPE)
    shutil.move(self.path_mkwf + "/tmp/auto-add/", "./file/auto-add/")
    shutil.rmtree(self.path_mkwf + "/tmp/")


def patch_track(self, tracks, total_track="?"):
    max_process = self.intvar_process_track.get()
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
                process_list[(track_szs_file, track_wu8_file)] = None
                self.Progress(statut=self.translate("Conversion des courses") + f"\n({i + 1}/{total_track})\n" +
                              "\n".join([get_nodir(process[0]) for process in process_list]), add=1)

                for track_file in [track_szs_file, track_wu8_file]:
                    if os.path.exists(track_file):
                        if os.path.getsize(track_file) < 1000:  # File under this size are corrupted
                            os.remove(track_file)

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
                                               self.translate("Impossible de télécharger cette course ! (") +
                                               str(error_count) + "/" + str(error_max) + ")")

                if not (os.path.exists(track_szs_file)):
                    process_list[(track_szs_file, track_wu8_file)] = subprocess.Popen([
                        "./tools/szs/wszst", "NORMALIZE", track_wu8_file, "--DEST",
                        "./file/Track/%N.szs", "--szs", "--overwrite", "--autoadd-path",
                        "./file/auto-add/"], creationflags=CREATE_NO_WINDOW, stderr=subprocess.PIPE)
                break
            else:
                for (track_szs_file, track_wu8_file), process in process_list.items():
                    key = (track_szs_file, track_wu8_file)
                    if process is not None:
                        returncode = process.poll()
                        if returncode is None:
                            pass  # if the process is still running
                        else:  # process ended
                            stderr = process.stderr.read()
                            if b"wszst: ERROR" in stderr:  # Error occured
                                process_list.pop(key)
                                os.remove(track_szs_file)
                                error_count += 1
                                if error_count > error_max:  # Too much track wasn't correctly converted
                                    messagebox.showerror(
                                        self.translate("Erreur"),
                                        self.translate("Trop de course ont eu une erreur de conversion."))
                                    return
                                else:  # if the error max hasn't been reach
                                    messagebox.showwarning(
                                        self.translate("Attention"),
                                        self.translate("La course ") +
                                        track_wu8_file +
                                        self.translate(" n'a pas été correctement converti. (") +
                                        str(error_count) + "/" + str(error_max) + ")")
                                    break

                            else:
                                if self.boolvar_del_track_after_conv.get(): os.remove(track_wu8_file)
                                process_list.pop(key)
                                break
                    else:
                        process_list.pop(key)
                        break
