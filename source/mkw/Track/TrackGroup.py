from typing import Generator, TYPE_CHECKING

from source.mkw import Tag
from source.translation import translate as _

if TYPE_CHECKING:
    from source import TemplateMultipleSafeEval
    from source.mkw.Track.CustomTrack import CustomTrack
    from source.mkw.ModConfig import ModConfig


class TrackGroupForbiddenCustomAttribute(Exception):
    def __init__(self, attribute_name: str):
        super().__init__(_("ERROR_FORBIDDEN_TRACKGROUP_ATTRIBUTE") % attribute_name)


class TrackGroup:

    mod_config: "ModConfig"
    tracks: list["CustomTrack"]
    tags: list["Tag"]

    def __init__(self, mod_config: "ModConfig", tracks: list["CustomTrack"] = None,
                 tags: list["Tag"] = None, **kwargs):
        self.mod_config = mod_config
        self.tracks = tracks if tracks is not None else []
        self.tags = tags if tags is not None else []

        # others not mandatory attributes
        for key, value in kwargs.items():
            # if the attribute start with __, this is a magic attribute, and it should not be modified
            if "__" in key: raise TrackGroupForbiddenCustomAttribute(key)
            setattr(self, key, value)

    def get_tracks(self) -> Generator["CustomTrack", None, None]:
        """
        Get all the track elements
        :return: track elements
        """
        for track in self.tracks:
            yield from track.get_tracks()

    @classmethod
    def from_dict(cls, mod_config: "ModConfig", group_dict: dict) -> "TrackGroup | Track":
        """
        create a track group from a dict, or create a track from the dict if not a group
        :param mod_config: the mod configuration
        :param group_dict: dict containing the track information
        :return: TrackGroup or Track
        """
        from source.mkw.Track.CustomTrack import CustomTrack

        if "group" not in group_dict: return CustomTrack.from_dict(mod_config, group_dict)
        return cls(
            mod_config,
            tracks=[CustomTrack.from_dict(mod_config, track) for track in group_dict["group"]],
            **group_dict,
        )

    def get_ctfile(self, template: "TemplateMultipleSafeEval") -> str:
        """
        return the ctfile of the track group
        :return: ctfile
        """
        ctfile = f'T T11; T11; 0x02; "-"; "-"; "-"\n'
        for track in self.get_tracks():
            ctfile += track.get_ctfile(template=template, hidden=True)

        return ctfile
