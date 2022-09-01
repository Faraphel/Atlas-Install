from source.mkw.Track.AbstractTrack import AbstractTrack


class DefaultTrack(AbstractTrack):
    def repr_format(self, template: str) -> str:
        return " "  # the name is always a blank space. Using nothing result in the filename being used instead

    @property
    def filename(self) -> str:
        return "beginner_course"  # by default, use the T11 track, beginner_course

    @property
    def is_new(self) -> bool:
        return False  # default track are never selected for random cup
