import json
from pathlib import Path


language_data = json.loads(Path("./assets/language/en.json").read_text(encoding="utf8"))


def translate(*text):
    return "".join([language_data["translation"].get(word, word) for word in text])
