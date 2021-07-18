from source.Track import Track


class Cup:
    def __init__(self, name: str = None,
                 track1: Track = None,
                 track2: Track = None,
                 track3: Track = None,
                 track4: Track = None, locked: bool = False,
                 *args, **kwargs):

        self.name = name
        self.tracks = [
            track1 if track1 else Track(),
            track2 if track2 else Track(),
            track3 if track3 else Track(),
            track4 if track4 else Track()
        ]
        self.locked = locked

    from .get_ctfile_cup import get_ctfile_cup
    from .load_from_json import load_from_json
