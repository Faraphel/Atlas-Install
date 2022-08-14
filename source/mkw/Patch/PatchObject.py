import json
from abc import abstractmethod, ABC
from pathlib import Path
from typing import Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from source.mkw.Patch import Patch
    from source.mkw.ExtractedGame import ExtractedGame


class PatchObject(ABC):
    """
    Represent an object inside a patch
    """

    def __init__(self, patch: "Patch", subpath: str):
        self.patch = patch
        self.subpath = subpath
        self._configuration = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_path}>"

    @property
    def full_path(self) -> Path:
        return self.patch.path / self.subpath

    @property
    def configuration(self) -> dict:
        """
        return the configuration from the file
        """
        if self._configuration is not None: return self._configuration

        # default configuration
        self._configuration = {
            "mode": "copy",  # mode on how should the file be patched
            "source": "patch",  # source of the file data that will be modified
            "if": "True",  # condition for the patch to be applied
        }

        configuration_path = self.full_path.with_suffix(self.full_path.suffix + ".json")
        if not configuration_path.exists(): return self._configuration

        self._configuration |= json.loads(configuration_path.read_text(encoding="utf8"))

        # if configuration inherit from an another file, then load it from the patch root,
        # keep this configuration keys over inherited one.
        # pop "base" to avoid infinite loop
        while "base" in self._configuration:
            self._configuration |= json.loads(
                (self.patch.path / self._configuration.pop("base")).read_text(encoding="utf8"))

        return self._configuration

    def subfile_from_path(self, path: Path) -> "PatchObject":
        """
        return a PatchObject from a path
        """
        from source.mkw.Patch.PatchDirectory import PatchDirectory
        from source.mkw.Patch.PatchFile import PatchFile

        obj = PatchDirectory if path.is_dir() else PatchFile
        return obj(self.patch, str(path.relative_to(self.patch.path)))

    @abstractmethod
    def install(self, extracted_game: "ExtractedGame", game_subpath: Path) -> Generator[dict, None, None]:
        """
        install the PatchObject into the game
        yield the step of the process
        """
        ...

    def is_enabled(self, extracted_game: "ExtractedGame") -> bool:
        """
        Return if the patch object is actually enabled
        :param extracted_game: the extracted game object
        :return: should the patch be applied ?
        """
        return self.patch.mod_config.safe_eval(self.configuration["if"], env={"extracted_game": extracted_game}) is True
