def search_tracks(self, values_list=False, not_value=False, **kwargs):
    """
    :param values_list: search track with a value list instead of a single value
    :param not_value: search track that does not have value
    :param kwargs: any track property = any value
    :return: track list respecting condition
    """
    track = self.all_tracks.copy()

    if values_list:
        if not_value: filter_func = lambda track: getattr(track, keyword) not in value
        else: filter_func = lambda track: getattr(track, keyword) in value
    else:
        if not_value: filter_func = lambda track: getattr(track, keyword) != value
        else: filter_func = lambda track: getattr(track, keyword) == value

    for keyword, value in kwargs.items():
        track = list(filter(filter_func, track))
    return track