import hashlib
import shutil
from io import BytesIO
from pathlib import Path
from typing import Generator, IO, TYPE_CHECKING

from source import file_block_size
from source.mkw import PathOutsideAllowedRange
from source.mkw.ModConfig import ModConfig
from source.mkw.Patch.Patch import Patch
from source.mkw.collection.Extension import Extension
from source.progress import Progress
from source.utils import comp_dict_changes
from source.wt import szs, lec, wit
from source.wt.wstrt import StrPath
from source.translation import translate as _

if TYPE_CHECKING:
    from source.mkw.Game import Game


RIIVOLUTION_FOLDER_NAME: str = "riivolution"


class ExtractedGame:
    """
    Class that represents an extracted game
    """

    def __init__(self, path: "Path | str", original_game: "Game" = None):
        self.path = Path(path)
        self.original_game = original_game
        self._special_file: dict[str, IO] = {}

    def extract_autoadd(self, destination_path: "Path | str") -> Generator[Progress, None, None]:
        """
        Extract all the autoadd files from the game to destination_path
        :param destination_path: directory where the autoadd files will be extracted
        """
        yield Progress(description=_("TEXT_EXTRACTING_AUTOADD"), determinate=False)
        szs.autoadd(self.path / "files/Race/Course/", destination_path)

    def extract_original_tracks(self, destination_path: "Path | str") -> Generator[Progress, None, None]:
        """
        Move all the original tracks to the destination path
        :param destination_path: destination of the track
        """
        destination_path = Path(destination_path)
        destination_path.mkdir(parents=True, exist_ok=True)

        original_tracks: list[Path] = list((self.path / "files/Race/Course/").glob("*.szs"))
        yield Progress(
            determinate=True,
            max_step=len(original_tracks),
            set_step=0,
        )

        for track_file in original_tracks:
            yield Progress(description=_("TEXT_EXTRACTING_ORIGINAL_TRACKS") % track_file.name, step=1)

            if not (destination_path / track_file.name).exists(): track_file.rename(destination_path / track_file.name)
            else: track_file.unlink()

    def install_mystuff(self, mystuff_path: "Path | str") -> Generator[Progress, None, None]:
        """
        Install mystuff directory. If any files of the game have the same name as a file at the root of the MyStuff
        Patch, then it is copied.
        :mystuff_path: path to the MyStuff directory
        :return:
        """
        yield Progress(description=_("TEXT_INSTALLING_MYSTUFF") % mystuff_path)
        mystuff_path = Path(mystuff_path)

        mystuff_rootfiles: dict[str, Path] = {}
        for mystuff_subpath in mystuff_path.glob("*"):
            if mystuff_subpath.is_file(): mystuff_rootfiles[mystuff_subpath.name] = mystuff_subpath
            else: shutil.copytree(mystuff_subpath, self.path / f"files/{mystuff_subpath.name}", dirs_exist_ok=True)

        for game_file in filter(lambda file: file.is_file(), (self.path / "files/").rglob("*")):
            if (mystuff_file := mystuff_rootfiles.get(game_file.name)) is None: continue
            shutil.copy(mystuff_file, game_file)

    def install_multiple_mystuff(self, mystuff_paths: list["Path | str"]) -> Generator[Progress, None, None]:
        """
        Install multiple mystuff patch
        :param mystuff_paths: paths to all the mystuff patch
        """
        yield Progress(determinate=True, max_step=len(mystuff_paths), set_step=0)

        for mystuff_path in mystuff_paths:
            yield Progress(step=1)
            yield from self.install_mystuff(mystuff_path)

    def prepare_special_file(self, mod_config: ModConfig) -> Generator[Progress, None, None]:
        """
        Prepare special files for the patch
        :return: the special files dict
        """
        yield Progress(description=_("TEXT_PREPARING_SPECIAL_FILE") % "ct_icons", determinate=False)
        ct_icons = BytesIO()
        mod_config.get_full_cticon().save(ct_icons, format="PNG")
        ct_icons.seek(0)
        self._special_file["ct_icons"] = ct_icons

    def prepare_dol(self) -> Generator[Progress, None, None]:
        """
        Prepare main.dol and StaticR.rel files (clean them and add lecode)
        """
        yield Progress(description=_("TEXT_PREPARING_MAIN_DOL"), determinate=False)
        StrPath(self.path / "sys/main.dol").patch(clean_dol=True, add_lecode=True)

    def recreate_all_szs(self) -> Generator[Progress, None, None]:
        """
        Repack all the .d directory into .szs files.
        """
        all_extracted_szs: list[Path] = list(filter(lambda path: path.is_dir(), self.path.rglob("*.d")))
        yield Progress(
            determinate=True,
            max_step=len(all_extracted_szs),
            set_step=0,
        )

        for extracted_szs in all_extracted_szs:
            # for every directory that end with a .d in the extracted game, recreate the szs
            yield Progress(
                description=_("TEXT_REPACKING_ARCHIVE") % extracted_szs.relative_to(self.path),
                step=1
            )

            szs.create(extracted_szs, extracted_szs.with_suffix(".szs"), overwrite=True)
            shutil.rmtree(str(extracted_szs.resolve()))

    def patch_lecode(self, mod_config: ModConfig, cache_directory: Path | str,
                     cttracks_directory: Path | str, ogtracks_directory: Path | str) -> Generator[Progress, None, None]:
        """
        install lecode on the mod
        :param cttracks_directory: directory to the customs tracks
        :param ogtracks_directory: directory to the originals tracks
        :param cache_directory: Path to the cache
        :param mod_config: mod configuration
        """
        yield Progress(description=_("TEXT_PATCHING_LECODE"), determinate=False)
        cache_directory = Path(cache_directory)
        cttracks_directory = Path(cttracks_directory)
        ogtracks_directory = Path(ogtracks_directory)

        # write ctfile data to a file in the cache
        ct_file = (cache_directory / "ctfile.lpar")
        ct_file.write_text(mod_config.get_ctfile(template="-"))

        lpar_dir: Path = mod_config.path.parent / "_LPAR/"
        lpar: Path = lpar_dir / mod_config.multiple_safe_eval(mod_config.lpar_template)()
        if not lpar.is_relative_to(lpar_dir): raise PathOutsideAllowedRange(lpar, lpar_dir)

        for lecode_file in (self.path / "files/rel/").glob("lecode-*.bin"):
            lec.patch(
                lecode_file=lecode_file,
                ct_file=ct_file,
                lpar=lpar,
                game_tracks_directory=self.path / "files/Race/Course/",
                copy_tracks_directories=[ogtracks_directory, cttracks_directory]
            )

    def _install_all_patch(self, mod_config: ModConfig, patch_directory_name: str) -> Generator[Progress, None, None]:
        """
        for all directory that are in the root of the mod, and don't start with an underscore,
        for all the subdirectory named by the patch_directory_name, apply the patch
        :param mod_config: the mod to install
        """
        patch_directories: list[Path] = []
        for part_directory in mod_config.get_mod_directory().glob("[!_]*"):
            for patch_directory in part_directory.glob(patch_directory_name):
                patch_directories.append(patch_directory)

        yield Progress(determinate=True, max_step=len(patch_directories)+1, set_step=0)

        for patch_directory in patch_directories:
            yield Progress(step=1)
            yield from Patch(patch_directory, mod_config, self._special_file).install(self)

    def install_all_prepatch(self, mod_config: ModConfig) -> Generator[Progress, None, None]:
        """
        Install all patchs of the mod_config into the game.
        Used before the lecode patch is applied
        :param mod_config: the mod to install
        """
        yield from self._install_all_patch(mod_config, "_PREPATCH/")

    def install_all_patch(self, mod_config: ModConfig) -> Generator[Progress, None, None]:
        """
        Install all patchs of the mod_config into the game.
        Used after the lecode patch is applied
        :param mod_config: the mod to install
        """
        yield from self._install_all_patch(mod_config, "_PATCH/")

    def convert_to(self, output_type: Extension) -> Generator[Progress, None, wit.WITPath | None]:
        """
        Convert the extracted game to another format
        :param output_type: path to the destination of the game
        :output_type: format of the destination game
        """
        yield Progress(description=_("TEXT_CONVERT_GAME_TO") % output_type.name, determinate=False)
        if output_type == Extension.FST: return

        destination_file = self.path.with_suffix(self.path.suffix + output_type.value)
        dest_stem: str = destination_file.stem

        i: int = 0
        while destination_file.exists():
            i += 1
            destination_file = destination_file.with_stem(dest_stem + f" ({i})")

        converted_game: wit.WITPath = wit.copy(
            source_directory=self.path,
            destination_file=destination_file,
        )

        yield Progress(description=_("TEXT_DELETING_EXTRACTED_GAME"), determinate=False)
        shutil.rmtree(self.path)

        return converted_game

    def convert_to_riivolution(self, mod_config: ModConfig, old_hash_map: dict[str, str]
                               ) -> Generator[Progress, None, None]:
        """
        Convert the extracted game into a riivolution patch
        :param mod_config: the mod configuration
        :param old_hash_map: hash map of all the games files created before all the modifications
        """
        new_hash_map = yield from self.get_hash_map()

        game_files: list[Path] = list(filter(lambda file: file.is_file(), self.path.rglob("*")))
        yield Progress(
            description=_("TEXT_CONVERTING_TO_RIIVOLUTION"),
            determinate=True,
            max_step=len(game_files),
            set_step=0,
        )

        # get the files difference between the original game and the patched game
        diff_hash_map: dict[str, Path] = comp_dict_changes(old_hash_map, new_hash_map)

        for file in game_files:
            yield Progress(step=1)
            # if the file have not being patched, delete it
            if str(file.relative_to(self.path)) not in diff_hash_map:
                file.unlink()

        # get riivolution configuration content
        riivolution_config_content = "\n".join((
            '<wiidisc version="1">',
            '    <id game="RMC" disc="0" version="0"> </id>',
            '',
            '    <options>',
            f'        <section name="{str(mod_config)}">',
            '            <option id="CT" name="Custom Tracks" default="1">',
            '                <choice name="Enabled"> <patch id="mod"/> </choice>',
            '            </option>',
            '            <option id="save_SD" name="Save on SD" default="1">',
            '                <choice name="Enabled"> <patch id="save_SD"/> </choice>',
            '            </option>',
            '            <option id="my_stuff" name="My Stuff" default="1">',
            '                <choice name="Enabled"> <patch id="my_stuff"/> </choice>',
            '            </option>',
            '        </section>',
            '    </options>',
            '',
            '    <patch id="mod">',
            f'        <folder disc="/" external="/{self.path.name}/files/" recursive="true" create="true"/>',
            f'        <folder disc="" external="/{self.path.name}/sys/" recursive="true" create="true"/>',
            '    </patch>',
            '',
            '    <patch id="my_stuff">',
            f'        <folder external="/{RIIVOLUTION_FOLDER_NAME}/MyStuff/" recursive="false"/>',
            f'        <folder external="/{RIIVOLUTION_FOLDER_NAME}/MyStuff/" disc="/"/>',
            '    </patch>',
            '',
            '    <patch id="save_SD">',
            '        <savegame clone="false"',
            f'            external="/{RIIVOLUTION_FOLDER_NAME}/save/{self.original_game.get_patched_gameid(mod_config)}"/>',
            '    </patch>',
            '</wiidisc>',
        ))

        # get riivolution configuration path
        riivolution_config_path: Path = self.path.parent / f"{RIIVOLUTION_FOLDER_NAME}/{str(mod_config)}.xml"
        riivolution_config_path.parent.mkdir(parents=True, exist_ok=True)
        riivolution_config_path.write_text(riivolution_config_content, encoding="utf-8")

    def get_hash_map(self) -> Generator[Progress, None, dict[str, str]]:
        """
        Return a dictionary associating all the game subfiles to a hash
        :return: a dictionary associating all the game subfiles to a hash
        """
        md5_map: dict[str, str] = {}

        game_files: list[Path] = list(filter(lambda fp: fp.is_file(), self.path.rglob("*")))
        yield Progress(
            determinate=True,
            max_step=len(game_files),
            set_step=0
        )

        for fp in game_files:
            hasher = hashlib.md5()
            rel_path: str = str(fp.relative_to(self.path))

            yield Progress(
                description=_("TEXT_CALCULATING_HASH") % rel_path,
                step=1
            )

            with open(fp, "rb") as file:
                while block := file.read(file_block_size):
                    hasher.update(block)
            md5_map[rel_path] = hasher.hexdigest()

        return md5_map
