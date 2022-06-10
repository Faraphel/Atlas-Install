from pathlib import Path

from source.wt.wit import WITPath, Region


class Game:
    def __init__(self, path: Path | str):
        self.wit_path = WITPath(path)

    def is_mkw(self) -> bool:
        """
        Return True if the game is Mario Kart Wii, False otherwise
        :return: is the game a MKW game
        """
        return self.wit_path.analyze()["dol_is_mkw"] == 1

    def is_vanilla(self) -> bool:
        """
        Return True if the game is vanilla, False if the game is modded
        :return: if the game is not modded
        """
        return not any(self.wit_path[f"./files/rel/lecode-{region.value}.bin"].exists() for region in Region)

    def extract(self, dest: Path | str) -> Path:
        """
        Extract the game to the destination directory. If the game is a FST, just copy to the destination
        :param dest: destination directory
        """
        return self.wit_path.extract_all(dest)
