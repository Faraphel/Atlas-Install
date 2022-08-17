import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from source.mkw.ModConfig import ModConfig


self = __import__(__name__)
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


def translate_external(mod_config: "ModConfig", language: str, message_texts: dict[str, str], default: str = "") -> str:
    """
    Translate any message that is not from the game.
    :param mod_config: the ModConfig object
    :param language: the language to translate to
    :param message_texts: a dictionary with the translation
    :param default: the default message if no translation are found
    :return: the translated message
    """
    message = message_texts.get(language)
    if message is None: message = message_texts.get("*")
    if message is None: message = default
    return mod_config.multiple_safe_eval(message)()


