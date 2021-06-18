from threading import Thread
import json
import glob
import os


def patch_file(self):
    def func():
        try:
            if not(os.path.exists("./file/Track-WU8/")): os.makedirs("./file/Track-WU8/")
            with open("./convert_file.json") as f: fc = json.load(f)
            tracks, total_track = self.count_track()
            max_step = len(fc["img"]) + total_track + 3 + len("EGFIS")

            self.Progress(show=True, indeter=False, statut=self.translate("Conversion des fichiers"), max=max_step, step=0)
            self.Progress(statut=self.translate("Configuration de LE-CODE"), add=1)
            self.create_lecode_config()
            self.Progress(statut=self.translate("Création de ct_icon.png"), add=1)
            self.patch_ct_icon()
            self.Progress(statut=self.translate("Création des images descriptives"), add=1)
            self.patch_img_desc()
            self.patch_image(fc)
            for file in glob.glob(self.path_mkwf+"/files/Scene/UI/MenuSingle_?.szs"): self.patch_bmg(file)
            self.patch_autoadd()
            self.patch_track(tracks, total_track)

            self.button_install_mod.grid(row=2, column=1, columnspan=2, sticky="NEWS")

        except: self.log_error()
        finally: self.Progress(show=False)

    t = Thread(target=func)
    t.setDaemon(True)
    t.start()
    return t
