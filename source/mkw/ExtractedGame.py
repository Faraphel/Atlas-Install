import shutil
from io import BytesIO
from pathlib import Path
from typing import Generator, IO, TYPE_CHECKING

from source.mkw.ModConfig import ModConfig
from source.mkw.Patch.Patch import Patch
from source.progress import Progress
from source.wt import szs, lec, wit
from source.wt.wstrt import StrPath

if TYPE_CHECKING:
    from source.mkw.Game import Game


class PathOutsideMod(Exception):
    def __init__(self, forbidden_path: Path, allowed_range: Path):
        super().__init__(f"Error : path {forbidden_path} outside of allowed range {allowed_range}")


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
        yield Progress(description="Extracting autoadd files...", determinate=False)
        szs.autoadd(self.path / "files/Race/Course/", destination_path)

    def extract_original_tracks(self, destination_path: "Path | str") -> Generator[Progress, None, None]:
        """
        Move all the original tracks to the destination path
        :param destination_path: destination of the track
        """
        destination_path = Path(destination_path)
        destination_path.mkdir(parents=True, exist_ok=True)
        yield Progress(description="Extracting original tracks...", determinate=False)
        for track_file in (self.path / "files/Race/Course/").glob("*.szs"):
            yield Progress(description=f"Extracting original tracks ({track_file.name})...", determinate=False)
            if not (destination_path / track_file.name).exists(): track_file.rename(destination_path / track_file.name)
            else: track_file.unlink()

    def install_mystuff(self, mystuff_path: "Path | str") -> Generator[Progress, None, None]:
        """
        Install mystuff directory. If any files of the game have the same name as a file at the root of the MyStuff
        Patch, then it is copied.
        :mystuff_path: path to the MyStuff directory
        :return:
        """
        yield Progress(description=f"Installing MyStuff '{mystuff_path}'...", determinate=False)
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
        yield Progress(description="Installing all the mystuff patchs")

        for mystuff_path in mystuff_paths:
            yield from self.install_mystuff(mystuff_path)

    def prepare_special_file(self, mod_config: ModConfig) -> Generator[Progress, None, None]:
        """
        Prepare special files for the patch
        :return: the special files dict
        """
        yield Progress(description="Preparing ct_icon special file...", determinate=False)
        ct_icons = BytesIO()
        mod_config.get_full_cticon().save(ct_icons, format="PNG")
        ct_icons.seek(0)
        self._special_file["ct_icons"] = ct_icons

    def prepare_dol(self) -> Generator[Progress, None, None]:
        """
        Prepare main.dol and StaticR.rel files (clean them and add lecode)
        """
        yield Progress(description="Preparing main.dol...", determinate=False)
        StrPath(self.path / "sys/main.dol").patch(clean_dol=True, add_lecode=True)

    def recreate_all_szs(self) -> Generator[Progress, None, None]:
        """
        Repack all the .d directory into .szs files.
        """
        yield Progress(description=f"Repacking all szs", determinate=False)

        for extracted_szs in filter(lambda path: path.is_dir(), self.path.rglob("*.d")):
            # for every directory that end with a .d in the extracted game, recreate the szs
            yield Progress(description=f"Repacking {extracted_szs} to szs", determinate=False)

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
        yield Progress(description="Patching LECODE.bin")
        cache_directory = Path(cache_directory)
        cttracks_directory = Path(cttracks_directory)
        ogtracks_directory = Path(ogtracks_directory)

        # write ctfile data to a file in the cache
        ct_file = (cache_directory / "ctfile.lpar")
        ct_file.write_text(mod_config.get_ctfile(template="-"))

        lpar_dir: Path = mod_config.path.parent / "_LPAR/"
        lpar: Path = lpar_dir / mod_config.multiple_safe_eval(mod_config.lpar_template)()
        if not lpar.is_relative_to(lpar_dir): raise PathOutsideMod(lpar, lpar_dir)

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
        # yield an empty dict so that if nothing is yielded by the Patch, still is considered a generator
        yield Progress()

        for part_directory in mod_config.get_mod_directory().glob("[!_]*"):
            for patch_directory in part_directory.glob(patch_directory_name):
                yield from Patch(patch_directory, mod_config, self._special_file).install(self)

    def install_all_prepatch(self, mod_config: ModConfig) -> Generator[Progress, None, None]:
        """
        Install all patchs of the mod_config into the game.
        Used before the lecode patch is applied
        :param mod_config: the mod to install
        """
        yield Progress(description="Installing all Pre-Patch...", determinate=False)
        yield from self._install_all_patch(mod_config, "_PREPATCH/")

    def install_all_patch(self, mod_config: ModConfig) -> Generator[Progress, None, None]:
        """
        Install all patchs of the mod_config into the game.
        Used after the lecode patch is applied
        :param mod_config: the mod to install
        """
        yield Progress(description="Installing all Patch...", determinate=False)
        yield from self._install_all_patch(mod_config, "_PATCH/")

    def convert_to(self, output_type: wit.Extension) -> Generator[Progress, None, wit.WITPath | None]:
        """
        Convert the extracted game to another format
        :param output_type: path to the destination of the game
        :output_type: format of the destination game
        """
        yield Progress(description=f"Converting game to {output_type}", determinate=False)
        if output_type == wit.Extension.FST: return

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

        yield Progress(description="Deleting the extracted game...", determinate=False)
        shutil.rmtree(self.path)

        return converted_game
