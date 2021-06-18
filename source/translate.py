import json


def translate(self, text, lang = None):
    if lang == None: lang = self.stringvar_language.get()
    elif lang == "E": lang = "en"
    elif lang == "G": lang = "ge"
    elif lang == "I": lang = "it"
    elif lang == "S": lang = "sp"

    with open("./translation.json", encoding="utf-8") as f:
        translation = json.load(f)
    if lang in translation:
        _lang_trad = translation[lang]
        if text in _lang_trad: return _lang_trad[text]
        else:
            print(f"no translation for : \"{text}\"")
    return text


def change_language(self):
    with open("./translation.json", encoding="utf-8") as f: translation = json.load(f)
    translation["selected"] = self.stringvar_language.get()
    with open("./translation.json", "w", encoding="utf-8") as f: json.dump(translation, f, ensure_ascii=False)
    self.restart()


def get_language(self):
    with open("./translation.json", encoding="utf-8") as f: translation = json.load(f)
    if "selected" in translation: return translation["selected"]
    else: return "fr"