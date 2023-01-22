import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from source.mkw.ModConfig import ModConfig


_language: str | None = None
_language_data: dict = {}


def load_language(language: str):
    """
    Load a language file.
    :param language: language code to load
    :return:
    """
    global _language, _language_data

    _language = language
    _language_data = json.loads(Path(f"./assets/language/{language}.json").read_text(encoding="utf8"))


def translate(text) -> str:
    """
    Translate a text to the loaded language.
    :param text: list of text to translate
    :return: translated text
    """
    return _language_data.get("translation", {}).get(text, text)


def translate_external(mod_config: "ModConfig", message_texts: dict[str, str], default: str = "") -> str:
    """
    Translate any message that is not from the game.
    :param mod_config: the ModConfig object
    :param message_texts: a dictionary with the translation
    :param default: the default message if no translation are found
    :return: the translated message
    """
    message = message_texts.get(_language)
    if message is None: message = message_texts.get("*")
    if message is None: message = default
    return mod_config.multiple_safe_eval(message, args=["language"])(language=_language)


