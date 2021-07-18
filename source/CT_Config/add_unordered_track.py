from source.Track import Track


def add_unordered_track(self, track: Track):
    """
    :param track: a Track object to add as an unordered tracks
    :return: ?
    """
    self.unordered_tracks.append(track)
    self.all_version.add(track.since_version)
    self.all_tracks.append(track)