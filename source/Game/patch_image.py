import subprocess

from source.definition import *


def patch_image(fc, gui):
    for i, file in enumerate(fc["img"]):
        gui.progress(statut=gui.translate("Converting images") + f"\n({i + 1}/{len(fc['img'])}) {file}", add=1)
        subprocess.run(["./tools/szs/wimgt", "ENCODE", "./file/" + file, "-x", fc["img"][file], "--overwrite"],
                       creationflags=CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)
