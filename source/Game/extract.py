import glob
import os

from .exception import *
from source.definition import *
from source import wszst


def extract(self):
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

    with open(self.path + "/setup.txt") as f:
        setup = f.read()
    setup = setup[setup.find("!part-id = ") + len("!part-id = "):]
    self.game_ID = setup[:setup.find("\n")]

    self.region_ID = self.game_ID[3]
    self.region = region_id_to_name[self.region_ID] if self.region_ID in region_id_to_name else self.region