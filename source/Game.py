from . import wszst
from .definition import *
import glob
import os

region_id_to_name = {
    "J": "JAP",
    "P": "PAL",
    "K": "KO",
    "E": "USA"
}

class InvalidGamePath(Exception):
    def __init__(self):
        super().__init__("This path is not valid !")


class InvalidFormat(Exception):
    def __init__(self):
        super().__init__("This game format is not supported !")


class Game:
    def __init__(self, path: str, region_ID: str = "P", game_ID: str = "RMCP01"):
        if not os.path.exists(path): raise InvalidGamePath()
        self.extension = get_extension(path).upper()
        self.path = path
        self.region = region_id_to_name[region_ID]
        self.region_ID = region_ID
        self.game_ID = game_ID

    def extract_game(self):
        if self.extension == "DOL":
            self.path = os.path.realpath(self.path + "/../../")  # main.dol is in PATH/sys/, so go back 2 dir upper

        elif self.extension in ["ISO", "WBFS", "CSIO"]:
            # Fiding a directory name that doesn't already exist
            directory_name, i = "MKWiiFaraphel", 1
            while True:
                path_dir = os.path.realpath(self.path + f"/../{directory_name}")
                if not (os.path.exists(path_dir)): break
                directory_name, i = f"MKWiiFaraphel ({i})", i + 1

            wszst.extract(self.path, path_dir)

            self.path = path_dir
            if os.path.exists(self.path + "/DATA"): self.path += "/DATA"
            self.extension = "DOL"

        else:
            raise InvalidFormat()

        if glob.glob(self.path + "/files/rel/lecode-???.bin"):  # if a LECODE file is already here
            raise Warning("ROM Already patched")  # warning already patched

        with open(self.path + "/setup.txt") as f: setup = f.read()
        setup = setup[setup.find("!part-id = ") + len("!part-id = "):]
        self.game_ID = setup[:setup.find("\n")]

        self.region_ID = self.game_ID[3]
        self.region = region_id_to_name[self.region_ID] if self.region_ID in region_id_to_name else self.region

    def install_mod(self):
        pass

    def convert_to(self, format: str = "FST"):
        """
        :param format: game format (ISO, WBFS, ...)
        :return: converted game path
        """