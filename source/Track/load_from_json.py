def load_from_json(self, track_json: dict):
    for key, value in track_json.items():  # load all value in the json as class attribute
        setattr(self, key, value)
