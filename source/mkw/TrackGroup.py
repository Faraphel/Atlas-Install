from typing import Generator

from source.mkw import Tag


class TrackGroup:
    def __init__(self, tracks: list["Track"] = None, tags: list[Tag] = None, name: str = None):
        self.tracks = tracks if tracks is not None else []
        self.tags = tags if tags is not None else []
        self.name = name if name is not None else ""

    def get_tracks(self) -> Generator["Track", None, None]:
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
        from source.mkw.Track import Track

        if "group" not in group_dict: return Track.from_dict(group_dict)
        return cls(
            tracks=[Track.from_dict(track) for track in group_dict["group"]],
            tags=group_dict.get("tags"),
            name=group_dict.get("name"),
        )

    def get_ctfile(self, mod_config: "ModConfig") -> str:
        """
        return the ctfile of the track group
        :return: ctfile
        """
        ctfile = f'T T11; T11; 0x02; "-"; "info"; "-"\n'
        for track in self.get_tracks():
            ctfile += track.get_ctfile(mod_config=mod_config, hidden=True)

        return ctfile
