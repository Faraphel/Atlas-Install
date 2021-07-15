from .Track import *
from PIL import Image
from .patch_ct_icon import get_cup_icon


class Cup:
    def __init__(self, name: str, id: int,
                 track1: Track = EMPTY_TRACK,
                 track2: Track = EMPTY_TRACK,
                 track3: Track = EMPTY_TRACK,
                 track4: Track = EMPTY_TRACK,
                 icon: Image = None):

        self.name = name
        self.track1 = track1
        self.track2 = track2
        self.track3 = track3
        self.track4 = track4
        self.icon = icon if icon else create_cup_icon(id)
        self.id = id                # cup number

    def get_ctfile_cup(self):
        pass

    def get_tracks(self):
        return self.track1, self.track2, self.track3, self.track4
