from source.mkw.Track.AbstractTrack import AbstractTrack


class DefaultTrack(AbstractTrack):
    def repr_format(self, mod_config: "ModConfig", template: str) -> str:
        return " "  # the name is always a blank space. Using nothing result in the filename being used instead

    def get_filename(self, mod_config: "ModConfig") -> str:
        return "beginner_course"  # by default, use the T11 track, beginner_course

    def is_new(self, mod_config: "ModConfig") -> bool:
        return False  # default track are never selected for random cup
