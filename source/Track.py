from source.definition import *
from source.wszst import *
from source.Error import *


def get_trackdata_from_json(track_json, *args, **kwargs):
    return (TrackGroup if "group" in track_json else Track)(*args, **kwargs).load_from_json(track_json)


def check_file_sha1(file: str, excepted_sha1: str) -> int:
    """
    check if track szs sha1 is correct
    :return: 1 if yes, 0 if no
    """
    if not os.path.exists(file): return 0
    calculated_sha1 = szs.sha1(file=file)
    if calculated_sha1 == excepted_sha1:
        return 1
    else:
        print(f"incorrect sha1 for {file} {calculated_sha1} : (expected {excepted_sha1})")
        return 0


class Track:
    _wu8_dir = None
    _szs_dir = None
    tag_retro = None
    prefix_list = None
    suffix_list = None
    tags_color = None

    def __init__(self, name: str = " ", author: str = "Nintendo", special: str = "T11", music: str = "T11",
                 sha1: str = None, since_version: str = None, score: int = -1, warning: int = 0,
                 version: str = None, tags: list = None, is_in_group: bool = False, weight: int = 1, *args, **kwargs):
        """
        Track class
        :param name: track name
        :param author: track creator(s)
        :param special: track special slot
        :param music: track music slot
        :param new: is the track original or from an older game
        :param sha1: track sha1
        :param since_version: since when version did the track got added to the mod
        :param score: what it the score of the track
        :param warning: what is the warn level of the track (0 = none, 1 = minor bug, 2 = major bug)
        :param track_version: version of the track
        :param tags: a list of tags that correspond to the track

        :param args: /
        :param kwargs: /
        """

        self.name = name  # Track name
        self.author = author  # Track author
        self.sha1 = sha1  # Track sha1 from wszst SHA1
        self.special = special  # Special slot of the track
        self.music = music  # Music of the track
        self.since_version = since_version  # Since which version is this track available
        self.score = score  # Track score between 1 and 3 stars
        self.warning = warning  # Track bug level (1 = minor, 2 = major)
        self.version = version
        self.tags = tags if tags else []
        self.weight = weight

        self._is_in_group = is_in_group

    def __repr__(self) -> str:
        """
        track representation when printed
        :return: track information
        """
        return f"{self.name} sha1={self.sha1} score={self.score}"

    def check_wu8_sha1(self) -> int:
        """
        check if track wu8 sha1 is correct
        :return: 0 if yes, -1 if no
        """
        return check_file_sha1(self.get_wu8_file(), self.sha1)

    def check_szs_sha1(self) -> int:
        """
        check if track szs sha1 is correct
        :return: 0 if yes, -1 if no
        """
        return check_file_sha1(self.get_szs_file(), self.sha1)

    def get_wu8_file(self): return f"{self._wu8_dir}/{self.sha1}.wu8"
    def get_szs_file(self): return f"{self._szs_dir}/{self.sha1}.szs"

    def convert_wu8_to_szs(self) -> None:
        """
        convert track to szs
        """

        szs_file = self.get_szs_file()
        wu8_file = self.get_wu8_file()

        if os.path.exists(szs_file) and os.path.getsize(szs_file) < 1000:
            os.remove(szs_file)  # File under this size are corrupted

        if not self.check_szs_sha1():  # if sha1 of track's szs is incorrect or track's szs does not exist
            if os.path.exists(wu8_file):
                szs.normalize(
                    src_file=wu8_file,
                    dest_file=szs_file
                )
            else:
                raise MissingTrackWU8()

    def get_author_str(self) -> str:
        """
        :return: the list of authors with ", " separating them
        """
        return self.author if type(self.author) == str else ", ".join(self.author)

    def get_ctfile(self, race=False, filter_random_new=None, *args, **kwargs) -> str:
        """
        get ctfile text to create CTFILE.txt and RCTFILE.txt
        :param filter_random_new: function to decide if the track should be used by the "random new" option
        :param race: is it a text used for Race_*.szs ?
        :return: ctfile definition for the track
        """
        track_type = "T"
        track_flag = 0x00 if self.tag_retro in self.tags else 0x01
        if filter_random_new: track_flag = 0x01 if filter_random_new(self) else 0x00

        if self._is_in_group:
            track_type = "H"
            track_flag |= 0x04

        ctfile_track = f'  {track_type} {self.music}; {self.special}; {hex(track_flag)}; '

        if race:
            ctfile_track += (
                f'"-"; '  # track path, not used in Race_*.szs, save a bit of space
                f'"{self.get_track_formatted_name(*args, **kwargs)}\\n{self.get_author_str()}"; '
                # only in race show author's name
                f'"-"\n'  # sha1, not used in Race_*.szs, save a bit of space
            )

        else:
            ctfile_track += (
                f'"{self.sha1}"; '  # track path
                f'"{self.get_track_formatted_name(*args, **kwargs)}"; '  # track text shown ig
                f'"{self.sha1}"\n' # sha1
            )

        return ctfile_track

    def select_tag(self, tag_list: list) -> str:
        for tag in self.tags:
            if tag in tag_list: return tag
        return ""

    def get_track_formatted_name(self, filter_highlight=None, *args, **kwargs) -> str:
        """
        get the track name with score, color, ...
        :param ct_config: ct_config for tags configuration
        :param filter_highlight: filter function to decide if the track should be filtered.
        :return: the name of the track with colored prefix, suffix
        """
        if not filter_highlight: filter_highlight = lambda track: False

        hl_prefix = ""  # highlight
        hl_suffix = ""
        prefix = self.select_tag(self.prefix_list)  # tag prefix
        suffix = self.select_tag(self.suffix_list)  # tag suffix
        star_prefix = ""  # star
        star_suffix = ""
        star_text = ""

        if 0 <= self.score <= 5:
            star_text = f"\\\\x{0xFF10 + self.score:04X}"
            star_prefix = "\\\\c{YOR2}"  # per default, stars are colored in gold
            star_suffix = "\\\\c{off} "
            if 0 < self.warning <= 3:
                star_prefix = warning_color[self.warning]

        if filter_highlight(self): hl_prefix, hl_suffix = "\\\\c{blue1}", "\\\\c{off}"

        if prefix: prefix = "\\\\c{" + self.tags_color[prefix] + "}" + prefix + "\\\\c{off} "
        if suffix: suffix = " (\\\\c{" + self.tags_color[suffix] + "}" + suffix + "\\\\c{off})"

        name = f"{star_prefix}{star_text}{star_suffix}{prefix}{hl_prefix}{self.name}{hl_suffix}{suffix}"
        return name

    def get_track_name(self, ct_config, *args, **kwargs) -> str:
        """
        get the track name without score, color...
        :return: track name
        """
        return f"{self.select_tag(ct_config.prefix_list)}{self.name}{self.select_tag(ct_config.suffix_list)}"

    def load_from_json(self, track_json: dict):
        """
        load the track from a dictionary
        :param track_json: track's dictionary
        """
        self.__init__(**track_json)

        return self

    def create_from_track_file(self, track_file: str) -> None:
        pass

    def copy(self):
        new = type(self)()
        for k, v in self.__dict__.items():
            setattr(new, k, v)
        return new

    def get_tracks(self): yield self


class TrackGroup(Track):
    def __init__(self, tracks: list = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tracks = tracks if tracks else []

    def load_from_json(self, group_json: dict, *args, **kwargs):
        for key, value in group_json.items():  # load all value in the json as class attribute
            if key == "group":
                for track_json in value:
                    track = Track(is_in_group=True, *args, **kwargs).load_from_json(track_json)
                    self.tracks.extend(
                        [track] * track.weight
                    )

            else:
                setattr(self, key, value)

        return self

    def get_tracks(self):
        for track in self.tracks: yield track

    def get_ctfile(self, *args, **kwargs):
        ctfile_group = f'  T T11; T11; 0x02; "-"; "{self.get_track_formatted_name()}"; "-"\n'
        for track in self.tracks:
            ctfile_group += track.get_ctfile(*args, **kwargs)

        return ctfile_group
