import subprocess
import shutil
from .definition import *


def patch_bmg(self, bmgfileszs):
    subprocess.call(["./tools/szs/wszst", "EXTRACT", bmgfileszs, "-d", bmgfileszs + ".d", "--overwrite"]
                    , creationflags=CREATE_NO_WINDOW)

    bmgfile = "./file/" + get_nodir(bmgfileszs) + ".bmg"
    print(bmgfile)
    filecopy(bmgfileszs + ".d/message/Common.bmg", bmgfile)
    shutil.rmtree(bmgfileszs + ".d")

    bmgtext = subprocess.check_output(["tools/szs/wctct", "--le-code", "--long", "BMG", "./file/CTFILE.txt",
                                       "--patch-bmg", "REPLACE="+bmgfile], creationflags=CREATE_NO_WINDOW)
    with open(bmgfile+".txt", "w", encoding="utf-8") as f: f.write(bmgtext.decode())
    subprocess.call(["./tools/szs/wbmgt", "ENCODE", bmgfile+".txt", "--overwrite"])
    #os.remove(bmgfile+".txt")