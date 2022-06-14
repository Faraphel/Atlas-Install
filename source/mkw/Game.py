import json
from pathlib import Path
from typing import Generator

from source.mkw.ModConfig import ModConfig
from source.wt import szs
from source.wt.wit import WITPath, Region, Extension


class ExtractedGame:
    """
    Class that represents an extracted game
    """
    def __init__(self, path: Path | str):
        self.path = Path(path)

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

    def install_file(self, mod_config: ModConfig, patch_directory: Path | str, subfile: Path | str) \
            -> Generator[dict, None, None]:
        """
        Install a file into the game
        :param patch_directory: patch_directory where the subfile is located
        :param subfile: subfile to install
        :param mod_config: the mod to install
        """
        subfile = Path(subfile)
        yield {"description": f"Installing {subfile.name}...", "determinate": False}

        configuration = {}
        configuration_path = subfile.with_suffix(subfile.suffix + ".json")
        if configuration_path.exists(): configuration |= json.loads(configuration_path.read_text(encoding="utf8"))

    def install_patch(self, mod_config: ModConfig, patch_directory: Path | str) -> Generator[dict, None, None]:
        """
        Install a patch into the game
        :param mod_config: the mod to install
        :param patch_directory: directory containing the patch
        """
        patch_directory = Path(patch_directory)
        yield {"description": f"Installing Patch {patch_directory.parent.name}...", "determinate": False}

        for subfile in filter(lambda sf: sf.suffix == ".json", patch_directory.rglob("*")):
            self.install_file(mod_config, subfile)

    def install_all_patch(self, mod_config: ModConfig) -> Generator[dict, None, None]:
        """
        Install all patchs of the mod_config into the game
        :param mod_config: the mod to install
        :return:
        """
        yield {"description": "Installing all Patch...", "determinate": False}

        # for all directory that are in the root of the mod, and don't start with an underscore,
        # for all of the subdirectory named "_PATCH", apply the patch
        for patch_directory in mod_config.get_mod_directory().glob("[!_]*").rglob("_PATCH/"):
            self.install_patch(mod_config, patch_directory)


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

    @staticmethod
    def get_output_directory(dest: Path | str, mod_config: ModConfig) -> Path:
        """
        Return the directory where the game will be installed
        :param dest: destination directory
        :param mod_config: mod configuration
        :return: directory where the game will be installed
        """
        dest = Path(dest)

        extracted_game: Path = Path(dest / f"{mod_config.nickname} {mod_config.version}")
        dest_name: str = extracted_game.name

        # if the directory already exist, add a number to the name
        i: int = 0
        while extracted_game.exists():
            i += 1
            extracted_game = extracted_game.with_name(dest_name + f" ({i})")

        return extracted_game

    def install_mod(self, dest: Path, mod_config: ModConfig, output_type: Extension) -> Generator[dict, None, None]:
        """
        Patch the game with the mod
        :dest: destination directory
        :mod_config: mod configuration
        :output_type: type of the destination game
        """
        # create a cache directory for some files
        cache_directory: Path = Path("./.cache")
        cache_directory.mkdir(parents=True, exist_ok=True)

        # get the directory where the game will be extracted
        extracted_game = ExtractedGame(self.get_output_directory(dest, mod_config))

        yield from self.extract(extracted_game.path)
        yield from extracted_game.extract_autoadd(cache_directory / "autoadd/")
        yield from extracted_game.install_mystuff()
        yield from extracted_game.install_all_patch(mod_config)

