from .definition import *
import subprocess
import source.wszst


class Track:
    def __init__(self, name: str, file_wu8: str = None, file_szs: str = None, prefix: str = None, suffix: str = None,
                 author="Nintendo", special="T11", music="T11", new=True, sha1: str = None, since_version: str = None,
                 score: int = 0, warning: int = 0, note: str = ""):

        self.name = name                    # Track name
        self.prefix = prefix                # Prefix, often used for game or original console like Wii U, DS, ...
        self.suffix = suffix                # Suffix, often used for variety like Boost, Night, ...
        self.author = author                # Track author
        self.sha1 = sha1                    # Track sha1 from wszst SHA1
        self.special = special              # Special slot of the track
        self.music = music                  # Music of the track
        self.new = new                      # Is the track new
        self.since_version = since_version  # Since which version is this track available
        self.file_wu8 = file_wu8
        self.file_szs = file_szs
        self.score = score                  # Track score between 1 and 3 stars
        self.warning = warning              # Track bug level (1 = minor, 2 = major)
        self.note = note                    # Note about the track

    def get_track_name(self):
        prefix = self.prefix + " " if self.prefix else ""
        suffix = self.suffix + " " if self.suffix else ""

        name = (prefix + self.name + suffix)
        return name

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
                star_text = "★" * track["score"] + "☆" * (3 - track["score"])
                star_text = trackname_color[star_text] + " "

        if self.since_version == highlight_track_from_version:
            hl_prefix, hl_suffix = "\\\\c{blue1}", "\\\\c{off}"

        if self.prefix in trackname_color:
            prefix = trackname_color[self.prefix] + " "
        if self.suffix in trackname_color:
            suffix = "(" + trackname_color[self.suffix] + ")"

        name = (star_text + prefix + hl_prefix + self.name + hl_suffix + suffix)
        name = name.replace("_", "")
        return name

    def convert_wu8_to_szs(self):
        source.wszst.normalize(src_file=self.file_wu8)

    def download_wu8(self): pass

    def check_sha1(self):
        if source.wszst.sha1(self.file_wu8) == self.sha1: return 0
        else: return -1

    def get_ct_file_track(self): pass


EMPTY_TRACK = Track("_")
