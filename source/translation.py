import json
from pathlib import Path


language_data = json.loads(Path("./assets/language/en.json").read_text(encoding="utf8"))


def translate(*text) -> str:
    """
    Translate a text to the loaded language.
    :param text: list of text to translate
    :return: translated text
    """
    return "".join([language_data["translation"].get(word, word) for word in text])
