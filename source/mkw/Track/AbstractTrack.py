from abc import ABC, abstractmethod
from typing import Generator, TYPE_CHECKING

from source.mkw import Tag, ModConfig
from source.mkw.collection import Slot
from source.translation import translate as _

if TYPE_CHECKING:
    from source import TemplateMultipleSafeEval


class TrackForbiddenCustomAttribute(Exception):
    def __init__(self, attribute_name: str):
        super().__init__(_("ERROR_FORBIDDEN_TRACK_ATTRIBUTE") % attribute_name)


class AbstractTrack(ABC):

    mod_config: "ModConfig"
    music: Slot.Slot
    special: Slot.Slot
    tags: list[Tag]
    weight: int

    def __init__(self, mod_config: "ModConfig", music: Slot.Slot = "T11", special: Slot.Slot = "T11",
                 tags: list[Tag] = None, weight: int = 1, **kwargs):

        self.mod_config = mod_config
        self.music = Slot.find(music)
        self.special = Slot.find(special)
        self.tags = tags if tags is not None else []
        self.weight = weight

        # others not mandatory attributes
        for key, value in kwargs.items():
            # if the attribute start with __, this is a magic attribute, and it should not be modified
            if "__" in key: raise TrackForbiddenCustomAttribute(key)
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
    def repr_format(self, template: "TemplateMultipleSafeEval") -> str:
        """
        return the representation of the track from the format
        :param template: template for the way the text will be represented
        :return: formatted representation of the track
        """
        ...

    @property
    @abstractmethod
    def filename(self) -> str:
        """
        Return the filename of the track
        :return: the filename of the track
        """
        ...

    @property
    @abstractmethod
    def is_new(self) -> bool:
        """
        Return if the track should be considered as new for random selection
        :return: is the track new
        """
        ...

    def get_ctfile(self, template: "TemplateMultipleSafeEval", hidden: bool = False) -> str:
        """
        return the ctfile of the track
        :hidden: if the track is in a group
        :template: format of the track's name
        :return: ctfile
        """
        category: str = "H" if hidden else "T"
        name: str = self.repr_format(template=template)
        filename: str = self.filename
        flags: int = (
            (0x04 if hidden else 0) |
            (0x01 if self.is_new else 0)
        )

        return (
            f'{category} '  # category (is the track hidden, visible, an arena, ...)
            f'{self.music.normal}; '  # music 
            f'{self.special.normal}; '  # property of the tracks
            f'{flags:#04x}; '  # lecode flags
            f'{filename!r}; '  # filename
            f'{name!r}; '  # name of the track in the menu
            f'{filename!r}\n'  # unique identifier for each track
        )
