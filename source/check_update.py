from tkinter import messagebox
from . import *
import requests
import zipfile
import json
import sys
import os

VERSION_FILE_URL = "https://raw.githubusercontent.com/Faraphel/MKWF-Install/master/version"
def check_update():
    try:
        gitversion = requests.get(VERSION_FILE_URL, allow_redirects=True).json()
        with open("version", "rb") as f:
            locversion = json.load(f)

        if gitversion["version"] != locversion["version"]:
            if messagebox.askyesno("Mise à jour disponible !", "Une mise à jour est disponible, souhaitez-vous l'installer ?\n\n"+ \
                                f"Version : {locversion['version']}.{locversion['subversion']} -> {gitversion['version']}.{gitversion['subversion']}\n"+\
                                f"Changelog :\n{gitversion['changelog']}"):

                if not(os.path.exists("./Updater/Updater.exe")):
                    dl = requests.get(gitversion["updater_bin"], allow_redirects=True)
                    with open("./download.zip", "wb") as file:
                        print(f"Téléchargement de Updater en cours...")
                        file.write(dl.content)
                        print("fin du téléchargement, début de l'extraction...")

                    with zipfile.ZipFile("./download.zip") as file:
                        file.extractall("./Updater/")
                        print("fin de l'extraction")

                    os.remove("./download.zip")
                    print("lancement de l'application...")
                    os.startfile(os.path.realpath("./Updater/Updater.exe"))
                    sys.exit()

    except Exception as e:
        print(e)