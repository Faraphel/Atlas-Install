from . import wszst
from .definition import *

from threading import Thread
from PIL import Image
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


class TooMuchDownloadFailed(Exception):
    def __init__(self):
        super().__init__("Too much download failed !")


class TooMuchSha1CheckFailed(Exception):
    def __init__(self):
        super().__init__("Too much sha1 check failed !")


class CantConvertTrack(Exception):
    def __init__(self):
        super().__init__("Can't convert track, check if download are enabled.")


def patch_img_desc(img_desc_path: str = "./file/img_desc", dest_dir: str = "./file"):
    il = Image.open(img_desc_path+"/illustration.png")
    il_16_9 = il.resize((832, 456))
    il_4_3 = il.resize((608, 456))

    for file_lang in glob.glob(img_desc_path+"??.png"):
        img_lang = Image.open(file_lang)
        img_lang_16_9 = img_lang.resize((832, 456))
        img_lang_4_3 = img_lang.resize((608, 456))

        new_16_9 = Image.new("RGBA", (832, 456), (0, 0, 0, 255))
        new_16_9.paste(il_16_9, (0, 0), il_16_9)
        new_16_9.paste(img_lang_16_9, (0, 0), img_lang_16_9)
        new_16_9.save(dest_dir+f"/strapA_16_9_832x456{get_filename(get_nodir(file_lang))}.png")

        new_4_3 = Image.new("RGBA", (608, 456), (0, 0, 0, 255))
        new_4_3.paste(il_4_3, (0, 0), il_4_3)
        new_4_3.paste(img_lang_4_3, (0, 0), img_lang_4_3)
        new_4_3.save(dest_dir+f"/strapA_608x456{get_filename(get_nodir(file_lang))}.png")


def patch_image(fc, gui):
    for i, file in enumerate(fc["img"]):
        gui.progress(statut=gui.translate("Converting images") + f"\n({i + 1}/{len(fc['img'])}) {file}", add=1)
        subprocess.run(["./tools/szs/wimgt", "ENCODE", "./file/" + file, "-x", fc["img"][file], "--overwrite"],
                       creationflags=CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)


