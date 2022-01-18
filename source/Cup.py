from source.Track import Track


class Cup:
    def __init__(self,
                 default_track: Track,
                 name: str = None,
                 track1: Track = None,
                 track2: Track = None,
                 track3: Track = None,
                 track4: Track = None,
                 *args, **kwargs):
        """
        class of a cup
        :param name: name of the cup
        :param track1: first track
        :param track2: second track
        :param track3: third track
        :param track4: fourth track
        :param args: other args that I could add in the future
        :param kwargs: other kwargs that I could add in the future
        """

        self.name = name
        self.tracks = [
            track1 if track1 else default_track.copy(),
            track2 if track2 else default_track.copy(),
            track3 if track3 else default_track.copy(),
            track4 if track4 else default_track.copy()
        ]

    def get_ctfile_cup(self, *args, **kwargs) -> str:
        """
        get the ctfile definition for the cup
        :param race: is it a text used for Race_*.szs ?
        :return: ctfile definition for the cup
        """
        ctfile_cup = f'\nC "{self.name}"\n'
        for track in self.tracks:
            ctfile_cup += track.get_ctfile(*args, **kwargs)
        return ctfile_cup

    def load_from_json(self, cup: dict):
        """
        load the cup from a dictionnary
        :param cup: dictionnary cup
        """
        for key, value in cup.items():  # load all value in the json as class attribute
            if key == "tracks":  # if the key is tracks
                for i, track_json in enumerate(value):  # load all tracks from their json
                    self.tracks[i].load_from_json(track_json)
            else:
                setattr(self, key, value)

        return self
