from tkinter import messagebox
from PIL import Image
import shutil
import glob
import json

from .CT_Config import CT_Config
from .definition import *
from .wszst import *


class RomAlreadyPatched(Exception):
    def __init__(self):
        super().__init__("ROM Already patched !")


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


class NoGui:
    """
    'fake' gui if no gui are used for compatibility.
    """
    class NoButton:
        def grid(self, *args, **kwargs): pass
        def config(self, *args, **kwargs): pass

    class NoVariable:
        def __init__(self, value=None):
            self.value = None

        def set(self, value):
            self.value = value

        def get(self):
            return self.value

    def progress(*args, **kwargs): print(args, kwargs)
    def translate(*args, **kwargs): return ""
    def log_error(*args, **kwargs): print(args, kwargs)

    is_dev_version = False
    button_install_mod = NoButton()
    stringvar_game_format = NoVariable()
    boolvar_disable_download = NoVariable()
    intvar_process_track = NoVariable()
    boolvar_dont_check_track_sha1 = NoVariable()
    boolvar_del_track_after_conv = NoVariable()


class Game:
    def __init__(self, path: str = "", region_ID: str = "P", game_ID: str = "RMCP01", gui=None):
        """
        Class about the game code and its treatment.
        :param path: path of the game file / directory
        :param region_ID: game's region id (P for PAL, K for KOR, ...)
        :param game_ID: game's id (RMCP01 for PAL, ...)
        :param gui: gui class used by the program
        """
        if not os.path.exists(path) and path: raise InvalidGamePath()
        self.extension = None
        self.path = path
        self.set_path(path)
        self.region = region_id_to_name[region_ID]
        self.region_ID = region_ID
        self.game_ID = game_ID
        self.gui = gui if gui else NoGui
        self.ctconfig = CT_Config(gui=gui)

    def set_path(self, path: str) -> None:
        """
        Change game path
        :param path: game's file
        """
        self.extension = get_extension(path).upper()
        self.path = path

    def convert_to(self, format: str = "FST") -> None:
        """
        Convert game to an another format
        :param format: game format (ISO, WBFS, ...)
        """
        if format in ["ISO", "WBFS", "CISO"]:
            path_game_format: str = os.path.realpath(self.path + "/../MKWFaraphel." + format.lower())
            wit.copy(self.path, path_game_format, format)
            shutil.rmtree(self.path)
            self.path = path_game_format

            self.gui.progress(statut=self.gui.translate("Changing game's ID"), add=1)
            wit.edit(self.path, region_ID=self.region_ID, name=f"Mario Kart Wii Faraphel {self.ctconfig.version}")

    def extract(self) -> None:
        """
        Extract game file in the same directory.
        """
        if self.extension == "DOL":
            self.path = os.path.realpath(self.path + "/../../")  # main.dol is in PATH/sys/, so go back 2 dir upper

        elif self.extension in ["ISO", "WBFS", "CSIO"]:
            # Fiding a directory name that doesn't already exist
            directory_name, i = "MKWiiFaraphel", 1
            while True:
                path_dir = os.path.realpath(self.path + f"/../{directory_name}")
                if not (os.path.exists(path_dir)): break
                directory_name, i = f"MKWiiFaraphel ({i})", i + 1

            wit.extract(self.path, path_dir)

            self.path = path_dir
            if os.path.exists(self.path + "/DATA"): self.path += "/DATA"
            self.extension = "DOL"

        else:
            raise InvalidFormat()

        if glob.glob(self.path + "/files/rel/lecode-???.bin"):  # if a LECODE file is already here
            raise RomAlreadyPatched()  # warning already patched

        with open(self.path + "/setup.txt") as f:
            setup = f.read()
        setup = setup[setup.find("!part-id = ") + len("!part-id = "):]
        self.game_ID = setup[:setup.find("\n")]

        self.region_ID = self.game_ID[3]
        self.region = region_id_to_name[self.region_ID] if self.region_ID in region_id_to_name else self.region

    @in_thread
    def install_mod(self):
        """
        Patch the game to install the mod
        """
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
            self.gui.progress(show=True, indeter=False, statut=self.gui.translate("Installing mod"), max=max_step,
                             step=0)

            def replace_file(path, file, subpath="/") -> None:
                """
                Replace subfile in the .szs file
                :param path: path to the .szs file
                :param file: file to replace
                :param subpath: directory between .szs file and file inside to replace
                """
                self.gui.progress(statut=self.gui.translate("Editing", "\n", get_nodir(path)), add=1)
                extension = get_extension(path)

                if extension == "szs":
                    if not (os.path.realpath(path) in extracted_file):
                        szs.extract(path, get_nodir(path))
                        extracted_file.append(os.path.realpath(path))

                    szs_extract_path = path + ".d"
                    if os.path.exists(szs_extract_path + subpath):
                        if subpath[-1] == "/":
                            shutil.copyfile(f"./file/{file}", szs_extract_path + subpath + file)
                        else:
                            shutil.copyfile(f"./file/{file}", szs_extract_path + subpath)

                elif path[-1] == "/":
                    shutil.copyfile(f"./file/{file}", path + file)
                else:
                    shutil.copyfile(f"./file/{file}", path)

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
                self.gui.progress(statut=self.gui.translate("Recompilating", "\n", get_nodir(file)), add=1)
                szs.create(file)
                if os.path.exists(file + ".d"):
                    shutil.rmtree(file + ".d")

            self.gui.progress(statut=self.gui.translate("Patch main.dol"), add=1)
            wstrt.patch(self.path)

            self.gui.progress(statut=self.gui.translate("Patch lecode.bin"), add=1)

            shutil.copytree("./file/Track/", self.path + "/files/Race/Course/", dirs_exist_ok=True)
            if not (os.path.exists(self.path + "/tmp/")): os.makedirs(self.path + "/tmp/")
            shutil.copyfile("./file/CTFILE.txt", self.path + "/tmp/CTFILE.txt")
            shutil.copyfile("./file/lpar-default.txt", self.path + "/tmp/lpar-default.txt")
            shutil.copyfile(f"./file/lecode-{self.region}.bin", self.path + f"/tmp/lecode-{self.region}.bin")

            lec.patch(
                self.path,
                lecode_file=f"./tmp/lecode-{self.region}.bin",
                dest_lecode_file=f"./files/rel/lecode-{self.region}.bin",
            )

            shutil.rmtree(self.path + "/tmp/")

            output_format = self.gui.stringvar_game_format.get()
            self.gui.progress(statut=self.gui.translate("Converting to", " ", output_format), add=1)
            self.convert_to(output_format)

            messagebox.showinfo(self.gui.translate("End"), self.gui.translate("The mod has been installed !"))

        except:
            self.gui.log_error()
        finally:
            self.gui.progress(show=False)

    def patch_autoadd(self, auto_add_dir: str = "./file/auto-add") -> None:
        """
        Create the autoadd directory used to convert wbz track into szs
        :param auto_add_dir: autoadd directory
        """
        if os.path.exists(auto_add_dir): shutil.rmtree(auto_add_dir)
        szs.autoadd(self.path, auto_add_dir)

    def patch_bmg(self, gamefile: str) -> None:
        """
        Patch bmg file (text file)
        :param gamefile: an .szs file where file will be patched
        """
        NINTENDO_CWF_REPLACE = "Wiimmfi"
        MAINMENU_REPLACE = f"MKWFaraphel {self.ctconfig.version}"
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
        self.gui.progress(statut=self.gui.translate("Patching text", " ", bmglang), add=1)

        szs.extract(file=gamefile)

        bmgmenu = bmg.cat(gamefile, ".d/message/Menu.bmg")  # Menu.bmg
        bmgtracks = bmg.cat(gamefile, ".d/message/Common.bmg")  # Common.bmg

        trackheader = "#--- standard track names"
        trackend = "2328"
        bmgtracks = bmgtracks[bmgtracks.find(trackheader) + len(trackheader):bmgtracks.find(trackend)]

        with open("./file/ExtraCommon.txt", "w", encoding="utf8") as f:
            f.write("#BMG\n\n"
                    f"  703e\t= \\\\c{{white}}{self.gui.translate('Random: All tracks', lang=bmglang)}\n"
                    f"  703f\t= \\\\c{{white}}{self.gui.translate('Random: Original tracks', lang=bmglang)}\n"
                    f"  7040\t= \\\\c{{white}}{self.gui.translate('Random: Custom Tracks', lang=bmglang)}\n"
                    f"  7041\t= \\\\c{{white}}{self.gui.translate('Random: New tracks', lang=bmglang)}\n")

            for bmgtrack in bmgtracks.split("\n"):
                if "=" in bmgtrack:

                    prefix = ""
                    track_name = bmgtrack[bmgtrack.find("= ") + 2:]

                    if "T" in bmgtrack[:bmgtrack.find("=")]:
                        start_track_id: int = bmgtrack.find("T")  # index where the bmg track definition start
                        track_id = bmgtrack[start_track_id:start_track_id + 3]
                        if track_id[1] in "1234":  # if the track is a original track from the wii
                            prefix = trackname_color["Wii"] + " "
                        elif track_id[1] in "5678":  # if the track is a retro track from the original game
                            for color_prefix, rep_color_prefix in trackname_color.items():  # color retro track prefix
                                track_name = track_name.replace(color_prefix, rep_color_prefix)
                        track_id = hex(bmgID_track_move[track_id])[2:]
                    else:  # Arena
                        start_track_id = bmgtrack.find("U") + 1  # index where the bmg arena definition start
                        track_id = bmgtrack[start_track_id:start_track_id + 2]
                        track_id = hex((int(track_id[0]) - 1) * 5 + (int(track_id[1]) - 1) + 0x7020)[2:]

                    f.write(f"  {track_id}\t= {prefix}{track_name}\n")

        bmgcommon = ctc.patch_bmg(ctfile="./file/CTFILE.txt",
                                        bmgs=[gamefile + ".d/message/Common.bmg", "./file/ExtraCommon.txt"])
        rbmgcommon = ctc.patch_bmg(ctfile="./file/RCTFILE.txt",
                                         bmgs=[gamefile + ".d/message/Common.bmg", "./file/ExtraCommon.txt"])

        shutil.rmtree(gamefile + ".d")
        os.remove("./file/ExtraCommon.txt")

        def finalise(file, bmgtext, replacement_list=None):
            if replacement_list:
                for text, colored_text in replacement_list.items(): bmgtext = bmgtext.replace(text, colored_text)
            with open(file, "w", encoding="utf-8") as f:
                f.write(bmgtext)
            bmg.encode(file)
            os.remove(file)

        finalise(f"./file/Menu_{bmglang}.txt", bmgmenu, menu_replacement)
        finalise(f"./file/Common_{bmglang}.txt", bmgcommon)
        finalise(f"./file/Common_R{bmglang}.txt", rbmgcommon)

    @in_thread
    def patch_file(self):
        """
        Prepare all files to install the mod (track, bmg text, descriptive image, ...)
        """
        try:
            if not (os.path.exists("./file/Track-WU8/")): os.makedirs("./file/Track-WU8/")
            with open("./convert_file.json") as f:
                fc = json.load(f)
            max_step = len(fc["img"]) + len(self.ctconfig.all_tracks) + 3 + len("EGFIS")

            self.gui.progress(show=True, indeter=False, statut=self.gui.translate("Converting files"),
                              max=max_step, step=0)
            self.gui.progress(statut=self.gui.translate("Configurating LE-CODE"), add=1)
            self.ctconfig.create_ctfile(highlight_version=self.gui.stringvar_mark_track_from_version.get())

            self.gui.progress(statut=self.gui.translate("Creating ct_icon.png"), add=1)
            ct_icon = self.ctconfig.get_cticon()
            ct_icon.save("./file/ct_icons.tpl.png")

            self.gui.progress(statut=self.gui.translate("Creating descriptive images"), add=1)
            self.patch_img_desc()
            self.patch_image(fc)
            for file in glob.glob(self.path + "/files/Scene/UI/MenuSingle_?.szs"): self.patch_bmg(file)
            # MenuSingle could be any other file, Common and Menu are all the same in all other files.
            self.patch_autoadd()
            if self.patch_tracks() != 0: return

            self.gui.button_install_mod.grid(row=2, column=1, columnspan=2, sticky="NEWS")
            self.gui.button_install_mod.config(
                text=self.gui.translate("Install mod", " (v", self.ctconfig.version, ")"))

        except:
            self.gui.log_error()
        finally:
            self.gui.progress(show=False)

    def patch_image(self, fc: dict) -> None:
        """
        Convert .png image into the format wrote in convert_file
        :param fc: file convert, a dictionnary indicating which format a file need to be converted
        """
        for i, file in enumerate(fc["img"]):
            self.gui.progress(statut=self.gui.translate("Converting images") + f"\n({i + 1}/{len(fc['img'])}) {file}",
                              add=1)
            img.encode("./file/" + file, fc["img"][file])

    def patch_img_desc(self, img_desc_path: str = "./file/img_desc", dest_dir: str = "./file") -> None:
        """
        patch descriptive image used when the game boot
        :param img_desc_path: directory where original part of the image are stored
        :param dest_dir: directory where patched image will be saved
        """
        il = Image.open(img_desc_path + "/illustration.png")
        il_16_9 = il.resize((832, 456))
        il_4_3 = il.resize((608, 456))

        for file_lang in glob.glob(img_desc_path + "??.png"):
            img_lang = Image.open(file_lang)
            img_lang_16_9 = img_lang.resize((832, 456))
            img_lang_4_3 = img_lang.resize((608, 456))

            new_16_9 = Image.new("RGBA", (832, 456), (0, 0, 0, 255))
            new_16_9.paste(il_16_9, (0, 0), il_16_9)
            new_16_9.paste(img_lang_16_9, (0, 0), img_lang_16_9)
            new_16_9.save(dest_dir + f"/strapA_16_9_832x456{get_filename(get_nodir(file_lang))}.png")

            new_4_3 = Image.new("RGBA", (608, 456), (0, 0, 0, 255))
            new_4_3.paste(il_4_3, (0, 0), il_4_3)
            new_4_3.paste(img_lang_4_3, (0, 0), img_lang_4_3)
            new_4_3.save(dest_dir + f"/strapA_608x456{get_filename(get_nodir(file_lang))}.png")

    def patch_tracks(self) -> int:
        """
        Download track's wu8 file and convert them to szs
        :return: 0 if no error occured
        """
        max_process = self.gui.intvar_process_track.get()
        thread_list = {}
        error_count, error_max = 0, 3

        def add_process(track) -> int:
            """
            a "single thread" to download, check sha1 and convert a track
            :param track: the track that will be patched
            :return: 0 if no error occured
            """
            nonlocal error_count, error_max, thread_list

            for _track in [track.file_szs, track.file_wu8]:
                if os.path.exists(_track):
                    if os.path.getsize(_track) < 1000:  # File under this size are corrupted
                        os.remove(_track)

            if not self.gui.boolvar_disable_download.get():
                while True:
                    download_returncode = 0
                    if not os.path.exists(track.file_wu8):
                        download_returncode = track.download_wu8(
                            GITHUB_DEV_BRANCH if self.gui.is_dev_version else GITHUB_MASTER_BRANCH)
                        if download_returncode == -1:  # can't download
                            error_count += 1
                            if error_count > error_max:  # Too much track wasn't correctly converted
                                messagebox.showerror(
                                    self.gui.translate("Error"),
                                    self.gui.translate("Too much tracks had a download issue."))
                                raise TooMuchDownloadFailed()
                            else:
                                messagebox.showwarning(self.gui.translate("Warning"),
                                                       self.gui.translate("Can't download this track !",
                                                                          f" ({error_count} / {error_max})"))

                    if track.sha1:
                        if not self.gui.boolvar_dont_check_track_sha1.get():
                            if track.check_sha1() != 0:  # if track sha1 is not the one excepted
                                error_count += 1
                                if error_count > error_max:  # Too much track wasn't correctly converted
                                    messagebox.showerror(
                                        self.gui.translate("Error"),
                                        self.gui.translate("Too much tracks had an issue during sha1 check."))
                                    raise TooMuchSha1CheckFailed()
                                continue

                    break

                if not os.path.exists(track.file_szs) or download_returncode == 3:
                    # returncode 3 is track has been updated
                    if os.path.exists(track.file_wu8):
                        track.convert_wu8_to_szs()
                    else:
                        messagebox.showerror(self.gui.translate("Error"),
                            self.gui.translate("Can't convert track.\nEnable track download and retry."))
                        raise CantConvertTrack()
                elif self.gui.boolvar_del_track_after_conv.get():
                    os.remove(track.file_wu8)
            return 0

        def clean_process() -> int:
            """
            Check if a track conversion ended, and remove them from thread_list
            :return: 0 if thread_list is empty, else 1
            """
            nonlocal error_count, error_max, thread_list

            for track_key, thread in thread_list.copy().items():
                if not thread.is_alive():  # if conversion ended
                    thread_list.pop(track_key)
                    if self.gui.boolvar_del_track_after_conv.get(): os.remove(track.file_wu8)
                if not (any(thread_list.values())): return 1  # if there is no more process

            if len(thread_list): return 1
            else: return 0

        total_track = len(self.ctconfig.all_tracks)
        for i, track in enumerate(self.ctconfig.all_tracks):
            while error_count <= error_max:
                if len(thread_list) < max_process:
                    track_name = track.get_track_name()
                    thread_list[track_name] = Thread(target=add_process, args=[track])
                    thread_list[track_name].setDaemon(True)
                    thread_list[track_name].start()
                    self.gui.progress(statut=self.gui.translate("Converting tracks", f"\n({i + 1}/{total_track})\n",
                                                                "\n".join(thread_list.keys())), add=1)
                    break
                clean_process()

        while clean_process() != 1:
            pass  # End the process if all process ended

        return 0
