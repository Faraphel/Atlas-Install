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


