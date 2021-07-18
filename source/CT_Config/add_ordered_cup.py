from source.Cup import Cup


def add_ordered_cup(self, cup: Cup):
    """
    :param cup: a Cup object to add as an ordered cup
    :return: ?
    """
    self.ordered_cups.append(cup)
    for track in cup.tracks:
        self.all_version.add(track.since_version)
        self.all_tracks.append(track)