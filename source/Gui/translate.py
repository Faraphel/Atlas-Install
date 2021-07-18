import json

with open("./translation.json", encoding="utf-8") as f:
    translation_dict = json.load(f)


def translate(self, *texts, lang=None):
    if lang is None:
        lang = self.stringvar_language.get()
    elif lang == "F":
        lang = "fr"
    elif lang == "G":
        lang = "ge"
    elif lang == "I":
        lang = "it"
    elif lang == "S":
        lang = "sp"

    if lang in translation_dict:
        _lang_trad = translation_dict[lang]
        translated_text = ""
        for text in texts:
            if text in _lang_trad:
                translated_text += _lang_trad[text]
            else:
                translated_text += text
        return translated_text

    return "".join(texts)  # if no translation language is found
