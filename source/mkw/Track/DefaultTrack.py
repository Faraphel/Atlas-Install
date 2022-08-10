from source.mkw.Track.AbstractTrack import AbstractTrack


class DefaultTrack(AbstractTrack):
    def get_filename(self, mod_config: "ModConfig") -> str:
        return "beginner_course"

    def is_new(self, mod_config: "ModConfig") -> bool:
        return False
