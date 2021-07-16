from .Track import *
from PIL import Image
from .patch_ct_icon import get_cup_icon


class Cup:
    def __init__(self, name: str,
                 track1: Track = EMPTY_TRACK,
                 track2: Track = EMPTY_TRACK,
                 track3: Track = EMPTY_TRACK,
                 track4: Track = EMPTY_TRACK,
                 icon: Image = None):

        self.name = name
        self.tracks = [track1, track2, track3, track4]
        self.icon = icon

    def get_ctfile_cup(self, race=False):
        """
        :param race: is it a text used for Race_*.szs ?
        :return: ctfile definition for the cup
        """
        ctfile_cup = f'\nC "{self.name}"\n'
        for track in self.tracks:
            ctfile_cup += track.get_ctfile_track(race)
        return ctfile_cup

    def get_icon(self, id: int):
        """
        :param id: cup number
        :return: icon of the cup
        """
        return self.icon if self.icon else get_cup_icon(id)
