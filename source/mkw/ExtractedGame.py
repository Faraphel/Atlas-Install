from io import BytesIO
from pathlib import Path
from typing import Generator, IO

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
        self._special_file: dict[str, IO] = {}

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
        # TODO: implement mystuff

    def prepare_special_file(self, mod_config: ModConfig) -> Generator[dict, None, None]:
        """
        Prepare special files for the patch
        :return: the special files dict
        """
        yield {"description": "Preparing ct_icon special file...", "determinate": False}
        ct_icons = BytesIO()
        mod_config.get_full_cticon().save(ct_icons, format="PNG")
        ct_icons.seek(0)
        self._special_file["ct_icon"] = ct_icons

    def install_all_patch(self, mod_config: ModConfig) -> Generator[dict, None, None]:
        """
        Install all patchs of the mod_config into the game
        :param special_file: special file that can be used to patch the game
        :param mod_config: the mod to install
        :return:
        """
        yield {"description": "Installing all Patch...", "determinate": False}

        # prepare special files data
        yield from self.prepare_special_file(mod_config)

        # for all directory that are in the root of the mod, and don't start with an underscore,
        # for all the subdirectory named "_PATCH", apply the patch
        for part_directory in mod_config.get_mod_directory().glob("[!_]*"):
            for patch_directory in part_directory.glob("_PATCH/"):
                yield from Patch(patch_directory, mod_config, self._special_file).install(self)
