import json
import sys
from pathlib import Path


self = sys.modules[__name__]
self._language_data = {}


def load_language(language: str):
    """
    Load a language file.
    :param language: language code to load
    :return:
    """
    self._language_data = json.loads(Path(f"./assets/language/{language}.json").read_text(encoding="utf8"))


def translate(*text) -> str:
    """
    Translate a text to the loaded language.
    :param text: list of text to translate
    :return: translated text
    """
    return "".join([
        self._language_data["translation"].get(word, word) if isinstance(word, str)
        else str(word)
        for word in text
    ])




