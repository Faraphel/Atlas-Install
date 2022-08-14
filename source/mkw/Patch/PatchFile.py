from io import BytesIO
from pathlib import Path
from typing import Generator, IO, TYPE_CHECKING

from source.mkw.Patch import PathOutsidePatch, InvalidPatchMode, InvalidSourceMode
from source.mkw.Patch.PatchOperation import AbstractPatchOperation
from source.mkw.Patch.PatchObject import PatchObject
from source.wt.szs import SZSPath

if TYPE_CHECKING:
    from source.mkw.ExtractedGame import ExtractedGame


class PatchFile(PatchObject):
    """
    Represent a file from a patch
    """

    def get_source_path(self, game_subpath: Path) -> Path:
        """
        Return the path of the file that the patch is applied on.
        If the configuration mode is set to "game", then return the path of the file inside the Game
        Else, return the path of the file inside the Patch
        """
        match self.configuration["source"]:
            case "patch": return self.full_path
            case "game": return game_subpath
            case _: raise InvalidSourceMode(self, self.configuration["course"])

    def get_patched_file(self, game_subpath: Path) -> (str, BytesIO):
        """
        Return the name and the content of the patched file
        :param game_subpath: path to the game subfile
        :return: the name and the content of the patched file
        """
        patch_source: Path = self.get_source_path(game_subpath)
        patch_name: str = game_subpath.name
        patch_content: BytesIO = BytesIO(open(patch_source, "rb").read())
        # the file is converted into a BytesIO because if the source is "game",
        # the file is overwritten and if the content is untouched, the file will only be lost

        for operation_name, operation in self.configuration.get("operation", {}).items():
            # process every operation and get the new patch_path (if the name is changed)
            # and the new content of the patch
            patch_name, patch_content = AbstractPatchOperation.get(operation_name)(**operation).patch(
                self.patch, patch_name, patch_content
            )

        return patch_name, patch_content

    @staticmethod
    def write_patch(destination: Path, patch_content: IO) -> None:
        """
        Write a patch content to the destination. Automatically create the directory and seek to the start.
        :param destination: file where the content will be written
        :param patch_content: content of the file to write
        """
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "wb") as file:
            patch_content.seek(0)
            file.write(patch_content.read())

    @staticmethod
    def check_szs(extracted_game: "ExtractedGame", game_subpath: Path) -> None:
        """
        Check if game path is inside a szs archive. If yes, extract it.
        :param extracted_game: the extracted game object
        :param game_subpath: path to the game file that is being patched
        """
        for szs_subpath in filter(lambda path: path.suffix == ".d",
                                  game_subpath.relative_to(extracted_game.path).parents):

            szs_path = extracted_game.path / szs_subpath

            # if the archive is not already extracted  and the szs file in the game exists, extract it
            if not szs_path.exists() and szs_path.with_suffix(".szs").exists():
                SZSPath(szs_path.with_suffix(".szs")).extract_all(szs_path)

    def install(self, extracted_game: "ExtractedGame", game_subpath: Path) -> Generator[dict, None, None]:
        """
        patch a subfile of the game with the PatchFile
        """
        yield {"description": f"Patching {game_subpath}"}

        # check if the file should be patched
        if not self.is_enabled(extracted_game): return

        # check if it is patching a szs archive. If yes, extract it.
        self.check_szs(extracted_game, game_subpath)

        # apply operation on the file

        match self.configuration["mode"]:
            # if the mode is copy, replace the subfile in the game by the PatchFile
            case "copy":
                patch_name, patch_content = self.get_patched_file(game_subpath)
                self.write_patch(game_subpath.parent / patch_name, patch_content)
                patch_content.close()

            # if the mode is replace, only write if the file existed before
            case "replace":
                patch_name, patch_content = self.get_patched_file(game_subpath)
                if (game_subpath.parent / patch_name).exists():
                    self.write_patch(game_subpath.parent / patch_name, patch_content)
                    patch_content.close()

            # if the mode is match, replace all the subfiles that match match_regex by the PatchFile
            case "match":
                patch_content: BytesIO = BytesIO()

                # if the source is the patch, then directly calculate the patch content
                # so that it is not recalculated for every file with no reason
                if self.configuration["source"] == "patch":
                    _, patch_content = self.get_patched_file(game_subpath)

                for game_subfile in game_subpath.parent.glob(self.configuration["match_regex"]):
                    # disallow patching files outside of the game
                    if not game_subfile.relative_to(extracted_game.path):
                        raise PathOutsidePatch(game_subfile, extracted_game.path)

                    yield {"description": f"Patching {game_subfile}"}

                    # if the source is the game, then recalculate the content for every game subfile
                    if self.configuration["source"] == "game":
                        _, patch_content = self.get_patched_file(game_subfile)

                    # patch the game with the patch content
                    self.write_patch(game_subfile, patch_content)

                patch_content.close()

            # ignore if mode is "ignore", useful if the file is used as a resource for an operation
            case "ignore": pass
            # else raise an error
            case _: raise InvalidPatchMode(self, self.configuration["mode"])
