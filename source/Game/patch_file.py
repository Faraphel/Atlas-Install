from threading import Thread
import glob
import json
import os

from .patch_img_desc import patch_img_desc
from .patch_image import patch_image
from .patch_track import patch_track
from .patch_bmg import patch_bmg


def patch_file(self, gui):
    def func():
        try:
            if not (os.path.exists("./file/Track-WU8/")): os.makedirs("./file/Track-WU8/")
            with open("./convert_file.json") as f:
                fc = json.load(f)
            max_step = len(fc["img"]) + len(gui.ctconfig.all_tracks) + 3 + len("EGFIS")

            gui.progress(show=True, indeter=False, statut=gui.translate("Converting files"), max=max_step, step=0)
            gui.progress(statut=gui.translate("Configurating LE-CODE"), add=1)
            gui.ctconfig.create_ctfile()

            gui.progress(statut=gui.translate("Creating ct_icon.png"), add=1)
            ct_icon = gui.ctconfig.get_cticon()
            ct_icon.save("./file/ct_icons.tpl.png")

            gui.progress(statut=gui.translate("Creating descriptive images"), add=1)
            patch_img_desc()
            patch_image(fc, gui)
            for file in glob.glob(self.path + "/files/Scene/UI/MenuSingle_?.szs"): patch_bmg(file, gui)
            # MenuSingle could be any other file, Common and Menu are all the same in all other files.
            self.patch_autoadd()
            if patch_track(gui) != 0: return

            gui.button_install_mod.grid(row=2, column=1, columnspan=2, sticky="NEWS")
            gui.button_install_mod.config(
                text=gui.translate("Install mod", " (v", gui.ctconfig.version, ")"))

        except:
            gui.log_error()
        finally:
            gui.progress(show=False)

    t = Thread(target=func)
    t.setDaemon(True)
    t.start()
    return t