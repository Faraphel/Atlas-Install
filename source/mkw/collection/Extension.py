import enum


class Extension(enum.Enum):
    """
    Enum for game extension
    """
    WBFS = ".wbfs"
    FST = ".dol"
    CISO = ".ciso"
    ISO = ".iso"
    RIIVO = ".xml"

    def is_riivolution(self) -> bool:
        """
        :return: True is a riivolution patch, otherwise False
        """
        return self == self.__class__.RIIVO

    def is_directory(self) -> bool:
        """
        :return: True if the extension a directory extension, otherwise False
        """
        return self == self.__class__.FST

    def is_extractable(self) -> bool:
        """
        :return: True if the extension is extractable, otherwise False
        """
        return self in [
            self.__class__.CISO,
            self.__class__.ISO,
            self.__class__.WBFS,
        ]

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
