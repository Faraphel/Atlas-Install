from pathlib import Path
from typing import Generator

from source.mkw.ModConfig import ModConfig
from source.wt import szs
from source.wt.wit import WITPath, Region, Extension


def extract_autoadd(extracted_game: Path | str, destination_path: Path | str) -> Path:
    """
    Extract all the autoadd files from the game to destination_path
    :param extracted_game: path of the extracted game
    :param destination_path: directory where the autoadd files will be extracted
    :return: directory where the autoadd files were extracted
    """
    yield {"description": "Extracting autoadd files...", "determinate": False}
    szs.autoadd(extracted_game / "files/Race/Course/", destination_path)


def install_mystuff(extracted_game: Path | str) -> None:
    """
    Install mystuff directory
    :param extracted_game: the extracted game
    :return:
    """
    yield {"description": "Installing MyStuff directory...", "determinate": False}



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

    def get_output_directory(self, dest: Path | str, mod_config: ModConfig) -> Path:
        """
        Return the directory where the game will be installed
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
        extracted_game: Path = self.get_output_directory(dest, mod_config)

        yield from self.extract(extracted_game)
        yield from extract_autoadd(extracted_game, cache_directory / "autoadd/")
        yield from install_mystuff(extracted_game)

