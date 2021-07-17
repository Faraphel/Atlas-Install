from tkinter import messagebox
import requests
import zipfile
import json
import os

from .definition import *


def check_update(self):
    try:
        gitversion = requests.get(VERSION_FILE_URL, allow_redirects=True).json()
        with open("./version", "rb") as f:
            locversion = json.load(f)

        if ((float(gitversion["version"]) > float(locversion["version"])) or   # if github version is newer than
           (float(gitversion["version"]) == float(locversion["version"])) and  # local version
                float(gitversion["subversion"]) > float(locversion["subversion"])):
            if messagebox.askyesno(
                    self.translate("Update available !"),
                    self.translate("An update is available, do you want to install it ?",
                                   f"\n\nVersion : {locversion['version']}.{locversion['subversion']} -> "
                                   f"{gitversion['version']}.{gitversion['subversion']}\n"
                                   f"Changelog :\n{gitversion['changelog']}")):

                if not(os.path.exists("./Updater/Updater.exe")):
                    dl = requests.get(gitversion["updater_bin"], allow_redirects=True)
                    with open("./download.zip", "wb") as file:
                        print(self.translate("Downloading the Updater..."))
                        file.write(dl.content)
                        print(self.translate("end of the download, extracting..."))

                    with zipfile.ZipFile("./download.zip") as file:
                        file.extractall("./Updater/")
                        print(self.translate("finished extracting"))

                    os.remove("./download.zip")
                    print(self.translate("starting application..."))
                    os.startfile(os.path.realpath("./Updater/Updater.exe"))

            if ((float(gitversion["version"]) < float(locversion["version"])) or        # if local version is newer than
                    (float(gitversion["version"]) == float(locversion["version"])) and  # github version
                    float(gitversion["subversion"]) < float(locversion["subversion"])):
                self.is_dev_version = True

    except requests.ConnectionError:
        messagebox.showwarning(self.translate("Warning"),
                               self.translate("Can't connect to internet. Download will be disabled."))
        self.option.disable_download = True

    except: self.log_error()
