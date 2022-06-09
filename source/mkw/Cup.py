# class that represent a mario kart wii cup
class Cup:
    def __init__(self, track1: "Track" = None, track2: "Track" = None, track3: "Track" = None, track4: "Track" = None):
        self._tracks = [track1, track2, track3, track4]