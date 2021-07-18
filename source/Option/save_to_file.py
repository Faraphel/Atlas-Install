import json


def save_to_file(self, option_file: str = "./option.json"):
    option_json: dict = self.__dict__  # this return all attribute of the class as a dict
    with open(option_file, "w", encoding="utf-8") as file:
        json.dump(option_json, file, ensure_ascii=False)
