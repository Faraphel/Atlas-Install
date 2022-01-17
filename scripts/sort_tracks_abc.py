import json

with open("../Pack/MKWFaraphel/ct_config.json", encoding="utf8", mode="r") as file:
    ct_config = json.load(file)

get_key = lambda track: track["name"]
ct_config["tracks_list"].sort(key=get_key)

with open("../Pack/MKWFaraphel/ct_config.json", encoding="utf8", mode="w") as file:
    json.dump(ct_config, file, ensure_ascii=False)
