import subprocess
import shutil
import os

from .definition import *


def patch_bmg(self, gamefile):  # gamefile est le fichier .szs trouvé dans le /files/Scene/UI/ du jeu
    try:

        bmgID_track_move = {
            "T11": 0x7008, "T12": 0x7001, "T13": 0x7002, "T14": 0x7004,
            "T21": 0x7000, "T22": 0x7005, "T23": 0x7006, "T24": 0x7007,
            "T31": 0x7009, "T32": 0x700f, "T33": 0x700b, "T34": 0x7003,
            "T41": 0x700e, "T42": 0x700a, "T43": 0x700c, "T44": 0x700d,

            "T51": 0x7010, "T52": 0x7014, "T53": 0x7019, "T54": 0x701a,
            "T61": 0x701b, "T62": 0x701f, "T63": 0x7017, "T64": 0x7012,
            "T71": 0x7015, "T72": 0x701e, "T73": 0x701d, "T74": 0x7011,
            "T81": 0x7018, "T82": 0x7016, "T83": 0x7013, "T84": 0x701c,
        }
        trackname_color = {
            "MSRDS ": "\c{green}MSRDS\c{off} ",
            "CTR ": "\c{YOR4}CTR\c{off} ",
            "CTTR ": "\c{YOR5}CTTR\c{off} ",
            "CNR ": "\c{YOR5}CNR\c{off} ",
            "DKR ": "\c{YOR6}DKR\c{off} ",
            "LCP ": "\c{green}LCP\c{off} ",
            "LEGO-R ": "\c{red2}LEGO-R\c{off} ",
            "MP9 ": "\c{YOR0}MP9\c{off} ",
            "MSUSA ": "\c{green}MSUSA\c{off} ",
            "FZMV ": "\c{YOR2}FZMV\c{off} ",
            "KAR ": "\c{green}KAR\c{off} ",
            "KO ": "\c{YOR5}KO\c{off} ",
            "FZ ": "\c{YOR2}FZ\c{off} ",
            "RV ": "\c{white}RV\c{off} ",
            "SADX ": "\c{blue2}SADX\c{off} ",
            "SCR ": "\c{YOR2}SCR\c{off} ",
            "SH ": "\c{red}SH\c{off} ",
            "SM64 ": "\c{red1}SM64\c{off} ",
            "SMB1 ": "\c{red2}SMB1\c{off} ",
            "SMB2 ": "\c{red3}SMB2\c{off} ",
            "SSBB ": "\c{red4}SSBB\c{off} ",
            "SMS ": "\c{YOR6}SMS\c{off} ",
            "SMO ": "\c{YOR7}SMO\c{off} ",
            "VVVVVV ": "\c{blue}VVVVVV\c{off} ",
            "WF ": "\c{green}WF\c{off} ",
            "WP ": "\c{yellow}WP\c{off} ",
            "Zelda OoT ": "\c{green}Zelda OoT\c{off} ",
            "Zelda TP ": "\c{green}Zelda TP\c{off} ",
            "Zelda WW ": "\c{green}Zelda WW\c{off} ",
            "PMWR ": "\c{yellow}PMWR\c{off} ",
            "SHR ": "\c{green}SHR\c{off} ",
            "SK64 ": "\c{green}SK64\c{off} ",
            "SMG ": "\c{red2}SMG\c{off} ",
            "Spyro 1 ": "\c{blue}Spyro 1\c{off} ",

            "Aléatoire: ": "\c{white}Aléatoire: ",
            "Random: ": "\c{white}Random: ",
            "Zufällig: ": "\c{white}Zufällig: ",
            "Casuale: ": "\c{white}Casuale: ",
            "Aleatorio: ": "\c{white}Aleatorio: ",

            "Wii U ": "WiiU ",
            "Wii ": "\c{blue}Wii\c{off} ",
            "WiiU ": "\c{red4}Wii U\c{off} ",  # Permet d'éviter que Wii et Wii U se mélange

            "3DS ": "\c{YOR3}3DS\c{off} ",
            "DS ": "\c{white}DS\c{off} ",
            "GCN ": "\c{blue2}GCN\c{off} ",
            "GBA ": "\c{blue1}GBA\c{off} ",
            "N64 ": "\c{red}N64\c{off} ",
            "SNES ": "\c{green}SNES\c{off} ",
            "RMX ": "\c{YOR4}RMX\c{off} ",
            "MKT ": "\c{YOR5}MKT\c{off} ",
            "GP ": "\c{YOR6}GP\c{off} ",

            "(Boost)": "\c{YOR3}(Boost)\c{off}",

            "★★★ ": "\c{YOR2}★★★\c{off} ",
            "★★☆ ": "\c{YOR2}★★☆\c{off} ",
            "★☆☆ ": "\c{YOR2}★☆☆\c{off} ",
            "★★★! ": "\c{YOR4}★★★\c{off} ",
            "★★☆! ": "\c{YOR4}★★☆\c{off} ",
            "★☆☆! ": "\c{YOR4}★☆☆\c{off} ",
            "★★★!! ": "\c{YOR6}★★★\c{off} ",
            "★★☆!! ": "\c{YOR6}★★☆\c{off} ",
            "★☆☆!! ": "\c{YOR6}★☆☆\c{off} ",
        }
        NINTENDO_CWF_REPLACE = "Wiimmfi"
        MAINMENU_REPLACE = f"MKWFaraphel {self.VERSION}"
        menu_replacement = {
            "CWF de Nintendo": NINTENDO_CWF_REPLACE,
            "CWF Nintendo": NINTENDO_CWF_REPLACE,
            "Nintendo WFC": NINTENDO_CWF_REPLACE,

            "Menu principal": MAINMENU_REPLACE,
            "Menú principal": MAINMENU_REPLACE,
            "Main Menu": MAINMENU_REPLACE,

            "Mario Kart Wii": MAINMENU_REPLACE,
        }

        bmglang = gamefile[-len("E.txt"):-len(".txt")]  # Langue du fichier
        self.Progress(statut=self.translate("Patch des textes ") + bmglang, add=1)

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
                    f"  703e\t= {self.translate('Aléatoire: Toutes les pistes', lang=bmglang)}\n"
                    f"  703f\t= {self.translate('Aléatoire: Pistes Originales', lang=bmglang)}\n"
                    f"  7040\t= {self.translate('Aléatoire: Custom Tracks', lang=bmglang)}\n"
                    f"  7041\t= {self.translate('Aléatoire: Pistes Nouvelles', lang=bmglang)}\n")

            for bmgtrack in bmgtracks.split("\n"):
                if "=" in bmgtrack:

                    prefix = ""
                    if "T" in bmgtrack[:bmgtrack.find("=")]:
                        sTid = bmgtrack.find("T")
                        Tid = bmgtrack[sTid:sTid + 3]
                        if Tid[1] in "1234": prefix = "Wii "  # Si la course est original à la wii
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

        def finalise(file, bmgtext, replacement_list):
            for text, colored_text in replacement_list.items(): bmgtext = bmgtext.replace(text, colored_text)
            with open(file, "w", encoding="utf-8") as f: f.write(bmgtext)
            subprocess.run(["./tools/szs/wbmgt", "ENCODE", get_nodir(file), "--overwrite"],
                           creationflags=CREATE_NO_WINDOW, cwd=get_dir(file))
            os.remove(file)

        finalise(f"./file/Menu_{bmglang}.txt", bmgmenu, menu_replacement)
        finalise(f"./file/Common_{bmglang}.txt", bmgcommon, trackname_color)
        finalise(f"./file/Common_R{bmglang}.txt", rbmgcommon, trackname_color)

    except:
        self.log_error()
