import time
from pathlib import Path
from typing import Generator

from source.mkw.ModConfig import ModConfig
from source.wt.wit import WITPath, Region, Extension


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

    def extract(self, dest: Path | str) -> Generator[dict, None, Path]:
        """
        Extract the game to the destination directory. If the game is a FST, just copy to the destination
        :param dest: destination directory
        """
        gen = self.wit_path.progress_extract_all(dest)
        for gen_data in gen:
            yield {
                "description": f'EXTRACTING - {gen_data["percentage"]}% - (estimated time remaining: '
                               f'{gen_data["estimation"] if gen_data["estimation"] is not None else "-:--"})',

                "maximum": 100,
                "value": gen_data["percentage"],
                "determinate": True
            }
        try: next(gen)
        except StopIteration as e:
            return e.value

    def install_mod(self, dest: Path, mod_config: ModConfig, output_type: Extension) -> Generator[dict, None, None]:
        """
        Patch the game with the mod
        :dest: destination directory
        :mod_config: mod configuration
        :output_type: type of the destination game
        """
        # yield from self.extract(dest / f"{mod_config.nickname} {mod_config.version}")
        print(mod_config.get_ctfile())
        yield {}
