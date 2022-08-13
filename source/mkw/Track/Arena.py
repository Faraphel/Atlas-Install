from source.mkw import Slot, Tag
from source.mkw.Track.RealArenaTrack import RealArenaTrack


class ArenaForbiddenCustomAttribute(Exception):
    def __init__(self, attribute_name: str):
        super().__init__(f"Forbidden arena attribute : {attribute_name!r}")


class Arena(RealArenaTrack):
    slot: Slot
    music: Slot
    special: Slot
    tags: list[Tag]

    def __init__(self, slot: Slot, music: Slot = None, special: Slot = None, tags: list[Tag] = None, **kwargs):
        self.slot = slot
        self.music = music if music is not None else slot
        self.special = special if special is not None else slot
        self.tags = tags if tags is not None else []

        # others not mandatory attributes
        for key, value in kwargs.items():
            # if the attribute start with __, this is a magic attribute, and it should not be modified
            if "__" in key or hasattr(self, key): raise ArenaForbiddenCustomAttribute(key)
            setattr(self, key, value)

    def __repr__(self):
        return f"<{self.__class__.__name__} name={getattr(self, 'name', '/')} tags={getattr(self, 'tags', '/')}>"

    @classmethod
    def from_dict(cls, arena_dict: dict[str, any]) -> "Arena":
        return cls(**arena_dict)

    def get_ctfile(self, mod_config: "ModConfig", template: str) -> (str, str):
        """
        Return the ctfile for the arena and the redefinition of the slot property
        :param mod_config: the mod_config object
        :param template: the template of the track name
        :return: the ctfile for the arena and the redefinition of the slot property
        """

        name: str = self.repr_format(mod_config=mod_config, template=template)
        filename = self.get_filename(mod_config=mod_config)

        return (
            (
                f'A '  # category (A for arena)
                f'{self.music}; '  # music 
                f'{self.slot}; '  # slot of the arena
                f'0x00; '  # lecode flag
                f'{filename!r}; '  # filename
                f'{name!r}; '  # name of the track in the menu
                f'{filename!r}\n'  # unique identifier for each track
            ),
            (
                f"{self.slot} "
                f"{self.special}\n"
            )
        )
