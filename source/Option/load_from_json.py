def load_from_json(self, option_json: dict):
    for key, value in option_json.items():  # load all value in the json as class attribute
        setattr(self, key, value)