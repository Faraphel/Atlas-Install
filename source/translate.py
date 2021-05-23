import json

def translate(self, text):
    with open("./translation.json") as f:
        translation = json.load(f)
    if self.language in translation:
        _lang_trad = translation[self.language]
        if text in _lang_trad: return _lang_trad[text]
    return text