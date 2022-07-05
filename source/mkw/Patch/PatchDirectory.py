from typing import Generator

from source.mkw.Patch import *
from source.mkw.Patch.PatchObject import PatchObject


class PatchDirectory(PatchObject):
    """
    Represent a directory from a patch
    """

    @property
    def subpatchs(self) -> Generator["PatchObject", None, None]:
        """
        return all the subpatchs inside the PatchDirectory
        """
        for subpath in self.full_path.iterdir():
            if subpath.suffix == ".json": continue
            yield self.subfile_from_path(subpath)

    def install(self, extracted_game: "ExtractedGame", game_subpath: Path) -> Generator[dict, None, None]:
        """
        patch a subdirectory of the game with the PatchDirectory
        """
        yield {"description": f"Patching {self}"}

        if self.patch.safe_eval(self.configuration["if"], extracted_game) == "False": return

        match self.configuration["mode"]:
            # if the mode is copy, then simply patch the subfile into the game with the same path
            case "copy":
                for subpatch in self.subpatchs:
                    # install the subfile in the directory with the same name as the PatchDirectory
                    yield from subpatch.install(extracted_game, game_subpath / subpatch.full_path.name)

            # if the mode is replace, patch all the files that match the replace_regex
            case "match":
                for subpatch in self.subpatchs:
                    # install the subfile in all the directory that match the match_regex of the configuration
                    for game_subfile in game_subpath.parent.glob(self.configuration["match_regex"]):
                        # disallow patching files outside of the game
                        if not game_subfile.relative_to(extracted_game.path):
                            raise PathOutsidePatch(game_subfile, extracted_game.path)

                        # patch the game with the subpatch
                        # if the subfile is a szs archive, replace it with a .d extension
                        if game_subfile.suffix == ".szs": game_subfile = game_subfile.with_suffix(".d")
                        yield from subpatch.install(extracted_game, game_subfile / subpatch.full_path.name)

            # ignore if mode is "ignore", useful if the file is used as a resource for an operation
            case "ignore": pass

            # else raise an error
            case _:
                raise InvalidPatchMode(self.configuration["mode"])
