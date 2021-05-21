import requests
import zipfile
import os
import sys

Dir, ext = os.path.splitext(sys.argv[0])
if ext == ".py":
    input("Ce code ne doit être lancé que sous sa forme .exe !")
    exit()

VERSION_FILE_URL = "https://raw.githubusercontent.com/Faraphel/MKWF-Install/master/version"

try:
    gitversion = requests.get(VERSION_FILE_URL, allow_redirects=True).json()
    URL = gitversion["download_bin"]

    dl = requests.get(URL, allow_redirects=True)
    with open("./download.zip", "wb") as file:
        print(f"Téléchargement de la version {gitversion['version']}.{gitversion['subversion']} en cours...")
        file.write(dl.content)
        print("fin du téléchargement, début de l'extraction...")

    with zipfile.ZipFile("./download.zip") as file:
        file.extractall("./")
        print("fin de l'extraction")

    os.remove("./download.zip")
    print("lancement de l'application...")
    os.startfile(os.path.realpath("./MKWF-Install.exe"))

except Exception as e:
    print(f"Impossible d'effectuer la mise à jour :\n\n{str(e)}")
    input("Appuyez pour continuer...")