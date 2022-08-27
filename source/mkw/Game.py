from pathlib import Path
from typing import Generator

from source.mkw.ExtractedGame import ExtractedGame
from source.mkw.ModConfig import ModConfig
from source.mkw.collection.Extension import Extension
from source.mkw.collection.Region import Region
from source.option import Options
from source.progress import Progress
from source.utils import comp_dict_changes
from source.wt.wit import WITPath
from source.translation import translate as _


class NotMKWGameError(Exception):
    def __init__(self, path: "Path | str"):
        path = Path(path)
        super().__init__(_("NOT_MKW_GAME", ' : "', path.name, '"'))


class NotVanillaError(Exception):
    def __init__(self, path: "Path | str"):
        path = Path(path)
        super().__init__(_("GAME_ALREADY_MODDED", ' : "', path.name, '"'))


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
            for __ in gen: yield Progress(description=_("COPYING_GAME"), determinate=False)
            try: next(gen)
            except StopIteration as e: return e.value

        else:
            for gen_data in gen:
                yield Progress(
                    description=_("EXTRACTING", " - ", gen_data["percentage"], "% - (", "ESTIMATED_TIME_REMAINING", ": "
                                  f'{gen_data["estimation"] if gen_data["estimation"] is not None else "-:--"})'),
                    max_step=100,
                    set_step=gen_data["percentage"],
                    determinate=True
                )
            try: next(gen)
            except StopIteration as e:
                return e.value

    def edit(self, mod_config: ModConfig) -> Generator[Progress, None, None]:
        yield Progress(description=_("CHANGING_GAME_METADATA"), determinate=False)
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
        yield Progress(title=_("EXTRACTION"), set_part=1)
        yield from self.extract(extracted_game.path)

        # Riivolution hash map for the final comparaison
        yield Progress(title=_("PREPARING_RIIVOLUTION"), set_part=2,
                       description=_("PREPARING_RIIVOLUTION"), determinate=False)
        if output_type.is_riivolution(): riivolution_original_hash_map = extracted_game.get_hash_map()

        # install mystuff
        yield Progress(title=_("MYSTUFF"), set_part=3)
        mystuff_packs = options.mystuff_packs.get()
        mystuff_data = mystuff_packs.get(options.mystuff_pack_selected.get())
        if mystuff_data is not None: yield from extracted_game.install_multiple_mystuff(mystuff_data["paths"])

        # prepare the cache
        yield Progress(title=_("PREPARING_FILES"), set_part=4)
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
        yield Progress(title=_("PRE-PATCHING"), set_part=5)
        yield from extracted_game.install_all_prepatch(mod_config)

        yield Progress(title="LE-CODE", set_part=6)
        yield from extracted_game.patch_lecode(
            mod_config,
            cache_directory,
            cache_cttracks_directory,
            cache_ogtracks_directory,
        )

        yield Progress(title=_("PATCHING"), set_part=7)
        yield from extracted_game.install_all_patch(mod_config)
        yield from extracted_game.recreate_all_szs()

        if output_type.is_riivolution():
            # Riivolution comparaison
            riivolution_patched_hash_map = extracted_game.get_hash_map()
            riivolution_diff: dict[str, Path] = comp_dict_changes(
                riivolution_original_hash_map,
                riivolution_patched_hash_map
            )

            for file in filter(lambda file: file.is_file(), extracted_game.path.rglob("*")):
                # if the file have not being patched, delete it
                if str(file.relative_to(extracted_game.path)) not in riivolution_diff:
                    file.unlink()

            # get riivolution configuration content
            riivolution_config_content = f"""
<wiidisc version="1">
    <id game="RMC" disc="0" version="0">
        <region type="P"/>
        <region type="J"/>
        <region type="E"/>
        <region type="K"/>
    </id>
    
    <options>
        <section name="{str(mod_config)}">
            <option id="CT" name="Custom Tracks" default="1">
                <choice name="Enabled"> <patch id="mod"/> </choice>
            </option>
            <option id="save_SD" name="Save on SD" default="1">
                <choice name="Enabled"> <patch id="save_SD"/> </choice>
            </option>
            <option id="my_stuff" name="My Stuff" default="1">
                <choice name="Enabled"> <patch id="my_stuff"/> </choice>
            </option>
        </section>
    </options>
    
    <patch id="mod">
        <folder disc="/" external="/{extracted_game.path.name}/files/" recursive="true" create="true"/>
        <folder disc="" external="/{extracted_game.path.name}/sys/" recursive="true" create="true"/>
    </patch>
    
    <patch id="my_stuff">
        <folder external="/riivolution/MyStuff/" recursive="false"/>
        <folder external="/riivolution/MyStuff/" disc="/"/>
    </patch>
    
    <patch id="save_SD">
        <savegame clone="false" external="/riivolution/save/{'{$__gameid}{$__region}'}{mod_config.variant}"/>
    </patch>
</wiidisc>
            """

            # get riivolution configuration path
            riivolution_config_path = extracted_game.path.parent / f"riivolution/{str(mod_config)}.xml"
            riivolution_config_path.parent.mkdir(parents=True, exist_ok=True)
            riivolution_config_path.write_text(riivolution_config_content, encoding="utf8")

        else:
            # convert the extracted game into a file
            yield Progress(title=_("CONVERTING_TO_GAME_FILE"), set_part=8)
            converted_game: WITPath = yield from extracted_game.convert_to(output_type)
            if converted_game is not None: yield from Game(converted_game.path).edit(mod_config)

