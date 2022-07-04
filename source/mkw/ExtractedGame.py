from pathlib import Path
from typing import Generator

from source.mkw.ModConfig import ModConfig
from source.mkw.Patch.Patch import Patch
from source.wt import szs


class ExtractedGame:
    """
    Class that represents an extracted game
    """

    def __init__(self, path: Path | str, original_game: "Game" = None):
        self.path = Path(path)
        self.original_game = original_game

    def extract_autoadd(self, destination_path: Path | str) -> Generator[dict, None, None]:
        """
        Extract all the autoadd files from the game to destination_path
        :param destination_path: directory where the autoadd files will be extracted
        :return: directory where the autoadd files were extracted
        """
        yield {"description": "Extracting autoadd files...", "determinate": False}
        szs.autoadd(self.path / "files/Race/Course/", destination_path)

    def install_mystuff(self) -> Generator[dict, None, None]:
        """
        Install mystuff directory
        :return:
        """
        yield {"description": "Installing MyStuff directory...", "determinate": False}
        ...

    def install_all_patch(self, mod_config: ModConfig) -> Generator[dict, None, None]:
        """
        Install all patchs of the mod_config into the game
        :param mod_config: the mod to install
        :return:
        """
        yield {"description": "Installing all Patch...", "determinate": False}

        # for all directory that are in the root of the mod, and don't start with an underscore,
        # for all the subdirectory named "_PATCH", apply the patch
        for part_directory in mod_config.get_mod_directory().glob("[!_]*"):
            for patch_directory in part_directory.glob("_PATCH/"):
                yield from Patch(patch_directory).install(self)
