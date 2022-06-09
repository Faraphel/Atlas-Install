from typing import Generator


# representation of a group of tracks
class TrackGroup:
    def __init__(self, tracks: list["Track"] = None):
        self.tracks = tracks if tracks is not None else []

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
        return cls(tracks=[Track.from_dict(track) for track in group_dict["group"]])
