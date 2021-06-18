import json


def change_option(self, option, value, restart=False):
    if type(value) in [str, int, bool]: self.option[option] = value
    else: self.option[option] = value.get()
    with open("./option.json", "w", encoding="utf-8") as f: json.dump(self.option, f, ensure_ascii=False)
    if restart: self.restart()


def load_option(self):
    with open("./option.json", encoding="utf-8") as f: self.option = json.load(f)