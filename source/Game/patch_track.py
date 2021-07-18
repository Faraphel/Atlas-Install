import os

from .exception import *


def patch_track(gui):
    max_process = gui.intvar_process_track.get()
    process_list = {}
    error_count, error_max = 0, 3

    def add_process(track):
        nonlocal error_count, error_max, process_list
        track_file = track.get_track_name()
        total_track = len(gui.ctconfig.all_tracks)

        process_list[track_file] = None  # Used for showing track in progress even if there's no process
        gui.progress(statut=gui.translate("Converting tracks", f"\n({i + 1}/{total_track})\n",
                                         "\n".join(process_list.keys())), add=1)

        for _track in [track.file_szs, track.file_wu8]:
            if os.path.exists(_track):
                if os.path.getsize(_track) < 1000:  # File under this size are corrupted
                    os.remove(_track)

        if not gui.boolvar_disable_download.get():
            while True:
                download_returncode = track.download_wu8()
                if download_returncode == -1:  # can't download
                    error_count += 1
                    if error_count > error_max:  # Too much track wasn't correctly converted
                        """messagebox.showerror(
                            gui.translate("Error"),
                            gui.translate("Too much tracks had a download issue."))
                        return -1"""
                        raise TooMuchDownloadFailed()
                    else:
                        """messagebox.showwarning(gui.translate("Warning"),
                                               gui.translate("Can't download this track !",
                                                              f" ({error_count} / {error_max})"))"""
                elif download_returncode == 2:
                    break  # if download is disabled, do not check sha1

                if track.sha1:
                    if not gui.boolvar_dont_check_track_sha1.get():
                        if not track.check_sha1():  # Check si le sha1 du fichier est le bon
                            error_count += 1
                            if error_count > error_max:  # Too much track wasn't correctly converted
                                """messagebox.showerror(
                                    gui.translate("Error"),
                                    gui.translate("Too much tracks had an issue during sha1 check."))"""
                                raise TooMuchSha1CheckFailed()
                            continue

                break

            if not (
            os.path.exists(track.file_szs)) or download_returncode == 3:  # returncode 3 is track has been updated
                if os.path.exists(track.file_wu8):
                    process_list[track_file] = track.convert_wu8_to_szs()
                else:
                    """messagebox.showerror(gui.translate("Error"),
                           gui.translate("Can't convert track.\nEnable track download and retry."))"""
                    raise CantConvertTrack()
            elif gui.boolvar_del_track_after_conv.get():
                os.remove(track.file_wu8)
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
                        os.remove(track.file_szs)
                        error_count += 1
                        if error_count > error_max:  # Too much track wasn't correctly converted
                            """messagebox.showerror(
                                gui.translate("Error"),
                                gui.translate("Too much track had a conversion issue."))"""
                            raise CantConvertTrack
                        else:  # if the error max hasn't been reach
                            """messagebox.showwarning(
                                gui.translate("Warning"),
                                gui.translate("The track", " ", track.file_wu8,
                                               "do not have been properly converted.",
                                               f" ({error_count} / {error_max})"))"""
                    else:
                        if gui.boolvar_del_track_after_conv.get(): os.remove(track.file_wu8)
            else:
                process_list.pop(track_file)
                if not (any(process_list.values())): return 1  # si il n'y a plus de processus

        if len(process_list):
            return 1
        else:
            return 0

    for i, track in enumerate(gui.ctconfig.all_tracks):
        while True:
            if len(process_list) < max_process:
                returncode = add_process(track)
                if returncode == 0:
                    break
                elif returncode == -1:
                    return -1  # if error occur, stop function
            elif clean_process() == -1:
                return -1

    while True:
        returncode = clean_process()
        if returncode == 1:
            break  # End the process if all process ended
        elif returncode == 0:
            pass
        else:
            return -1

    return 0