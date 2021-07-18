from source.Cup import Cup
from source.Track import Track


def load_ctconfig_json(self, ctconfig_json: dict):
    """
    :param ctconfig_json: json of the ctconfig to load
    :return: ?
    """
    self.ordered_cups = []
    self.unordered_tracks = []
    self.all_tracks = []

    for cup_json in ctconfig_json["cup"].values():  # tracks with defined order
        cup = Cup()
        cup.load_from_json(cup_json)
        if not cup.locked:  # locked cup are not useful (they are original track or random track)
            self.ordered_cups.append(cup)
            self.all_tracks.extend(cup.tracks)

    for track_json in ctconfig_json["tracks_list"]:  # unordered tracks
        track = Track()
        track.load_from_json(track_json)
        self.unordered_tracks.append(track)
        self.all_tracks.append(track)

    self.version = ctconfig_json["version"]

    self.all_version = set()
    for track in self.all_tracks:
        self.all_version.add(track.since_version)
    self.all_version = sorted(self.all_version)