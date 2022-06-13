from typing import Generator
import re

from source.mkw import Tag, Slot
from source.safe_eval import safe_eval

TOKEN_START = "{{"
TOKEN_END = "}}"


# representation of a custom track
class Track:
    def __init__(self, special: Slot = None, music: Slot = None, tags: list[Tag] = None, weight: int = None, **kwargs):
        self.special: Slot = special if special is not None else "T11"
        self.music: Slot = music if music is not None else "T11"
        self.tags: list[Tag] = tags if tags is not None else []
        self.weight: int = weight if weight is not None else 1

        # others not mandatory attributes
        for key, value in kwargs.items():
            # if the attribute start with __, this is a magic attribute, and it should not be modified
            if key.startswith("__"): continue
            setattr(self, key, value)

    def __repr__(self):
        return f"<Track name={getattr(self, 'name', '/')} tags={getattr(self, 'tags', '/')}>"

    @classmethod
    def from_dict(cls, track_dict: dict) -> "Track | TrackGroup":
        """
        create a track from a dict, or create a track group is it is a group
        :param track_dict: dict containing the track information
        :return: Track
        """
        if "group" in track_dict:
            from source.mkw.TrackGroup import TrackGroup
            return TrackGroup.from_dict(track_dict)
        return cls(**track_dict)

    def get_tracks(self) -> Generator["Track", None, None]:
        """
        Get all the track elements
        :return: track elements
        """
        for _ in range(self.weight):
            yield self

    def repr_format(self, mod_config: "ModConfig", format: str) -> str:
        """
        return the representation of the track from the format
        :param mod_config: configuration of the mod
        :return: formatted representation of the track
        """

        extra_token_map = {  # replace the suffix and the prefix by the corresponding values
            "prefix": f'{self.get_prefix(mod_config, "")!r}',
            "suffix": f'{self.get_suffix(mod_config, "")!r}',
            "track": "track"
        }

        def format_template(match: re.Match) -> str:
            """
            when a token is found, replace it by the corresponding value
            :param match: match in the format
            :return: corresponding value
            """
            # get the token string without the brackets, then strip it. Also double antislash
            template = match.group(1).strip().replace("\\", "\\\\")
            return safe_eval(template, extra_token_map, {"track": self})

        # pass everything between TOKEN_START and TOKEN_END in the function
        return re.sub(rf"{TOKEN_START}(.*?){TOKEN_END}", format_template, format)

    def get_prefix(self, mod_config: "ModConfig", default: any = None) -> any:
        """
        return the prefix of the track
        :param default: default value if no prefix is found
        :param mod_config: mod configuration
        :return: formatted representation of the track prefix
        """
        for tag in filter(lambda tag: tag in mod_config.tags_prefix, self.tags): return tag
        return default

    def get_suffix(self, mod_config: "ModConfig", default: any = None) -> any:
        """
        return the suffix of the track
        :param default: default value if no suffix is found
        :param mod_config: mod configuration
        :return: formatted representation of the track suffix
        """
        for tag in filter(lambda tag: tag in mod_config.tags_suffix, self.tags): return tag
        return default

    def is_highlight(self, mod_config: "ModConfig", default: any = None) -> bool:
        ...

    def is_new(self, mod_config: "ModConfig", default: any = None) -> bool:
        ...

    def get_ctfile(self, mod_config: "ModConfig", hidden: bool = False) -> str:
        """
        return the ctfile of the track
        :hidden: if the track is in a group
        :return: ctfile
        """
        menu_name = f'{self.repr_format(mod_config=mod_config, format=mod_config.track_formatting["menu_name"])!r}'
        file_name = f'{self.repr_format(mod_config=mod_config, format=mod_config.track_formatting["file_name"])!r}'

        return (
            f'{"H" if hidden else "T"} {self.music}; '  # track type
            f'{self.special}; {(0x04 if hidden else 0) | (0x01 if self.is_new(mod_config, False) else 0):#04x}; '  # lecode flags
            f'{file_name}; '  # filename
            f'{menu_name}; '  # name of the track in the menu
            f'{file_name}\n'  # unique identifier for each track
        )
