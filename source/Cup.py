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

    def get_ctfile_cup(self, race=False):
        """
        :param race: is it a text used for Race_*.szs ?
        :return: ctfile definition for the cup
        """
        ctfile_cup = f'\nC "{self.name}"\n'
        for track in self.tracks:
            ctfile_cup += track.get_ctfile(race)
        return ctfile_cup

    def load_from_json(self, cup: dict):
        for key, value in cup.items():  # load all value in the json as class attribute
            if key != "tracks":
                setattr(self, key, value)
            else:  # if the key is tracks
                for i, track_json in value.items():  # load all tracks from their json
                    self.tracks[int(i)].load_from_json(track_json)
