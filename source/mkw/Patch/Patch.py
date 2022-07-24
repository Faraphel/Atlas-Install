from typing import Generator, IO

from source.mkw.Patch import *


class Patch:
    """
    Represent a patch object
    """

    def __init__(self, path: Path | str, mod_config: "ModConfig", special_file: dict[str, IO] = None):
        self.path = Path(path)
        self.mod_config = mod_config
        self.special_file = special_file if special_file is not None else {}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.path}>"

    def install(self, extracted_game: "ExtractedGame") -> Generator[dict, None, None]:
        """
        patch a game with this Patch
        :param extracted_game: the extracted game
        """
        from source.mkw.Patch.PatchDirectory import PatchDirectory
        yield {"description": f"Installing the patch", "determinate": False}

        # take all the files in the root directory, and patch them into the game.
        # Patch is not directly applied to the root to avoid custom configuration
        # on the base directory.

        for file in self.path.iterdir():
            pathname = file.relative_to(self.path)
            yield from PatchDirectory(self, str(pathname)).install(extracted_game, extracted_game.path / pathname)
