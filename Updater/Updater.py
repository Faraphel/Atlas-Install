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

    dl = requests.get(URL, allow_redirects=True, stream=True)
    dl_size = int(dl.headers["Content-Length"])

    with open("./download.zip", "wb") as file:
        print(f"Téléchargement de la version {gitversion['version']}.{gitversion['subversion']} en cours...")
        chunk_size = 1024
        for i, chunk in enumerate(dl.iter_content(chunk_size=chunk_size)):
            progress = int((i * chunk_size * 100) / dl_size)
            print("("+str(progress)+"%) | " + "#" * (progress//5) + "_"* (20 - (progress//5)) + " | " +
                  str(round(i*chunk_size/1000000,1)) + "Mo/" + str(round(dl_size/1000000,1)) + "Mo", end="\r")
            file.write(chunk)
            file.flush()

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