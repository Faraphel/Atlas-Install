from .definition import *
from tkinter import messagebox
import subprocess
import shutil
import json
import os


def get_trackname(self, track, color=False):
    hl_prefix, hl_suffix = "", ""
    if color:
        if track.get("since_version") == self.stringvar_mark_track_from_version.get():
            hl_prefix, hl_suffix = "\\\\c{blue1}", "\\\\c{off}"

    name = track["name"]
    name = hl_prefix + name + hl_suffix

    if "prefix" in track:
        prefix = track["prefix"]
        if color:
            if prefix in trackname_color:
                prefix = trackname_color[prefix]
        name = prefix + " " + name
    if "suffix" in track:
        suffix = track["suffix"]
        if color:
            if suffix in trackname_color:
                suffix = trackname_color[suffix]
        name = name + " (" + suffix + ")"

    return name


def get_trackctname(self, *args, **kwargs):
    return self.get_trackname(*args, **kwargs).replace("_", "")


def load_ct_config(self):
    tracks = []
    with open("./ct_config.json", encoding="utf-8") as f: ctconfig = json.load(f)

    for cup in ctconfig["cup"].values():  # defined order tracks
        if not (cup["locked"]): tracks.extend(cup["courses"].values())

    tracks.extend(ctconfig["tracks_list"])  # unordered tracks

    self.TRACKS = [dict(t) for t in {tuple(d.items()) for d in tracks}]  # removing duplicate
    self.TOTAL_TRACK = len(tracks)

    self.VERSION = ctconfig["version"]

    self.ALL_VERSION = []
    for track in self.TRACKS:
        if not track.get("since_version") in self.ALL_VERSION:
            self.ALL_VERSION.append(track["since_version"])
    self.ALL_VERSION.sort()


def patch_autoadd(self):
    if os.path.exists("./file/auto-add"): shutil.rmtree("./file/auto-add")
    if not os.path.exists(self.path_mkwf + "/tmp/"): os.makedirs(self.path_mkwf + "/tmp/")
    subprocess.run(["./tools/szs/wszst", "AUTOADD", get_nodir(self.path_mkwf) + "/files/Race/Course/",
                    "--DEST", get_nodir(self.path_mkwf) + "/tmp/auto-add/"],
                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(self.path_mkwf),
                   check=True, stdout=subprocess.PIPE)
    shutil.move(self.path_mkwf + "/tmp/auto-add/", "./file/auto-add/")
    shutil.rmtree(self.path_mkwf + "/tmp/")


def patch_track(self):
    max_process = self.intvar_process_track.get()
    process_list = {}
    error_count, error_max = 0, 3

    def add_process(track):
        track_file = self.get_trackname(track=track)
        nonlocal error_count, error_max, process_list

        process_list[track_file] = None  # Used for
        self.Progress(statut=self.translate("Converting tracks", f"\n({i + 1}/{self.TOTAL_TRACK})\n",
                      "\n".join(process_list.keys())), add=1)

        for _track in [get_track_szs(track_file), get_track_wu8(track_file)]:
            if os.path.exists(_track):
                if os.path.getsize(_track) < 1000:  # File under this size are corrupted
                    os.remove(_track)

        while True:
            download_returncode = self.get_github_file(get_track_wu8(track_file))
            if download_returncode == -1:  # can't download
                error_count += 1
                if error_count > error_max:  # Too much track wasn't correctly converted
                    messagebox.showerror(
                        self.translate("Error"),
                        self.translate("Too much tracks had a download issue."))
                    return -1
                else:
                    messagebox.showwarning(self.translate("Warning"),
                                           self.translate("Can't download this track !",
                                                          f" ({error_count} / {error_max})"))
            elif download_returncode == 2: break  # if download is disabled, don't check sha1

            if "sha1" in track:
                if not self.boolvar_dont_check_track_sha1.get():
                    if not self.check_track_sha1(get_track_wu8(track_file), track["sha1"]) == 0:  # La course est correcte
                        error_count += 1
                        if error_count > error_max:  # Too much track wasn't correctly converted
                            messagebox.showerror(
                                self.translate("Error"),
                                self.translate("Too much tracks had an issue during sha1 check."))
                            return -1
                        continue

            break

        if not (os.path.exists(
                get_track_szs(track_file))) or download_returncode == 3:  # returncode 3 is track has been updated
            if os.path.exists(get_track_wu8(track_file)):
                process_list[track_file] = subprocess.Popen([
                    "./tools/szs/wszst", "NORMALIZE", get_track_wu8(track_file), "--DEST",
                    "./file/Track/%N.szs", "--szs", "--overwrite", "--autoadd-path",
                    "./file/auto-add/"], creationflags=CREATE_NO_WINDOW, stderr=subprocess.PIPE)
            else:
                messagebox.showerror(self.translate("Error"),
                                     self.translate("Can't convert track.\nEnable track download and retry."))
                return -1
        elif self.boolvar_del_track_after_conv.get(): os.remove(get_track_wu8(track_file))
        return 0

    def clean_process():
        nonlocal error_count, error_max, process_list

        for track_file, process in process_list.copy().items():
            if process is not None:
                if process.poll() is None:
                    pass  # if the process is still running
                else:  # process ended
                    process_list.pop(track_file)
                    stderr = process.stderr.read()
                    if b"wszst: ERROR" in stderr:  # Error occured
                        os.remove(get_track_szs(track_file))
                        error_count += 1
                        if error_count > error_max:  # Too much track wasn't correctly converted
                            messagebox.showerror(
                                self.translate("Error"),
                                self.translate("Too much track had a conversion issue."))
                            return -1
                        else:  # if the error max hasn't been reach
                            messagebox.showwarning(
                                self.translate("Warning"),
                                self.translate("The track", " ", get_track_wu8(track_file),
                                               "do not have been properly converted.",
                                               f" ({error_count} / {error_max})"))
                    else:
                        if self.boolvar_del_track_after_conv.get(): os.remove(get_track_wu8(track_file))
            else:
                process_list.pop(track_file)
                if not(any(process_list.values())): return 1  # si il n'y a plus de processus

        if len(process_list): return 1
        else: return 0

    for i, track in enumerate(self.TRACKS):
        while True:
            if len(process_list) < max_process:
                returncode = add_process(track)
                if returncode == 0: break
                elif returncode == -1: return -1  # if error occur, stop function
            elif clean_process() == -1: return -1

    while True:
        returncode = clean_process()
        if returncode == 1: break  # End the process if all process ended
        elif returncode == 0: pass
        else: return -1

    return 0