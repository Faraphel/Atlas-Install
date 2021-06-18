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
    tracks = [dict(t) for t in {tuple(d.items()) for d in tracks}]
    total_track = len(tracks)
    return tracks, total_track


def patch_autoadd(self):
    if os.path.exists("./file/auto-add"): shutil.rmtree("./file/auto-add")
    if not os.path.exists(self.path_mkwf + "/tmp/"): os.makedirs(self.path_mkwf + "/tmp/")
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
        track_file = get_trackname(track=track)
        while True:
            if len(process_list) < max_process:
                process_list[track_file] = None  # Used for
                self.Progress(statut=self.translate("Conversion des courses") + f"\n({i + 1}/{total_track})\n" +
                              "\n".join(process_list.keys()), add=1)

                for _track in [get_track_szs(track_file), get_track_wu8(track_file)]:
                    if os.path.exists(_track):
                        if os.path.getsize(_track) < 1000:  # File under this size are corrupted
                            os.remove(_track)

                download_returncode = self.get_github_file(get_track_wu8(track_file))
                if download_returncode == -1:  # can't download
                    error_count += 1
                    if error_count > error_max:  # Too much track wasn't correctly converted
                        messagebox.showerror(
                            self.translate("Erreur"),
                            self.translate("Trop de course ont eu une erreur du téléchargement."))
                        return -1
                    else:
                        messagebox.showwarning(self.translate("Attention"),
                                               self.translate("Impossible de télécharger cette course ! (") +
                                               str(error_count) + "/" + str(error_max) + ")")

                if not (os.path.exists(get_track_szs(track_file))) or download_returncode == 3:  # returncode 3 is track has been updated
                    if os.path.exists(get_track_wu8(track_file)):
                        process_list[track_file] = subprocess.Popen([
                            "./tools/szs/wszst", "NORMALIZE", get_track_wu8(track_file), "--DEST",
                            "./file/Track/%N.szs", "--szs", "--overwrite", "--autoadd-path",
                            "./file/auto-add/"], creationflags=CREATE_NO_WINDOW, stderr=subprocess.PIPE)
                    else:
                        messagebox.showerror(self.translate("Erreur"),
                                             self.translate("Impossible de convertir la course.\n"
                                                            "Réactiver le téléchargement des courses et réessayer."))
                        return -1
                elif self.boolvar_del_track_after_conv.get(): os.remove(get_track_wu8(track_file))
                break
            else:
                for _track_file, process in process_list.items():
                    if process is not None:
                        if process.poll() is None: pass  # if the process is still running
                        else:  # process ended
                            process_list.pop(_track_file)
                            stderr = process.stderr.read()
                            if b"wszst: ERROR" in stderr:  # Error occured
                                os.remove(get_track_szs(_track_file))
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
                                        get_track_wu8(_track_file) +
                                        self.translate(" n'a pas été correctement converti. (") +
                                        str(error_count) + "/" + str(error_max) + ")")
                                    break

                            else:
                                if self.boolvar_del_track_after_conv.get(): os.remove(get_track_wu8(_track_file))
                                break
                    else:
                        process_list.pop(_track_file)
                        break
    return 0