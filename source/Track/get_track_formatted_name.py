from ..definition import *


def get_track_formatted_name(self, highlight_track_from_version: str = None):
    """
    :param highlight_track_from_version: if a specific version need to be highlighted.
    :return: the name of the track with colored prefix, suffix
    """
    hl_prefix = ""
    hl_suffix = ""
    prefix = ""
    suffix = ""
    star_text = ""

    if self.score:
        if 0 < self.score <= 3:
            star_text = "★" * self.score + "☆" * (3 - self.score)
            star_text = trackname_color[star_text] + " "

    if self.since_version == highlight_track_from_version:
        hl_prefix, hl_suffix = "\\\\c{blue1}", "\\\\c{off}"

    if self.prefix in trackname_color:
        prefix = trackname_color[self.prefix] + " "
    if self.suffix in trackname_color:
        suffix = "(" + trackname_color[self.suffix] + ")"

    name = (star_text + prefix + hl_prefix + self.name + hl_suffix + suffix)
    name = name.replace("_", " ")
    return name
