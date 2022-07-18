import shutil
from io import BytesIO
from pathlib import Path
from typing import Generator, IO

from source.mkw.ModConfig import ModConfig
from source.mkw.Patch.Patch import Patch
from source.wt import szs
from source.wt.wstrt import StrPath


class ExtractedGame:
    """
    Class that represents an extracted game
    """

    def __init__(self, path: "Path | str", original_game: "Game" = None):
        self.path = Path(path)
        self.original_game = original_game
        self._special_file: dict[str, IO] = {}

    def extract_autoadd(self, destination_path: "Path | str") -> Generator[dict, None, None]:
        """
        Extract all the autoadd files from the game to destination_path
        :param destination_path: directory where the autoadd files will be extracted
        """
        yield {"description": "Extracting autoadd files...", "determinate": False}
        szs.autoadd(self.path / "files/Race/Course/", destination_path)

    def extract_original_tracks(self, destination_path: "Path | str") -> Generator[dict, None, None]:
        """
        Move all the original tracks to the destination path
        :param destination_path: destination of the track
        """
        destination_path = Path(destination_path)
        destination_path.mkdir(parents=True, exist_ok=True)
        yield {"description": "Extracting original tracks...", "determinate": False}
        for track_file in (self.path / "files/Race/Course/").glob("*.szs"):
            track_file.rename(destination_path / track_file.name)

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

    def prepare_dol(self) -> Generator[dict, None, None]:
        """
        Prepare main.dol and StaticR.rel files (clean them and add lecode)
        """
        yield {"description": "Preparing main.dol...", "determinate": False}
        StrPath(self.path / "sys/main.dol").patch(clean_dol=True, add_lecode=True)

    def recreate_all_szs(self) -> Generator[dict, None, None]:
        """
        Repack all the .d directory into .szs files.
        """
        yield {"description": f"Repacking all szs", "determinate": False}

        for extracted_szs in filter(lambda path: path.is_dir(), self.path.rglob("*.d")):
            # for every directory that end with a .d in the extracted game, recreate the szs
            yield {"description": f"Repacking {extracted_szs} to szs", "determinate": False}

            szs.create(extracted_szs, extracted_szs.with_suffix(".szs"), overwrite=True)
            shutil.rmtree(str(extracted_szs.resolve()))

    def install_all_patch(self, mod_config: ModConfig) -> Generator[dict, None, None]:
        """
        Install all patchs of the mod_config into the game
        :param mod_config: the mod to install
        """
        yield {"description": "Installing all Patch...", "determinate": False}

        # prepare special files data
        yield from self.prepare_special_file(mod_config)

        # for all directory that are in the root of the mod, and don't start with an underscore,
        # for all the subdirectory named "_PATCH", apply the patch
        for part_directory in mod_config.get_mod_directory().glob("[!_]*"):
            for patch_directory in part_directory.glob("_PATCH/"):
                yield from Patch(patch_directory, mod_config, self._special_file).install(self)

