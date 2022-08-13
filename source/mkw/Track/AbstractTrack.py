from abc import ABC, abstractmethod
from typing import Generator

from source.mkw import Slot, Tag, ModConfig


class TrackForbiddenCustomAttribute(Exception):
    def __init__(self, attribute_name: str):
        super().__init__(f"Forbidden track attribute : {attribute_name!r}")


class AbstractTrack(ABC):
    music: Slot
    special: Slot
    tags: list[Tag]
    weight: int

    def __init__(self, music: Slot = "T11", special: Slot = "T11", tags: list[Tag] = None, weight: int = 1, **kwargs):
        self.music = music
        self.special = special
        self.tags = tags if tags is not None else []
        self.weight = weight

        # others not mandatory attributes
        for key, value in kwargs.items():
            # if the attribute start with __, this is a magic attribute, and it should not be modified
            if "__" in key or hasattr(self, key): raise TrackForbiddenCustomAttribute(key)
            setattr(self, key, value)

    def __repr__(self):
        return f"<{self.__class__.__name__} {hex(id(self))}>"

    def get_tracks(self) -> Generator["AbstractTrack", None, None]:
        """
        Return all the track itself or the subtracks if available
        :return: all the track itself or the subtracks if available
        """
        for _ in range(self.weight):
            yield self

    @abstractmethod
    def repr_format(self, mod_config: "ModConfig", template: str) -> str:
        """
        return the representation of the track from the format
        :param template: template for the way the text will be represented
        :param mod_config: configuration of the mod
        :return: formatted representation of the track
        """
        ...

    @abstractmethod
    def get_filename(self, mod_config: "ModConfig") -> str:
        """
        Return the filename of the track
        :param mod_config: the mod_config object
        :return: the filename of the track
        """
        ...

    @abstractmethod
    def is_new(self, mod_config: "ModConfig") -> bool:
        """
        Return if the track should be considered as new for random selection
        :param mod_config: mod configuration
        :return: is the track new
        """
        ...

    def get_ctfile(self, mod_config: "ModConfig", template: str, hidden: bool = False) -> str:
        """
        return the ctfile of the track
        :hidden: if the track is in a group
        :template: format of the track's name
        :return: ctfile
        """
        category: str = "H" if hidden else "T"
        name: str = self.repr_format(mod_config=mod_config, template=template)
        filename: str = self.get_filename(mod_config=mod_config)
        flags: int = (
            (0x04 if hidden else 0) |
            (0x01 if self.is_new(mod_config) else 0)
        )

        return (
            f'{category} '  # category (is the track hidden, visible, an arena, ...)
            f'{self.music}; '  # music 
            f'{self.special}; '  # property of the tracks
            f'{flags:#04x}; '  # lecode flags
            f'{filename!r}; '  # filename
            f'{name!r}; '  # name of the track in the menu
            f'{filename!r}\n'  # unique identifier for each track
        )