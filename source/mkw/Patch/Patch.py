from typing import Generator

from source.mkw.Patch import *
from source.safe_eval import safe_eval, multiple_safe_eval


class Patch:
    """
    Represent a patch object
    """

    def __init__(self, path: Path | str, mod_config: "ModConfig"):
        self.path = Path(path)
        self.mod_config = mod_config

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.path}>"

    def safe_eval(self, template: str, multiple: bool = False, **env) -> str:
        """
        Safe eval with a patch environment
        :param multiple: should the expression be a multiple safe eval or a single safe eval
        :param env: other variable that are allowed in the safe_eval
        :param template: template to evaluate
        :return: the result of the evaluation
        """
        return (multiple_safe_eval if multiple else safe_eval)(
            template,
            extra_token_map={"mod_config": "mod_config"} | {key: key for key in env},
            env={"mod_config": self.mod_config} | env,
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
