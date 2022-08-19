from typing import TYPE_CHECKING

from source.mkw import Tag
from source.mkw.collection import Slot
from source.mkw.Track.RealArenaTrack import RealArenaTrack
from source.translation import translate as _

if TYPE_CHECKING:
    from source import TemplateMultipleSafeEval
    from source.mkw.ModConfig import ModConfig


class ArenaForbiddenCustomAttribute(Exception):
    def __init__(self, attribute_name: str):
        super().__init__(_("FORBIDDEN_ARENA_ATTRIBUTE", " : ", repr(attribute_name)))


class Arena(RealArenaTrack):
    """
    Represent an arena object
    """

    mod_config: "ModConfig"
    slot: Slot.Slot
    music: Slot.Slot
    special: Slot.Slot
    tags: list[Tag]

    def __init__(self, mod_config: "ModConfig", slot: Slot.Slot, music: Slot.Slot = None, special: Slot.Slot = None,
                 tags: list[Tag] = None, **kwargs):

        self.mod_config = mod_config
        self.slot = Slot.find(slot)
        self.music = Slot.find(music if music is not None else slot)
        self.special = Slot.find(special if special is not None else slot)
        self.tags = tags if tags is not None else []

        # others not mandatory attributes
        for key, value in kwargs.items():
            # if the attribute start with __, this is a magic attribute, and it should not be modified
            if "__" in key: raise ArenaForbiddenCustomAttribute(key)
            setattr(self, key, value)

    def __repr__(self):
        return f"<{self.__class__.__name__} name={getattr(self, 'name', '/')} tags={getattr(self, 'tags', '/')}>"

    @classmethod
    def from_dict(cls, mod_config: "ModConfig", arena_dict: dict[str, any]) -> "Arena":
        return cls(mod_config, **arena_dict)

    def get_ctfile(self, template: "TemplateMultipleSafeEval") -> (str, str):
        """
        Return the ctfile for the arena and the redefinition of the slot property
        :param template: the template of the track name
        :return: the ctfile for the arena and the redefinition of the slot property
        """

        name: str = self.repr_format(template=template)
        filename: str = self.filename

        return (
            (
                f'A '  # category (A for arena)
                f'{self.music.normal}; '  # music 
                f'{self.slot.normal}; '  # slot of the arena
                f'0x00; '  # lecode flag
                f'{filename!r}; '  # filename
                f'{name!r}; '  # name of the track in the menu
                f'{filename!r}\n'  # unique identifier for each track
            ),
            (
                f"{self.slot.normal} "
                f"{self.special.normal}\n"
            )
        )
