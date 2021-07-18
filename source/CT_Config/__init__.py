class CT_Config:
    def __init__(self, version: str = None):
        self.version = version
        self.ordered_cups = []
        self.unordered_tracks = []
        self.all_tracks = []
        self.all_version = {version}

    from .add_ordered_cup import add_ordered_cup
    from .add_unordered_track import add_unordered_track
    from .create_ctfile import create_ctfile
    from .get_cticon import get_cticon
    from .load_ctconfig_file import load_ctconfig_file
    from .load_ctconfig_json import load_ctconfig_json
    from .search_tracks import search_tracks
