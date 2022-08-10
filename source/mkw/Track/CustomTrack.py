from source.mkw.Track.AbstractTrack import AbstractTrack

ModConfig: any


class CustomTrack(AbstractTrack):
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
            from source.mkw.TrackGroup import TrackGroup
            return TrackGroup.from_dict(track_dict)
        return cls(**track_dict)

    def get_filename(self, mod_config: "ModConfig") -> str:
        return self.repr_format(mod_config=mod_config, template=mod_config.track_file_template)

    def is_new(self, mod_config: "ModConfig") -> bool:
        """
        Return if the track should be considered as new for random selection
        :param mod_config: mod configuration
        :return: is the track new
        """
        return mod_config.safe_eval(mod_config.global_settings["replace_random_new"].value, env={"track": self}) is True
