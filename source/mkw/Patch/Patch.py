from typing import Generator, IO

from source.mkw.Patch import *
from source.safe_eval import safe_eval, multiple_safe_eval


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

    def safe_eval(self, template: str, multiple: bool = False, env: dict[str, any] = None) -> str:
        """
        Safe eval with a patch environment
        :param multiple: should the expression be a multiple safe eval or a single safe eval
        :param env: other variable that are allowed in the safe_eval
        :param template: template to evaluate
        :return: the result of the evaluation
        """
        return (multiple_safe_eval if multiple else safe_eval)(
            template,
            env={"mod_config": self.mod_config} | (env if env is not None else {}),
        )

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
