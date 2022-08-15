from typing import Generator, TYPE_CHECKING

from source.mkw import Tag

if TYPE_CHECKING:
    from source import TemplateMultipleSafeEval
    from source.mkw.Track.CustomTrack import CustomTrack
    from source.mkw.ModConfig import ModConfig


class TrackGroup:
    def __init__(self, tracks: list["CustomTrack"] = None, tags: list[Tag] = None):
        self.tracks = tracks if tracks is not None else []
        self.tags = tags if tags is not None else []

    def get_tracks(self) -> Generator["CustomTrack", None, None]:
        """
        Get all the track elements
        :return: track elements
        """
        for track in self.tracks:
            yield from track.get_tracks()

    @classmethod
    def from_dict(cls, group_dict: dict) -> "TrackGroup | Track":
        """
        create a track group from a dict, or create a track from the dict if not a group
        :param group_dict: dict containing the track information
        :return: TrackGroup or Track
        """
        from source.mkw.Track.CustomTrack import CustomTrack

        if "group" not in group_dict: return CustomTrack.from_dict(group_dict)
        return cls(
            tracks=[CustomTrack.from_dict(track) for track in group_dict["group"]],
            tags=group_dict.get("tags"),
        )

    def get_ctfile(self, mod_config: "ModConfig", template: "TemplateMultipleSafeEval") -> str:
        """
        return the ctfile of the track group
        :return: ctfile
        """
        ctfile = f'T T11; T11; 0x02; "-"; "info"; "-"\n'
        for track in self.get_tracks():
            ctfile += track.get_ctfile(template=template, mod_config=mod_config, hidden=True)

        return ctfile
