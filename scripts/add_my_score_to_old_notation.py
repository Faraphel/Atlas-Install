import os
import json
os.chdir("..")
from source.CT_Config import CT_Config

ct_config = CT_Config()
ct_config.load_ctconfig_file()

with open(r"..\GameReview\MKWF\old_notation.json", "r", encoding="utf8") as f:
    old_n = json.load(f)

track_list = list(filter(lambda x: x.since_version == "0.10", ct_config.unordered_tracks))
for track in track_list:
    old_n[track.sha1] = {"216179546427359232": track.score}

with open(r"..\GameReview\MKWF\old_notation.json", "w", encoding="utf8") as f:
    json.dump(old_n, f, ensure_ascii=False)
