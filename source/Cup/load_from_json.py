def load_from_json(self, cup: dict):
    for key, value in cup.items():  # load all value in the json as class attribute
        if key != "tracks":
            setattr(self, key, value)
        else:  # if the key is tracks
            for i, track_json in value.items():  # load all tracks from their json
                self.tracks[int(i)].load_from_json(track_json)