from typing import TYPE_CHECKING

from source.mkw.Track.AbstractTrack import AbstractTrack
from source.mkw.Track.RealArenaTrack import RealArenaTrack

if TYPE_CHECKING:
    from source.mkw.ModConfig import ModConfig


class CustomTrack(RealArenaTrack, AbstractTrack):
    """
    Represent a custom track
    """
    def __repr__(self):
        return f"<{self.__class__.__name__} name={getattr(self, 'name', '/')} tags={getattr(self, 'tags', '/')}>"

    @classmethod
    def from_dict(cls, mod_config: "ModConfig", track_dict: dict) -> "Track | TrackGroup":
        """
        create a track from a dict, or create a track group is it is a group
        :param mod_config: the mod configuration
        :param track_dict: dict containing the track information
        :return: Track
        """
        if "group" in track_dict:
            from source.mkw.Track.TrackGroup import TrackGroup
            return TrackGroup.from_dict(mod_config, track_dict)
        return cls(mod_config, **track_dict)

    @property
    def is_new(self) -> bool:
        return self.mod_config.safe_eval(
            self.mod_config.global_settings["replace_random_new"].value,
            args=["track"]
        )(track=self) is True
