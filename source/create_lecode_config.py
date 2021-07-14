import json
from .definition import *


def create_lecode_config(self):
    try:
        def get_star_text(track):
            if "warning" in track: warning = "!" * track["warning"]
            else: warning = ""

            if "score" in track:
                if 0 < track["score"] <= 3:
                    return "★" * track["score"] + "☆" * (3 - track["score"]) + warning + " "
            return ""

        def get_ctfile_text(track, race=False):
            if race:
                return f'  T {track["music"]}; ' + \
                       f'{track["special"]}; ' + \
                       f'{"0x01" if track["new"] else "0x00"}; ' + \
                       f'"-"; ' + \
                       f'"{get_star_text(track)}{get_trackctname(track=track)}\\n{track["author"]}"; ' + \
                       f'"-"\n'
            else:
                return f'  T {track["music"]}; ' + \
                       f'{track["special"]}; ' + \
                       f'{"0x01" if track["new"] else "0x00"}; ' + \
                       f'"{get_trackctname(track=track)}"; ' + \
                       f'"{get_star_text(track)}{get_trackctname(track=track)}"; ' + \
                       f'"-"\n'

        with open("./ct_config.json", encoding="utf-8") as f:
            ctconfig = json.load(f)

        with open("./file/CTFILE.txt", "w", encoding="utf-8") as ctfile, \
             open("./file/RCTFILE.txt", "w", encoding="utf-8") as rctfile:

            header = "#CT-CODE\n" +\
                     "[RACING-TRACK-LIST]\n" +\
                     "%LE-FLAGS=1\n" +\
                     "%WIIMM-CUP=1\n" +\
                     "N N$SWAP | N$F_WII\n\n"
            ctfile.write(header)
            rctfile.write(header)

            for cup in ctconfig["cup"]:  # defined cup section
                _cup_config = ctconfig["cup"][cup]
                if int(cup) >= 9:  # Track that are not original and not random selection
                    cup = f'\nC "{_cup_config["name"]}"\n'
                    ctfile.write(cup)
                    rctfile.write(cup)

                    for course in _cup_config["courses"]:
                        _course_config = _cup_config["courses"][course]
                        ctfile.write(get_ctfile_text(_course_config, race=False))
                        rctfile.write(get_ctfile_text(_course_config, race=True))

            tracks_list = ctconfig["tracks_list"]
            if not self.boolvar_use_1star_track.get():  # if 1 star track are disabled, remove them
                tracks_list = list(filter(lambda track: track.get("score") != 1, tracks_list))
            if not self.boolvar_use_2star_track.get():  # if 2 stars track are disabled, remove them
                tracks_list = list(filter(lambda track: track.get("score") != 2, tracks_list))
            if not self.boolvar_use_3star_track.get():  # if 3 stars track are disabled, remove them
                tracks_list = list(filter(lambda track: track.get("score") != 3, tracks_list))
            #  using dict.get allow track that with no "score" attribute to not raise an exception by returning None

            for i, _course_config in enumerate(tracks_list):  # undefined cup section
                if i % 4 == 0:
                    cup = f'\nC "TL{i//4}"\n'
                    ctfile.write(cup)
                    rctfile.write(cup)

                ctfile.write(get_ctfile_text(_course_config, race=False))
                rctfile.write(get_ctfile_text(_course_config, race=True))

            for _ in range(1, 4-(i%4)):  # Complete cup if track are missing
                ctfile.write(EMPTY_TRACK)
                rctfile.write(EMPTY_TRACK)

    except:
        self.log_error()
