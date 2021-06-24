import json
import os

default_option = {
    "language": "en",
    "format": "FST",
    "disable_download": False,
    "del_track_after_conv": False,
    "dont_check_for_update": False,
    "dont_check_track_sha1": False,
    "process_track": 8
}


def change_option(self, option, value, restart=False):
    if type(value) in [str, int, bool]: self.option[option] = value
    else: self.option[option] = value.get()
    with open("./option.json", "w", encoding="utf-8") as f: json.dump(self.option, f, ensure_ascii=False)
    if restart: self.restart()


def load_option(self):
    if not(os.path.exists("./option.json")):
        with open("./option.json", "w", encoding="utf-8") as f: json.dump(default_option, f, ensure_ascii=False)
    with open("./option.json", encoding="utf-8") as f: self.option = json.load(f)

    for option_key, option_value in default_option.items():
        if not(option_key in self.option):
            self.option[option_key] = option_value