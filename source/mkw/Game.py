from pathlib import Path
from typing import Generator

from source.mkw.ExtractedGame import ExtractedGame
from source.mkw.ModConfig import ModConfig
from source.wt.wit import WITPath, Region, Extension


class NotMKWGameError(Exception):
    def __init__(self, path: "Path | str"):
        path = Path(path)
        super().__init__(f'Not a Mario Kart Wii game : "{path.name}"')


class NotVanillaError(Exception):
    def __init__(self, path: "Path | str"):
        path = Path(path)
        super().__init__(f'This game is already modded : "{path.name}"')


class Game:
    def __init__(self, path: "Path | str"):
        self.wit_path = WITPath(path)

    def is_mkw(self) -> bool:
        """
        Return True if the game is Mario Kart Wii, False otherwise
        :return: is the game a MKW game
        """
        return self.wit_path.analyze().get("dol_is_mkw") == 1

    def is_vanilla(self) -> bool:
        """
        Return True if the game is vanilla, False if the game is modded
        :return: if the game is not modded
        """
        return not any(self.wit_path[f"./files/rel/lecode-{region.value}.bin"].exists() for region in Region)

    def extract(self, dest: "Path | str") -> Generator[dict, None, Path]:
        """
        Extract the game to the destination directory. If the game is a FST, just copy to the destination
        :param dest: destination directory
        """
        gen = self.wit_path.progress_extract_all(dest)

        if self.wit_path.extension == Extension.FST:
            for gen_data in gen:
                yield {
                    "description": "Copying Game...",
                    "determinate": False
                }
            try: next(gen)
            except StopIteration as e:
                return e.value

        else:
            for gen_data in gen:
                yield {
                    "description": f'Extracting - {gen_data["percentage"]}% - (estimated time remaining: '
                                   f'{gen_data["estimation"] if gen_data["estimation"] is not None else "-:--"})',
                    "maximum": 100,
                    "value": gen_data["percentage"],
                    "determinate": True
                }
            try: next(gen)
            except StopIteration as e:
                return e.value

    @staticmethod
    def get_output_directory(dest: "Path | str", mod_config: ModConfig) -> Path:
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

        cache_autoadd_directory = cache_directory / "autoadd/"
        cache_ogtracks_directory = cache_directory / "original-tracks/"
        cache_cttracks_directory = cache_directory / f"custom-tracks/"

        # get the directory where the game will be extracted
        extracted_game = ExtractedGame(self.get_output_directory(dest, mod_config), self)

        if not self.is_mkw(): raise NotMKWGameError(self.wit_path.path)
        if not self.is_vanilla(): raise NotVanillaError(self.wit_path.path)

        # extract the game
        yield from self.extract(extracted_game.path)

        # prepare the cache
        # TODO: normalize all tracks should get the threads amount changeable
        yield from extracted_game.extract_autoadd(cache_autoadd_directory)
        yield from extracted_game.extract_original_tracks(cache_ogtracks_directory)
        yield from mod_config.normalize_all_tracks(cache_autoadd_directory, cache_cttracks_directory)

        # patch the game
        yield from extracted_game.install_mystuff()
        yield from extracted_game.prepare_dol()
        yield from extracted_game.install_all_patch(mod_config)
        yield from extracted_game.recreate_all_szs()