def patch_bmg(gamefile: str, gui):  # gamefile est le fichier .szs trouvé dans le /files/Scene/UI/ du jeu
    NINTENDO_CWF_REPLACE = "Wiimmfi"
    MAINMENU_REPLACE = f"MKWFaraphel {gui.ctconfig.version}"
    menu_replacement = {
        "CWF de Nintendo": NINTENDO_CWF_REPLACE,
        "Wi-Fi Nintendo": NINTENDO_CWF_REPLACE,
        "CWF Nintendo": NINTENDO_CWF_REPLACE,
        "Nintendo WFC": NINTENDO_CWF_REPLACE,
        "Wi-Fi": NINTENDO_CWF_REPLACE,
        "インターネット": NINTENDO_CWF_REPLACE,

        "Menu principal": MAINMENU_REPLACE,
        "Menú principal": MAINMENU_REPLACE,
        "Main Menu": MAINMENU_REPLACE,
        "トップメニュー": MAINMENU_REPLACE,

        "Mario Kart Wii": MAINMENU_REPLACE,
    }

    bmglang = gamefile[-len("E.txt"):-len(".txt")]  # Langue du fichier
    gui.progress(statut=gui.translate("Patching text", " ", bmglang), add=1)

    subprocess.run(["./tools/szs/wszst", "EXTRACT", get_nodir(gamefile), "-d", get_nodir(gamefile) + ".d",
                    "--overwrite"], creationflags=CREATE_NO_WINDOW, cwd=get_dir(gamefile))

    # Menu.bmg
    bmgmenu = subprocess.run(["./tools/szs/wbmgt", "CAT", get_nodir(gamefile) + ".d/message/Menu.bmg"],
                             creationflags=CREATE_NO_WINDOW, cwd=get_dir(gamefile),
                             check=True, stdout=subprocess.PIPE).stdout.decode()

    # Common.bmg
    bmgtracks = subprocess.run(["./tools/szs/wbmgt", "CAT", get_nodir(gamefile) + ".d/message/Common.bmg"],
                               creationflags=CREATE_NO_WINDOW, cwd=get_dir(gamefile),
                               check=True, stdout=subprocess.PIPE).stdout.decode()
    trackheader = "#--- standard track names"
    trackend = "2328"
    bmgtracks = bmgtracks[bmgtracks.find(trackheader) + len(trackheader):bmgtracks.find(trackend)]

    with open("./file/ExtraCommon.txt", "w", encoding="utf8") as f:
        f.write("#BMG\n\n"
                f"  703e\t= \\\\c{{white}}{gui.translate('Random: All tracks', lang=bmglang)}\n"
                f"  703f\t= \\\\c{{white}}{gui.translate('Random: Original tracks', lang=bmglang)}\n"
                f"  7040\t= \\\\c{{white}}{gui.translate('Random: Custom Tracks', lang=bmglang)}\n"
                f"  7041\t= \\\\c{{white}}{gui.translate('Random: New tracks', lang=bmglang)}\n")

        for bmgtrack in bmgtracks.split("\n"):
            if "=" in bmgtrack:

                prefix = ""
                if "T" in bmgtrack[:bmgtrack.find("=")]:
                    sTid = bmgtrack.find("T")
                    Tid = bmgtrack[sTid:sTid + 3]
                    if Tid[1] in "1234":
                        prefix = trackname_color["Wii"] + " "  # Si la course est original à la wii
                    Tid = hex(bmgID_track_move[Tid])[2:]

                else:  # Arena
                    sTid = bmgtrack.find("U") + 1
                    Tid = bmgtrack[sTid:sTid + 2]
                    Tid = hex((int(Tid[0]) - 1) * 5 + (int(Tid[1]) - 1) + 0x7020)[2:]

                Tname = bmgtrack[bmgtrack.find("= ") + 2:]
                f.write(f"  {Tid}\t= {prefix}{Tname}\n")

    if not (os.path.exists("./file/tmp/")): os.makedirs("./file/tmp/")

    filecopy(gamefile + ".d/message/Common.bmg", "./file/tmp/Common.bmg")
    bmgcommon = subprocess.run(
        ["tools/szs/wctct", "bmg", "--le-code", "--long", "./file/CTFILE.txt", "--patch-bmg",
         "OVERWRITE=./file/tmp/Common.bmg", "--patch-bmg", "OVERWRITE=./file/ExtraCommon.txt"],
        creationflags=CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE).stdout.decode()
    rbmgcommon = subprocess.run(
        ["tools/szs/wctct", "bmg", "--le-code", "--long", "./file/RCTFILE.txt", "--patch-bmg",
         "OVERWRITE=./file/tmp/Common.bmg", "--patch-bmg", "OVERWRITE=./file/ExtraCommon.txt"],
        creationflags=CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE).stdout.decode()

    shutil.rmtree(gamefile + ".d")
    os.remove("./file/tmp/Common.bmg")
    os.remove("./file/ExtraCommon.txt")

    def finalise(file, bmgtext, replacement_list=None):
        if replacement_list:
            for text, colored_text in replacement_list.items(): bmgtext = bmgtext.replace(text, colored_text)
        with open(file, "w", encoding="utf-8") as f:
            f.write(bmgtext)
        subprocess.run(["./tools/szs/wbmgt", "ENCODE", get_nodir(file), "--overwrite"],
                       creationflags=CREATE_NO_WINDOW, cwd=get_dir(file))
        os.remove(file)

    finalise(f"./file/Menu_{bmglang}.txt", bmgmenu, menu_replacement)
    finalise(f"./file/Common_{bmglang}.txt", bmgcommon)
    finalise(f"./file/Common_R{bmglang}.txt", rbmgcommon)


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
                gui.progress(show=True, indeter=False, statut=gui.translate("Installing mod"), max=max_step, step=0)

                def replace_file(path, file, subpath="/"):
                    gui.progress(statut=gui.translate("Editing", "\n", get_nodir(path)), add=1)
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
                    gui.progress(statut=gui.translate("Recompilating", "\n", get_nodir(file)), add=1)
                    subprocess.run(["./tools/szs/wszst", "CREATE", get_nodir(file) + ".d", "-d", get_nodir(file),
                                    "--overwrite"], creationflags=CREATE_NO_WINDOW, cwd=get_dir(file),
                                   check=True, stdout=subprocess.PIPE)
                    if os.path.exists(file + ".d"): shutil.rmtree(file + ".d")

                gui.progress(statut=gui.translate("Patch main.dol"), add=1)
                subprocess.run(["./tools/szs/wstrt", "patch", get_nodir(self.path) + "/sys/main.dol", "--clean-dol",
                                "--add-lecode"], creationflags=CREATE_NO_WINDOW, cwd=get_dir(self.path),
                               check=True, stdout=subprocess.PIPE)

                gui.progress(statut=gui.translate("Patch lecode.bin"), add=1)

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
                gui.progress(statut=gui.translate("Converting to", " ", output_format), add=1)

                if output_format in ["ISO", "WBFS", "CISO"]:
                    path_game_format: str = os.path.realpath(self.path + "/../MKWFaraphel." + output_format.lower())
                    subprocess.run(["./tools/wit/wit", "COPY", get_nodir(self.path), "--DEST",
                                   get_nodir(path_game_format), f"--{output_format.lower()}", "--overwrite"],
                                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(path_game_format),
                                   check=True, stdout=subprocess.PIPE)
                    shutil.rmtree(self.path)
                    self.path = path_game_format

                    gui.progress(statut=gui.translate("Changing game's ID"), add=1)
                    subprocess.run(["./tools/wit/wit", "EDIT", get_nodir(self.path), "--id",
                                    f"RMC{self.region_ID}60", "--name",
                                    f"Mario Kart Wii Faraphel {gui.ctconfig.version}", "--modify", "ALL"],
                                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(self.path),
                                   check=True, stdout=subprocess.PIPE)

                # messagebox.showinfo(gui.translate("End"), gui.translate("The mod has been installed !"))

            except: gui.log_error()
            finally: gui.progress(show=False)

        t = Thread(target=func)
        t.setDaemon(True)
        t.start()
        return t

    def convert_to(self, format: str = "FST"):
        """
        :param format: game format (ISO, WBFS, ...)
        :return: converted game path
        """

    def patch_file(self, gui):
        def func():
            try:
                if not (os.path.exists("./file/Track-WU8/")): os.makedirs("./file/Track-WU8/")
                with open("./convert_file.json") as f:
                    fc = json.load(f)
                max_step = len(fc["img"]) + len(gui.ctconfig.all_tracks) + 3 + len("EGFIS")

                gui.progress(show=True, indeter=False, statut=gui.translate("Converting files"), max=max_step, step=0)
                gui.progress(statut=gui.translate("Configurating LE-CODE"), add=1)
                gui.ctconfig.create_ctfile()

                gui.progress(statut=gui.translate("Creating ct_icon.png"), add=1)
                ct_icon = gui.ctconfig.get_cticon()
                ct_icon.save("./file/ct_icons.tpl.png")

                gui.progress(statut=gui.translate("Creating descriptive images"), add=1)
                patch_img_desc()
                patch_image(fc, gui)
                for file in glob.glob(self.path + "/files/Scene/UI/MenuSingle_?.szs"): patch_bmg(file, gui)
                # MenuSingle could be any other file, Common and Menu are all the same in all other files.
                self.patch_autoadd()
                if patch_track(gui) != 0: return

                gui.button_install_mod.grid(row=2, column=1, columnspan=2, sticky="NEWS")
                gui.button_install_mod.config(
                    text=gui.translate("Install mod", " (v", gui.ctconfig.version, ")"))

            except: gui.log_error()
            finally: gui.progress(show=False)

        t = Thread(target=func)
        t.setDaemon(True)
        t.start()
        return t
