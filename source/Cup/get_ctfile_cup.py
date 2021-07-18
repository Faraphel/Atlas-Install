def get_ctfile_cup(self, race=False):
    """
    :param race: is it a text used for Race_*.szs ?
    :return: ctfile definition for the cup
    """
    ctfile_cup = f'\nC "{self.name}"\n'
    for track in self.tracks:
        ctfile_cup += track.get_ctfile_track(race)
    return ctfile_cup
