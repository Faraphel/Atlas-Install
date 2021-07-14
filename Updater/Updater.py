import requests
import zipfile
import os
import sys

Dir, ext = os.path.splitext(sys.argv[0])
if ext == ".py":
    input("This code need to be started from its .exe version !")
    exit()

VERSION_FILE_URL = "https://raw.githubusercontent.com/Faraphel/MKWF-Install/master/version"

try:
    gitversion = requests.get(VERSION_FILE_URL, allow_redirects=True).json()
    URL = gitversion["download_bin"]

    dl = requests.get(URL, allow_redirects=True, stream=True)
    dl_size = int(dl.headers["Content-Length"])

    with open("./download.zip", "wb") as file:
        print(f"Downloading version {gitversion['version']}.{gitversion['subversion']}...")
        chunk_size = 1024
        for i, chunk in enumerate(dl.iter_content(chunk_size=chunk_size)):
            progress = int((i * chunk_size * 100) / dl_size)
            print("("+str(progress)+"%) | " + "#" * (progress//5) + "_" * (20 - (progress//5)) + " | " +
                  str(round(i*chunk_size/1000000,1)) + "Mo/" + str(round(dl_size/1000000,1)) + "Mo" + " " * 10,
                  end="\r")
            file.write(chunk)
            file.flush()

        print("end of the download, starting extraction..." + (" " * 10))

    with zipfile.ZipFile("./download.zip") as file:
        file.extractall("./")
        print("end of extraction")

    os.remove("./download.zip")
    print("restarting application...")
    os.startfile(os.path.realpath("./MKWF-Install.exe"))

except Exception as e:
    print(f"Can't update :\n\n{str(e)}")
    input("Press to close...")
