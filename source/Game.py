from . import wszst
from .definition import *
import glob
import os


class Game:
    def __init__(self, path: str, region: str = "PAL", game_ID: str = "RMCP01"):
        self.extension = get_extension(path)
        self.path = path
        self.region_ID = region_ID[region]
        self.region = region
        self.game_ID = game_ID

    def extract_game(self):
        if self.extension.upper() == "DOL":
            self.path = os.path.realpath(self.path + "/../../")  # main.dol is in PATH/sys/, so go back 2 dir upper

        elif self.extension.upper() in ["ISO", "WBFS", "CSIO"]:
            # Fiding a directory name that doesn't already exist
            directory_name, i = "MKWiiFaraphel", 1
            while True:
                self.path = os.path.realpath(self.path + f"/../{directory_name}")
                if not (os.path.exists(self.path)): break
                directory_name, i = f"MKWiiFaraphel ({i})", i + 1

            wszst.extract(self.path, self.path)
            if os.path.exists(self.path + "/DATA"): self.path += "/DATA"
            self.extension = "DOL"

        else:
            raise Exception("This format is not supported !")

        if glob.glob(self.path + "/files/rel/lecode-???.bin"):  # if a LECODE file is already here
            raise Warning("ROM Already patched")  # warning already patched

        with open(self.path + "/setup.txt") as f: setup = f.read()
        setup = setup[setup.find("!part-id = ") + len("!part-id = "):]
        self.game_ID = setup[:setup.find("\n")]

        self.region_ID = self.game_ID[3]
        self.region = region_ID[self.region_ID] if self.region_ID in region_ID else self.region

    def install_mod(self):
        pass

    def convert_to(self, format: str = "FST"):
        """
        :param format: game format (ISO, WBFS, ...)
        :return: converted game path
        """