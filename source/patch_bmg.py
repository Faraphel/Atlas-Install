import subprocess
import shutil
import os

from .definition import *

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


def patch_bmg(self, gamefile):  # gamefile est le fichier .szs trouvé dans le /files/Scene/UI/ du jeu
    bmglang = gamefile[-len("E.txt"):-len(".txt")]  # Langue du fichier
    self.Progress(statut=self.translate("Patch des textes " + bmglang), add=1)

    subprocess.call(["./tools/szs/wszst", "EXTRACT", gamefile, "-d", gamefile + ".d", "--overwrite"]
                    , creationflags=CREATE_NO_WINDOW)

    bmgtracks = subprocess.check_output(["wbmgt", "CAT", gamefile + ".d/message/Common.bmg"])
    bmgtracks = bmgtracks.decode()
    trackheader = "#--- standard track names"
    trackend = "2328"
    bmgtracks = bmgtracks[bmgtracks.find(trackheader) + len(trackheader):bmgtracks.find(trackend)]

    with open("./file/ExtraCommon.txt", "w") as f:
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
                    if Tid[1] in "1234": prefix = "Wii " # Si la course est original à la wii
                    Tid = hex(bmgID_track_move[Tid])[2:]

                else: # Arena
                    sTid = bmgtrack.find("U") + 1
                    Tid = bmgtrack[sTid:sTid + 2]
                    Tid = hex((int(Tid[0]) - 1) * 5 + (int(Tid[1]) - 1) + 0x7020)[2:]

                Tname = bmgtrack[bmgtrack.find("= ") + 2:]
                f.write(f"  {Tid}\t= {prefix}{Tname}\n")

    bmgtext = subprocess.check_output(["tools/szs/wctct", "bmg", "--le-code", "--long", "./file/CTFILE.txt",
                                       "--patch-bmg", "OVERWRITE=" + gamefile + ".d/message/Common.bmg",
                                       "--patch-bmg", "OVERWRITE=./file/ExtraCommon.txt"],
                                      creationflags=CREATE_NO_WINDOW)
    rbmgtext = subprocess.check_output(["tools/szs/wctct", "bmg", "--le-code", "--long", "./file/RCTFILE.txt",
                                        "--patch-bmg", "OVERWRITE=" + gamefile + ".d/message/Common.bmg",
                                        "--patch-bmg", "OVERWRITE=./file/ExtraCommon.txt"],
                                       creationflags=CREATE_NO_WINDOW)
    shutil.rmtree(gamefile + ".d")
    os.remove("./file/ExtraCommon.txt")

    common_file = f"./file/Common_{bmglang}.txt"
    rcommon_file = f"./file/Common_R{bmglang}.txt"
    with open(common_file, "w", encoding="utf-8") as f:
        f.write(bmgtext.decode())
    with open(rcommon_file, "w", encoding="utf-8") as f:
        f.write(rbmgtext.decode())
    subprocess.call(["./tools/szs/wbmgt", "ENCODE", common_file, "--overwrite"])
    subprocess.call(["./tools/szs/wbmgt", "ENCODE", rcommon_file, "--overwrite"])
    os.remove(common_file)
    os.remove(rcommon_file)
