import enum


class Extension(enum.Enum):
    """
    Enum for game extension
    """
    WBFS = ".wbfs"
    FST = ".dol"
    CISO = ".ciso"
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
