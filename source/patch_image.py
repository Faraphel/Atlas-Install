from .definition import *
import subprocess


def patch_image(self, fc):
    for i, file in enumerate(fc["img"]):
        self.Progress(statut=self.translate("Conversion des images") + f"\n({i + 1}/{len(fc['img'])}) {file}", add=1)
        subprocess.run(["./tools/szs/wimgt", "ENCODE", "./file/" + file, "-x", fc["img"][file], "--overwrite"],
                       creationflags=CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)
