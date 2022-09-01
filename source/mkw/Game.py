from pathlib import Path
from typing import Generator

from source.mkw.ExtractedGame import ExtractedGame
from source.mkw.ModConfig import ModConfig
from source.mkw.collection.Extension import Extension
from source.mkw.collection.Region import Region
from source.option import Options
from source.progress import Progress
from source.wt.wit import WITPath
from source.translation import translate as _


class NotMKWGameError(Exception):
    def __init__(self, path: "Path | str"):
        super().__init__(_("ERROR_NOT_MKW_GAME") % Path(path).name)


class NotVanillaError(Exception):
    def __init__(self, path: "Path | str"):
        super().__init__(_("ERROR_GAME_ALREADY_MODDED") % Path(path).name)


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

    def extract(self, dest: "Path | str") -> Generator[Progress, None, Path]:
        """
        Extract the game to the destination directory. If the game is a FST, just copy to the destination
        :param dest: destination directory
        """
        gen = self.wit_path.progress_extract_all(dest)

        if self.wit_path.extension == Extension.FST:
            for __ in gen: yield Progress(description=_("TEXT_COPYING_GAME"), determinate=False)
            try: next(gen)
            except StopIteration as e: return e.value

        else:
            yield Progress(determinate=True, max_step=100)

            for gen_data in gen:
                percentage: int = gen_data["percentage"]
                estimation: str = gen_data["estimation"] if gen_data["estimation"] is not None else "-:--"

                yield Progress(
                    description=_("TEXT_EXTRACTING_GAME") % (percentage, estimation),
                    set_step=percentage,
                )

            try: next(gen)
            except StopIteration as e:
                return e.value

    def edit(self, mod_config: ModConfig) -> Generator[Progress, None, None]:
        yield Progress(description=_("TEXT_CHANGING_GAME_METADATA"), determinate=False)
        self.wit_path.edit(
            name=mod_config.name,
            game_id=self.wit_path.id[:4] + mod_config.variant
        )

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

    def install_mod(self, dest: Path, mod_config: ModConfig, options: "Options", output_type: Extension
                    ) -> Generator[Progress, None, None]:
        """
        Patch the game with the mod
        :dest: destination directory
        :mod_config: mod configuration
        :options: others options for customized installation
        :output_type: type of the destination game
        """
        yield Progress(max_part=8)

        # create a cache directory for some files
        cache_directory: Path = Path("./.cache")
        cache_directory.mkdir(parents=True, exist_ok=True)

        cache_autoadd_directory = cache_directory / "autoadd/"
        cache_ogtracks_directory = cache_directory / "original-tracks/"
        cache_cttracks_directory = cache_directory / f"custom-tracks/{mod_config}/"

        # get the directory where the game will be extracted
        extracted_game = ExtractedGame(self.get_output_directory(dest, mod_config), self)

        if not self.is_mkw(): raise NotMKWGameError(self.wit_path.path)
        if not self.is_vanilla(): raise NotVanillaError(self.wit_path.path)

        # extract the game
        yield Progress(title=_("PART_EXTRACTION"), set_part=1)
        yield from self.extract(extracted_game.path)

        # Get the original file hash map for comparaison with the post-patched game
        yield Progress(title=_("PART_PRE_RIIVOLUTION"), set_part=2)
        riivolution_original_hash_map: dict[str, str] | None = None
        if output_type.is_riivolution():
            riivolution_original_hash_map = yield from extracted_game.get_hash_map()

        # install mystuff
        yield Progress(title=_("PART_MYSTUFF"), set_part=3)
        mystuff_packs = options.mystuff_packs.get()
        mystuff_data = mystuff_packs.get(options.mystuff_pack_selected.get())
        if mystuff_data is not None: yield from extracted_game.install_multiple_mystuff(mystuff_data["paths"])

        # prepare the cache
        yield Progress(title=_("PART_PREPARING_FILES"), set_part=4)
        yield from extracted_game.extract_autoadd(cache_autoadd_directory)
        yield from extracted_game.extract_original_tracks(cache_ogtracks_directory)
        yield from mod_config.normalize_all_tracks(
            cache_autoadd_directory,
            cache_cttracks_directory,
            cache_ogtracks_directory,
            options.threads.get(),
        )
        yield from extracted_game.prepare_dol()
        yield from extracted_game.prepare_special_file(mod_config)

        # prepatch the game
        yield Progress(title=_("PART_PREPATCH"), set_part=5)
        yield from extracted_game.install_all_prepatch(mod_config)

        yield Progress(title=_("PART_LECODE"), set_part=6)
        yield from extracted_game.patch_lecode(  # PROGRESS
            mod_config,
            cache_directory,
            cache_cttracks_directory,
            cache_ogtracks_directory,
        )

        yield Progress(title=_("PART_PATCH"), set_part=7)
        yield from extracted_game.install_all_patch(mod_config)
        yield from extracted_game.recreate_all_szs()

        if output_type.is_riivolution():
            yield Progress(title=_("PART_RIIVOLUTION"), set_part=8)
            yield from extracted_game.convert_to_riivolution(mod_config, riivolution_original_hash_map)

        else:
            # convert the extracted game into a file
            yield Progress(title=_("PART_CONVERSION"), set_part=8)
            converted_game: WITPath = yield from extracted_game.convert_to(output_type)
            if converted_game is not None: yield from Game(converted_game.path).edit(mod_config)

