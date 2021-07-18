class Track:
    def __init__(self, name: str = "_", file_wu8: str = None, file_szs: str = None, prefix: str = None, suffix: str = None,
                 author="Nintendo", special="T11", music="T11", new=True, sha1: str = None, since_version: str = None,
                 score: int = 0, warning: int = 0, note: str = "", track_wu8_dir: str = "./file/Track-WU8/",
                 track_szs_dir: str = "./file/Track/", *args, **kwargs):

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
        self.file_wu8 = f"{track_wu8_dir}/{self.get_track_name()}.wu8"
        self.file_szs = f"{track_szs_dir}/{self.get_track_name()}.szs"

    from .__repr__ import __repr__
    from .check_sha1 import check_sha1
    from .convert_wu8_to_szs import convert_wu8_to_szs
    from .download_wu8 import download_wu8
    from .get_ctfile import get_ctfile
    from .get_track_formatted_name import get_track_formatted_name
    from .get_track_name import get_track_name
    from .load_from_json import load_from_json
