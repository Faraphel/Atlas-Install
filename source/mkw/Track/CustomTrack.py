from source.mkw.Track.AbstractTrack import AbstractTrack
from source.mkw.Track.RealArenaTrack import RealArenaTrack

ModConfig: any


class CustomTrack(RealArenaTrack, AbstractTrack):
    """
    Represent a custom track
    """
    def __repr__(self):
        return f"<{self.__class__.__name__} name={getattr(self, 'name', '/')} tags={getattr(self, 'tags', '/')}>"

    @classmethod
    def from_dict(cls, track_dict: dict) -> "Track | TrackGroup":
        """
        create a track from a dict, or create a track group is it is a group
        :param track_dict: dict containing the track information
        :return: Track
        """
        if "group" in track_dict:
            from source.mkw.Track.TrackGroup import TrackGroup
            return TrackGroup.from_dict(track_dict)
        return cls(**track_dict)

    def is_new(self, mod_config: "ModConfig") -> bool:
        return mod_config.safe_eval(
            mod_config.global_settings["replace_random_new"].value,
            args=["track"]
        )(track=self) is True
