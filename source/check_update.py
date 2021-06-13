from . import *
import requests
import zipfile
import json
import sys
import os

VERSION_FILE_URL = "https://raw.githubusercontent.com/Faraphel/MKWF-Install/master/version"
def check_update(self):
    try:
        gitversion = requests.get(VERSION_FILE_URL, allow_redirects=True).json()
        with open("version", "rb") as f:
            locversion = json.load(f)

        if float(gitversion["version"]) > float(locversion["version"]):
            if messagebox.askyesno(self.translate("Mise à jour disponible !"), self.translate("Une mise à jour est disponible, souhaitez-vous l'installer ?") +
                                f"\n\nVersion : {locversion['version']}.{locversion['subversion']} -> {gitversion['version']}.{gitversion['subversion']}\n"+\
                                f"Changelog :\n{gitversion['changelog']}"):

                if not(os.path.exists("./Updater/Updater.exe")):
                    dl = requests.get(gitversion["updater_bin"], allow_redirects=True)
                    with open("./download.zip", "wb") as file:
                        print(self.translate("Téléchargement de Updater en cours..."))
                        file.write(dl.content)
                        print(self.translate("fin du téléchargement, "
                                             "début de l'extraction..."))

                    with zipfile.ZipFile("./download.zip") as file:
                        file.extractall("./Updater/")
                        print(self.translate("fin de l'extraction"))

                    os.remove("./download.zip")
                    print(self.translate("lancement de l'application..."))
                    os.startfile(os.path.realpath("./Updater/Updater.exe"))
                    sys.exit()

    except Exception as e:
        print(e)