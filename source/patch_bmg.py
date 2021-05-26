import subprocess
import shutil
import os

from .definition import *


def patch_bmg(self, gamefile): # gamefile est le fichier .szs trouvé dans le /files/Scene/UI/ du jeu
    subprocess.call(["./tools/szs/wszst", "EXTRACT", gamefile, "-d", gamefile+".d", "--overwrite"]
                    , creationflags=CREATE_NO_WINDOW)

    bmglang = gamefile[-len("E.txt"):-len(".txt")] # Langue du fichier
    bmgtext = subprocess.check_output(["tools/szs/wctct", "bmg", "--le-code", "--long", "./file/CTFILE.txt",
                                       "--patch-bmg", "OVERWRITE="+gamefile+".d/message/Common.bmg"]
                                      , creationflags=CREATE_NO_WINDOW)
    shutil.rmtree(gamefile+".d")

    common_file = f"./file/Common_{bmglang}.txt"
    with open(common_file, "w", encoding="utf-8") as f: f.write(bmgtext.decode())
    subprocess.call(["./tools/szs/wbmgt", "ENCODE", common_file, "--overwrite"])
    os.remove(common_file)