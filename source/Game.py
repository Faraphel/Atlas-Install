from tkinter import messagebox
from PIL import Image
import shutil
import glob
import json

from .Track import CantDownloadTrack
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
    intvar_process_track = NoVariable()
    boolvar_dont_check_track_sha1 = NoVariable()


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
            path_game_format: str = os.path.realpath(self.path + f"/../{self.ctconfig.nickname} v{self.ctconfig.version}." + format.lower())
            wit.copy(src_path=self.path, dst_path=path_game_format, format=format)
            shutil.rmtree(self.path)
            self.path = path_game_format

            self.gui.progress(statut=self.gui.translate("Changing game's ID"), add=1)
            wit.edit(
                file=self.path,
                region_ID=self.region_ID,
                game_variant=self.ctconfig.game_variant,
                name=f"{self.ctconfig.name} {self.ctconfig.version}"
            )

    def extract(self) -> None:
        """
        Extract game file in the same directory.
        """
        if self.extension == "DOL":
            self.path = os.path.realpath(self.path + "/../../")  # main.dol is in PATH/sys/, so go back 2 dir upper

        elif self.extension in ["ISO", "WBFS", "CSIO"]:
            # Fiding a directory name that doesn't already exist
            path_dir = get_next_available_dir(
                parent_dir=self.path + f"/../",
                dir_name=f"{self.ctconfig.nickname} v{self.ctconfig.version}"
            )

            wit.extract(file=self.path, dst_dir=path_dir)

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

    def count_patch_subfile_operation(self) -> int:
        """
        count all the step patching subfile will take (for the progress bar)
        :return: number of step estimated
        """
        with open("./file_structure.json") as f:
            fs = json.load(f)

        # This part is used to estimate the max_step
        extracted_file = []
        max_step = 1

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

        return max_step

    def install_patch_subfile(self) -> None:
        """
        patch subfile as indicated in the file_structure.json file (for file structure)
        """
        with open("./file_structure.json") as f:
            fs = json.load(f)

        extracted_file = []
        self.gui.progress(show=True, indeter=False, statut=self.gui.translate("Modifying subfile..."), add=1)

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
                    szs.extract(file=path)
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
            szs.create(file=file)
            if os.path.exists(file + ".d"):
                shutil.rmtree(file + ".d")

    def install_copy_mystuff(self) -> None:
        """
        copy MyStuff directory into the game *before* patching the game
        """
        self.gui.progress(show=True, indeter=False, statut=self.gui.translate("Copying MyStuff..."), add=1)

        mystuff_folder = self.gui.stringvar_mystuff_folder.get()
        if mystuff_folder and mystuff_folder != "None":

            # replace game's file by files with the same name in the MyStuff root
            mystuff_files = {}
            for mystuff_file in glob.glob(f"{mystuff_folder}/*"):   # for every file at the root of the mystuff folder
                basename = os.path.basename(mystuff_file)

                if os.path.isfile(mystuff_file):
                    #  replace the game files with the file at mystuff's root
                    mystuff_files[basename] = mystuff_file
                else:
                    #  if this is a dict, simply copy it into the game files
                    shutil.copytree(mystuff_file, f"{self.path}/files/{basename}/", dirs_exist_ok=True)

            for game_file in glob.glob(f"{self.path}/files/**/*", recursive=True):
                basename = os.path.basename(game_file)
                if basename in mystuff_files:
                    mystuff_file = mystuff_files[basename]
                    shutil.copy(mystuff_file, game_file)
                    print(f"copied {mystuff_file} to {game_file}")

    def install_patch_maindol(self) -> None:
        """
        patch the main.dol file to allow the addition of LECODE.bin file
        """
        self.gui.progress(statut=self.gui.translate("Patch main.dol"), add=1)

        region_id = self.ctconfig.region if self.gui.is_using_official_config() else self.ctconfig.cheat_region
        wstrt.patch(path=self.path, region_id=region_id)

    def install_patch_lecode(self) -> None:
        """
        configure and add the LECODE.bin file to the mod
        """
        self.gui.progress(statut=self.gui.translate("Patch lecode.bin"), add=1)

        lpar_path = "./file/lpar-debug.txt" if self.gui.boolvar_use_debug_mode.get() else "./file/lpar-default.txt"

        lec.patch(
            lecode_file=f"./file/lecode-{self.region}.bin",
            dest_lecode_file=f"{self.path}/files/rel/lecode-{self.region}.bin",
            game_track_path=f"{self.path}/files/Race/Course/",
            copy_track_paths=[f"./file/Track/"],
            move_track_paths=[f"{self.path}/files/Race/Course/"],
            ctfile_path="./file/CTFILE.txt",
            lpar_path=lpar_path,
        )

    def install_convert_rom(self) -> None:
        """
        convert the rom to the selected game format
        """
        output_format = self.gui.stringvar_game_format.get()
        self.gui.progress(statut=self.gui.translate("Converting to", " ", output_format), add=1)
        self.convert_to(output_format)

    def install_mod(self) -> None:
        """
        Patch the game to install the mod
        """
        try:
            max_step = 5 + self.count_patch_subfile_operation()
            # PATCH main.dol and PATCH lecode.bin, converting, changing ID, copying MyStuff Folder

            self.gui.progress(statut=self.gui.translate("Installing mod..."), max=max_step, step=0)
            self.install_copy_mystuff()
            self.install_patch_subfile()
            self.install_patch_maindol()
            self.install_patch_lecode()
            self.install_convert_rom()

            messagebox.showinfo(self.gui.translate("End"), self.gui.translate("The mod have been installed !"))

        except:
            self.gui.log_error()
        finally:
            self.gui.progress(show=False)
            self.gui.quit()

    def patch_autoadd(self, auto_add_dir: str = "./file/auto-add") -> None:
        """
        Create the autoadd directory used to convert wbz track into szs
        :param auto_add_dir: autoadd directory
        """
        if os.path.exists(auto_add_dir): shutil.rmtree(auto_add_dir)
        szs.autoadd(path=self.path, dest_dir=auto_add_dir)

    def create_extra_common(self, bmgtracks: str, extra_common_path: str = "./file/ExtraCommon.txt") -> None:
        """
        this function create an "extra common" file : it contain modification about the original tracks name
        (the color modification) and allow the modification to be applied by overwritting the normal common
        file by this one.
        :param bmgtracks: bmg containing the track list
        :param extra_common_path: destination path to the extra common file
        """

        with open(extra_common_path, "w", encoding="utf8") as f:
            f.write("#BMG\n")

            for bmgtrack in bmgtracks.split("\n"):
                if "=" in bmgtrack:

                    prefix = ""
                    track_name = bmgtrack[bmgtrack.find("= ") + 2:]

                    if "T" in bmgtrack[:bmgtrack.find("=")]:
                        start_track_id: int = bmgtrack.find("T")  # index where the bmg track definition start
                        track_id = bmgtrack[start_track_id:start_track_id + 3]
                        if track_id[1] in "1234":  # if the track is a original track from the wii
                            prefix = "Wii"
                            if prefix in self.ctconfig.tags_color:
                                prefix = "\\\\c{" + self.ctconfig.tags_color[prefix] + "}" + prefix + "\\\\c{off}"
                            prefix += " "

                        elif track_id[1] in "5678":  # if the track is a retro track from the original game
                            prefix, *track_name = track_name.split(" ")
                            track_name = " ".join(track_name)
                            if prefix in self.ctconfig.tags_color:
                                prefix = "\\\\c{" + self.ctconfig.tags_color[prefix] + "}" + prefix + "\\\\c{off}"
                            prefix += " "

                        track_id = hex(bmgID_track_move[track_id])[2:]

                    else:  # Arena
                        start_track_id = bmgtrack.find("U") + 1  # index where the bmg arena definition start
                        track_id = bmgtrack[start_track_id:start_track_id + 2]
                        track_id = hex((int(track_id[0]) - 1) * 5 + (int(track_id[1]) - 1) + 0x7020)[2:]

                    f.write(f"  {track_id}\t= {prefix}{track_name}\n")

    def patch_bmg(self, gamefile: str) -> None:
        """
        Patch bmg file (text file)
        :param gamefile: an .szs file where file will be patched
        """

        bmg_replacement = {
            "MOD_NAME": self.ctconfig.name,
            "MOD_NICKNAME": self.ctconfig.nickname,
            "MOD_VERSION": self.ctconfig.version,
            "MOD_CUSTOMIZED": "" if self.gui.is_using_official_config() else " (custom)",
            "ONLINE_SERVICE": "Wiimmfi",
        }

        bmglang = gamefile[-len("E.txt"):-len(".txt")]  # Langue du fichier
        self.gui.progress(statut=self.gui.translate("Patching text", " ", bmglang), add=1)

        szs.extract(file=gamefile)

        bmgmenu = bmg.cat(path=gamefile, subfile=".d/message/Menu.bmg")  # Menu.bmg

        trackheader = "#--- standard track names"
        trackend = "2328"
        bmgtracks = bmg.cat(path=gamefile, subfile=".d/message/Common.bmg")  # Common.bmg
        bmgtracks = bmgtracks[bmgtracks.find(trackheader) + len(trackheader):bmgtracks.find(trackend)]

        self.create_extra_common(bmgtracks=bmgtracks, extra_common_path="./file/ExtraCommon.txt")

        bmgcommon = ctc.patch_bmg(ctfile="./file/CTFILE.txt",
                                  bmgs=[gamefile + ".d/message/Common.bmg", "./file/ExtraCommon.txt"])
        rbmgcommon = ctc.patch_bmg(ctfile="./file/RCTFILE.txt",
                                   bmgs=[gamefile + ".d/message/Common.bmg", "./file/ExtraCommon.txt"])

        shutil.rmtree(gamefile + ".d")
        os.remove("./file/ExtraCommon.txt")

        def process_bmg_replacement(bmg_content: str, bmg_language: str) -> str:
            """
            This function apply the file_process to the bmg file. This allow text modification useful to
            change menu text (Wiimmfi for example) and the Wiimm's cup.
            :param bmg_content: content of the bmg to process
            :param bmg_language: language of the bmg file
            :return: the replaced bmg file
            """
            with open("./file_process.json", encoding="utf8") as fp_file:
                file_process = json.load(fp_file)

            for bmg_process in file_process["bmg"]:
                if "language" in bmg_process:
                    if bmg_language not in bmg_process["language"]:
                        continue

                for data, data_replacement in bmg_process["data"].items():
                    for key, replacement in bmg_replacement.items():
                        data_replacement = data_replacement.replace("{"+key+"}", replacement)

                    if bmg_process["mode"] == "overwrite_id":
                        start_line = f"\n\t{str_to_int(data):x} = "
                        start_pos = bmg_content.find(start_line)
                        if start_pos != -1:
                            end_pos = bmg_content[start_pos:].find("\n")
                            bmg_content = (
                                    bmg_content[:start_pos] +
                                    start_line + data_replacement +
                                    bmg_content[end_pos:]
                            )
                        else:
                            bmg_content = f"{bmg_content}\n{start_line}{data_replacement}\n"

                    elif bmg_process["mode"] == "replace_text":
                        bmg_content = bmg_content.replace(data, data_replacement)

            return bmg_content

        def save_bmg(file: str, bmg_content: str) -> None:
            """
            Save and encode the bmg
            :param file: name of the bmg-text to save
            :param bmg_content: content to save in the bmg-text
            """
            with open(file, "w", encoding="utf-8") as f: f.write(bmg_content)
            bmg.encode(file)
            os.remove(file)

        save_bmg(f"./file/Menu_{bmglang}.txt", process_bmg_replacement(bmgmenu, bmglang))
        save_bmg(f"./file/Common_{bmglang}.txt", process_bmg_replacement(bmgcommon, bmglang))
        save_bmg(f"./file/Common_R{bmglang}.txt", process_bmg_replacement(rbmgcommon, bmglang))

    def patch_file(self):
        """
        Prepare all files to install the mod (track, bmg text, descriptive image, ...)
        """
        try:
            if not (os.path.exists("./file/Track-WU8/")): os.makedirs("./file/Track-WU8/")
            with open("./file_process.json", encoding="utf8") as fp_file:
                file_process = json.load(fp_file)
            max_step = len(file_process["img"]) + len(self.ctconfig.all_tracks) + 3 + len("EGFIS")

            self.gui.progress(show=True, indeter=False, statut=self.gui.translate("Converting files"),
                              max=max_step, step=0)
            self.gui.progress(statut=self.gui.translate("Configurating LE-CODE"), add=1)
            self.ctconfig.create_ctfile(
                highlight_version=self.gui.stringvar_mark_track_from_version.get(),
                sort_track_by=self.gui.stringvar_sort_track_by.get()
            )

            self.gui.progress(statut=self.gui.translate("Creating ct_icon.png"), add=1)
            ct_icon = self.ctconfig.get_cticon()
            ct_icon.save("./file/ct_icons.tpl.png")

            self.gui.progress(statut=self.gui.translate("Creating descriptive images"), add=1)
            self.patch_img_desc()
            self.patch_image(file_process["img"])
            for file in glob.glob(self.path + "/files/Scene/UI/MenuSingle_?.szs"): self.patch_bmg(file)
            # MenuSingle could be any other file, Common and Menu are all the same in all other files.
            self.patch_autoadd()
            self.patch_tracks()

        except:
            self.gui.log_error()
        finally:
            self.gui.progress(show=False)

    def patch_image(self, fp_img: dict) -> None:
        """
        Convert .png image into the format wrote in convert_file
        :param fp_img: file convert, a dictionnary indicating which format a file need to be converted
        """
        for i, file in enumerate(fp_img):
            self.gui.progress(statut=self.gui.translate("Converting images") + f"\n({i + 1}/{len(fp_img)}) {file}",
                              add=1)
            img.encode(file="./file/" + file, format=fp_img[file])

    def patch_img_desc(self, img_desc_path: str = "./file/img_desc/", dest_dir: str = "./file/") -> None:
        """
        patch descriptive image used when the game boot
        :param img_desc_path: directory where original part of the image are stored
        :param dest_dir: directory where patched image will be saved
        """
        il = Image.open(img_desc_path + "/illustration.png")
        il_16_9 = il.resize((832, 456))
        il_4_3 = il.resize((608, 456))

        for file_lang in glob.glob(img_desc_path + "/??.png"):
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

    def patch_tracks(self) -> None:
        """
        Download track's wu8 file and convert them to szs
        """
        max_process = self.gui.intvar_process_track.get()
        thread_list = {}
        error_count, error_max = 0, 3

        def add_process(track) -> None:
            """
            a "single thread" to download, check sha1 and convert a track
            :param track: the track that will be patched
            :return: 0 if no error occured
            """
            nonlocal error_count, error_max, thread_list

            if os.path.exists(track.file_szs) and os.path.getsize(track.file_szs) < 1000:
                os.remove(track.file_szs)  # File under this size are corrupted

            if not track.check_szs_sha1():  # if sha1 of track's szs is incorrect or track's szs does not exist
                if os.path.exists(track.file_wu8):
                    track.convert_wu8_to_szs()
                else:
                    messagebox.showerror(self.gui.translate("Error"),
                                         self.gui.translate("Can't convert track.\nEnable track download and retry."))
                    raise CantConvertTrack()

        def clean_process() -> int:
            """
            Check if a track conversion ended, and remove them from thread_list
            :return: 0 if thread_list is empty, else 1
            """
            nonlocal error_count, error_max, thread_list

            for track_key, thread in thread_list.copy().items():
                if not thread.is_alive():  # if conversion ended
                    thread_list.pop(track_key)
                if not (any(thread_list.values())): return 1  # if there is no more process

            return bool(thread_list)

        total_track = len(self.ctconfig.all_tracks)
        self.gui.progress(max=total_track, indeter=False, show=True)

        for i, track in enumerate(self.ctconfig.all_tracks):
            while error_count <= error_max:
                if len(thread_list) < max_process:
                    thread_list[track.sha1] = Thread(target=add_process, args=[track])
                    thread_list[track.sha1].setDaemon(True)
                    thread_list[track.sha1].start()
                    self.gui.progress(statut=self.gui.translate("Converting tracks", f"\n({i + 1}/{total_track})\n",
                                                                "\n".join(thread_list.keys())), add=1)
                    break
                clean_process()

        while clean_process() != 1: pass  # End the process if all process ended
