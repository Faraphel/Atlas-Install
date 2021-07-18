def get_ctfile(self, race=False):
    """
    :param race: is it a text used for Race_*.szs ?
    :return: ctfile definition for the track
    """
    ctfile_text = (
        f'  T {self.music}; '
        f'{self.special}; '
        f'{"0x01" if self.new else "0x00"}; '
    )
    if not race:
        ctfile_text += (
            f'"{self.get_track_name()}"; '  # track path
            f'"{self.get_track_formatted_name()}"; '  # track text shown ig
            f'"-"\n')  # sha1, useless for now.
    else:
        ctfile_text += (
            f'"-"; '  # track path, not used in Race_*.szs, save a bit of space
            f'"{self.get_track_formatted_name()}\\n{self.author}"; '  # only in race show author's name
            f'"-"\n'  # sha1, useless for now.
        )

    return ctfile_text
