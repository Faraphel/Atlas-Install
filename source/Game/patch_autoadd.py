import subprocess
import shutil
import os

from source.definition import *


def patch_autoadd(self, auto_add_dir: str = "./file/auto-add"):
    if os.path.exists(auto_add_dir): shutil.rmtree(auto_add_dir)
    if not os.path.exists(self.path + "/tmp/"): os.makedirs(self.path + "/tmp/")
    subprocess.run(["./tools/szs/wszst", "AUTOADD", get_nodir(self.path) + "/files/Race/Course/",
                    "--DEST", get_nodir(self.path) + "/tmp/auto-add/"],
                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(self.path),
                   check=True, stdout=subprocess.PIPE)
    shutil.move(self.path + "/tmp/auto-add/", auto_add_dir)
    shutil.rmtree(self.path + "/tmp/")
