import subprocess
import shutil
import os

from .definition import *


def patch_bmg(self, gamefile):  # gamefile est le fichier .szs trouvé dans le /files/Scene/UI/ du jeu
    subprocess.call(["./tools/szs/wszst", "EXTRACT", gamefile, "-d", gamefile + ".d", "--overwrite"]
                    , creationflags=CREATE_NO_WINDOW)

    bmgtracks = subprocess.check_output(["wbmgt", "CAT", gamefile + ".d/message/Common.bmg"])
    bmgtracks = bmgtracks.decode()
    trackheader = "#--- standard track names"
    trackend = "2328"
    bmgtracks = bmgtracks[bmgtracks.find(trackheader) + len(trackheader):bmgtracks.find(trackend)]
    bmglang = gamefile[-len("E.txt"):-len(".txt")]  # Langue du fichier

    with open("./file/ExtraCommon.txt", "w") as f:
        f.write("#BMG\n\n"
                f"  703e\t= {self.translate('Aléatoire: Toutes les pistes', lang=bmglang)}\n"
                f"  703f\t= {self.translate('Aléatoire: Pistes Originales', lang=bmglang)}\n"
                f"  7040\t= {self.translate('Aléatoire: Custom Tracks', lang=bmglang)}\n"
                f"  7041\t= {self.translate('Aléatoire: Pistes Nouvelles', lang=bmglang)}\n")



        for bmgtrack in bmgtracks.split("\n"):
            if "=" in bmgtrack:

                if "T" in bmgtrack[:bmgtrack.find("=")]:
                    sTid, offset = bmgtrack.find("T") + 1, 0x7000
                else:
                    sTid, offset = bmgtrack.find("U") + 1, 0x7020

                eTid = sTid + 2
                Tid = bmgtrack[sTid:eTid]
                Tid = hex((int(Tid[0]) - 1) * 4 + (int(Tid[1]) - 1) + offset)[2:]
                Tname = bmgtrack[bmgtrack.find("= ") + 2:]

                f.write(f"  {Tid}\t= {Tname}\n")

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
