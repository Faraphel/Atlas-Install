import json


def translate(self, text):
    with open("./translation.json", encoding="utf-8") as f:
        translation = json.load(f)
    if self.language in translation:
        _lang_trad = translation[self.language]
        if text in _lang_trad: return _lang_trad[text]
    return text


def change_language(self):
    with open("./translation.json", encoding="utf-8") as f: translation = json.load(f)
    translation["selected"] = self.listbox_language.get()
    with open("./translation.json", "w", encoding="utf-8") as f: json.dump(translation, f)

    self.restart()


def get_language(self):
    with open("./translation.json", encoding="utf-8") as f: translation = json.load(f)
    if "selected" in translation: return translation["selected"]
    else: return "fr"