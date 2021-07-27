import requests

from .definition import *
from . import wszst


class Track:
    def __init__(self, name: str = "_", prefix: str = None, suffix: str = None,
                 author="Nintendo", special="T11", music="T11", new=True, sha1: str = None, since_version: str = None,
                 score: int = 0, warning: int = 0, note: str = "", track_wu8_dir: str = "./file/Track-WU8/",
                 track_szs_dir: str = "./file/Track/", *args, **kwargs):
        """
        Track class
        :param name: track name
        :param file_wu8: path to its wu8 file
        :param file_szs: path to its szs file
        :param prefix: track prefix (often original console or game)
        :param suffix: track suffix (often for variation like Boost or Night)
        :param author: track creator
        :param special: track special slot
        :param music: track music slot
        :param new: is the track original or from an older game
        :param sha1: track sha1
        :param since_version: since when version did the track got added to the mod
        :param score: what it the score of the track
        :param warning: what is the warn level of the track (0 = none, 1 = minor bug, 2 = major bug)
        :param note: note about the track
        :param track_wu8_dir: where is stored the track wu8
        :param track_szs_dir: where is stored the track szs
        :param args: /
        :param kwargs: /
        """

        self.name = name                    # Track name
        self.prefix = prefix                # Prefix, often used for game or original console like Wii U, DS, ...
        self.suffix = suffix                # Suffix, often used for variety like Boost, Night, ...
        self.author = author                # Track author
        self.sha1 = sha1                    # Track sha1 from wszst SHA1
        self.special = special              # Special slot of the track
        self.music = music                  # Music of the track
        self.new = new                      # Is the track new
        self.since_version = since_version  # Since which version is this track available
        self.score = score                  # Track score between 1 and 3 stars
        self.warning = warning              # Track bug level (1 = minor, 2 = major)
        self.note = note                    # Note about the track
        self.track_wu8_dir = track_wu8_dir
        self.track_szs_dir = track_szs_dir
        self.file_wu8 = f"{track_wu8_dir}/{self.get_track_name()}.wu8"
        self.file_szs = f"{track_szs_dir}/{self.get_track_name()}.szs"

    def __repr__(self) -> str:
        """
        track representation when printed
        :return: track information
        """
        return f"{self.get_track_name()} sha1={self.sha1} score={self.score}"

    def check_sha1(self) -> int:
        """
        check if track wu8's sha1 is correct
        :return: 0 if yes, -1 if no
        """
        if wszst.szs.sha1(self.file_wu8) == self.sha1: return 0
        else: return -1

    def convert_wu8_to_szs(self) -> None:
        """
        convert track to szs
        """
        wszst.szs.normalize(src_file=self.file_wu8)

    def download_wu8(self, github_content_root: str) -> int:
        """
        download track wu8 from github
        :param github_content_root: url to github project root
        :return: 0 if correctly downloaded, 1 if no need to download, 3 if track size is incorrect, -1 if error
        """
        returncode = 0

        dl = requests.get(github_content_root + self.file_wu8, allow_redirects=True, stream=True)
        if os.path.exists(self.file_wu8):
            if int(dl.headers['Content-Length']) == os.path.getsize(self.file_wu8):
                return 1
            else:
                returncode = 3

        if dl.status_code == 200:  # if page is found
            with open(self.file_wu8, "wb") as file:
                chunk_size = 524288
                for i, chunk in enumerate(dl.iter_content(chunk_size=chunk_size)):
                    file.write(chunk)
                    file.flush()
            return returncode
        else:
            print(f"error {dl.status_code} {self.file_wu8}")
            return -1

    def get_ctfile(self, race=False, *args, **kwargs) -> str:
        """
        get ctfile text to create CTFILE.txt and RCTFILE.txt
        :param race: is it a text used for Race_*.szs ?
        :return: ctfile definition for the track
        """
        ctfile_text = (
            f'  T {self.music}; '
            f'{self.special}; '
            f'{"0x01" if self.new else "0x00"}; '
        )
        if not race:
            ctfile_text += (
                f'"{self.get_track_name()}"; '  # track path
                f'"{self.get_track_formatted_name(*args, **kwargs)}"; '  # track text shown ig
                f'"-"\n')  # sha1, useless for now.
        else:
            ctfile_text += (
                f'"-"; '  # track path, not used in Race_*.szs, save a bit of space
                f'"{self.get_track_formatted_name(*args, **kwargs)}\\n{self.author}"; '  # only in race show author's name
                f'"-"\n'  # sha1, useless for now.
            )

        return ctfile_text

    def get_track_formatted_name(self, highlight_version: str = None) -> str:
        """
        get the track name with score, color, ...
        :param highlight_version: if a specific version need to be highlighted.
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

        if self.since_version == highlight_version:
            hl_prefix, hl_suffix = "\\\\c{blue1}", "\\\\c{off}"

        if self.prefix in trackname_color:
            prefix = trackname_color[self.prefix] + " "
        if self.suffix in trackname_color:
            suffix = "(" + trackname_color[self.suffix] + ")"

        name = (star_text + prefix + hl_prefix + self.name + hl_suffix + suffix)
        name = name.replace("_", " ")
        return name

    def get_track_name(self) -> str:
        """
        get the track name without score, color...
        :return: track name
        """
        prefix = (self.prefix + " ") if self.prefix else ""
        suffix = (" (" + self.suffix + ")") if self.suffix else ""

        name = (prefix + self.name + suffix)
        return name

    def load_from_json(self, track_json: dict) -> None:
        """
        load the track from a dictionary
        :param track_json: track's dictionnary
        """
        for key, value in track_json.items():  # load all value in the json as class attribute
            setattr(self, key, value)

        self.file_wu8 = f"{self.track_wu8_dir}/{self.get_track_name()}.wu8"
        self.file_szs = f"{self.track_szs_dir}/{self.get_track_name()}.szs"
