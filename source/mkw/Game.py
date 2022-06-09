import enum
from pathlib import Path

from source.wt.wit import WITPath


class Extension(enum.Enum):
    """
    Enum for game extension
    """
    FST = ".dol"
    WBFS = ".wbfs"
    ISO = ".iso"

    @classmethod
    def _missing_(cls, value: str) -> "Extension | None":
        """
        if not found, search for the same value with lower case
        :param value: value to search for
        :return: None if nothing found, otherwise the found value
        """
        value = value.lower()
        for member in filter(lambda m: m.value == value, cls): return member
        return None


class Region(enum.Enum):
    """
    Enum for game region
    """
    PAL = "PAL"
    USA = "USA"
    EUR = "EUR"
    KOR = "KOR"


class Game:
    def __init__(self, path: Path | str):
        self.path = Path(path) if isinstance(path, str) else path

    @property
    def extension(self) -> Extension:
        """
        Returns the extension of the game
        :return: the extension of the game
        """
        return Extension(self.path.suffix)

    @property
    def id(self) -> str:
        """
        Return the id of the game (RMCP01, RMCK01, ...)
        :return: the id of the game
        """
        return WITPath(self.path).analyze()["id6"]

    @property
    def region(self) -> Region:
        """
        Return the region of the game (PAL, USA, EUR, ...)
        :return: the region of the game
        """
        return Region(WITPath(self.path).analyze()["dol_region"])

    def is_mkw(self) -> bool:
        """
        Return True if the game is Mario Kart Wii, else otherwise
        :return: is the game a MKW game
        """
        return WITPath(self.path).analyze()["dol_is_mkw"] == 1

    def is_vanilla(self) -> bool:
        ...
