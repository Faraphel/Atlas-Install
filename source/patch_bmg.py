import subprocess
import shutil
import os

from .definition import *


def patch_bmg(self, gamefile):  # gamefile est le fichier .szs trouvé dans le /files/Scene/UI/ du jeu
    try:
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
        self.Progress(statut=self.translate("Patching text", " ", bmglang), add=1)

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
                    f"  703e\t= \\\\c{{white}}{self.translate('Random: All tracks', lang=bmglang)}\n"
                    f"  703f\t= \\\\c{{white}}{self.translate('Random: Original tracks', lang=bmglang)}\n"
                    f"  7040\t= \\\\c{{white}}{self.translate('Random: Custom Tracks', lang=bmglang)}\n"
                    f"  7041\t= \\\\c{{white}}{self.translate('Random: New tracks', lang=bmglang)}\n")

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

        if not(os.path.exists("./file/tmp/")): os.makedirs("./file/tmp/")

        filecopy(gamefile+".d/message/Common.bmg", "./file/tmp/Common.bmg")
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
            with open(file, "w", encoding="utf-8") as f: f.write(bmgtext)
            subprocess.run(["./tools/szs/wbmgt", "ENCODE", get_nodir(file), "--overwrite"],
                           creationflags=CREATE_NO_WINDOW, cwd=get_dir(file))
            os.remove(file)

        finalise(f"./file/Menu_{bmglang}.txt", bmgmenu, menu_replacement)
        finalise(f"./file/Common_{bmglang}.txt", bmgcommon)
        finalise(f"./file/Common_R{bmglang}.txt", rbmgcommon)

    except:
        self.log_error()
