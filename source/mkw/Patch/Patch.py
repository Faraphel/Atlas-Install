from typing import Generator

from source.mkw.Patch import *
from source.safe_eval import safe_eval


class Patch:
    """
    Represent a patch object
    """

    def __init__(self, path: Path | str):
        self.path = Path(path)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.path}>"

    def safe_eval(self, template: str, extracted_game: "ExtractedGame") -> str:
        """
        Safe eval with a patch environment
        :param extracted_game: the extracted game to patch
        :param template: template to evaluate
        :return: the result of the evaluation
        """
        return safe_eval(
            template,
            extra_token_map={"extracted_game": "extracted_game"},
            env={"extracted_game": extracted_game},
        )

    def install(self, extracted_game: "ExtractedGame") -> Generator[dict, None, None]:
        """
        patch a game with this Patch
        """
        from source.mkw.Patch.PatchDirectory import PatchDirectory

        # take all the files in the root directory, and patch them into the game.
        # Patch is not directly applied to the root to avoid custom configuration
        # on the base directory.

        for file in self.path.iterdir():
            pathname = file.relative_to(self.path)
            yield from PatchDirectory(self, str(pathname)).install(extracted_game, extracted_game.path / pathname)
