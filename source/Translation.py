import json
from source.definition import gamelang_to_lang

with open("./translation.json", encoding="utf-8") as f:
    translation_dict = json.load(f)


class Translator:
    def __init__(self, common):
        self.common = common

    def translate(self, *texts, gamelang: str = None) -> str:
        """
        translate text into an another language in translation.json file
        :param self: object needing translation to get its language
        :param texts: all text to convert
        :param gamelang: force a destination language to convert track
        :return: translated text
        """
        lang = gamelang_to_lang.get(gamelang, self.common.option.language)
        if lang not in translation_dict: return "".join(texts)  # if no translation language is found

        _lang_trad = translation_dict[lang]
        translated_text = ""
        for text in texts:
            if text in _lang_trad:
                translated_text += _lang_trad[text]
            else:
                print(f"No translation found for ({lang}) {text}")
                translated_text += text

        return translated_text