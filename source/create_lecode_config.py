import json


def create_lecode_config(self):
    def get_star_text(track):
        if "score" in track:
            if track["score"] > 0:
                return "★" * track["score"] + "☆" * (3 - track["score"]) + " "
        return ""

    def get_ctfile_text(track):
        track_name = track["name"].replace("_", "")
        return f'  T {track["music"]}; ' + \
               f'{track["special"]}; ' + \
               f'{"0x01" if track["new"] else "0x00"}; ' + \
               f'"{track["name"]}"; ' + \
               f'"{get_star_text(track)}{track_name}"; ' + \
               f'"-"\n'

    def get_rctfile_text(track):
        track_name = track["name"].replace("_", "")
        return f'  T {track["music"]}; ' + \
               f'{track["special"]}; ' + \
               f'{"0x01" if track["new"] else "0x00"}; ' + \
               f'"-"; ' + \
               f'"{get_star_text(track)}{track_name}\\n{track["author"]}"; ' + \
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

        for cup in ctconfig["cup"]: # defined cup section
            _cup_config = ctconfig["cup"][cup]
            if int(cup) >= 9:  # Course qui ne sont ni les originales, ni les courses aléatoires.
                cup = f'\nC "{_cup_config["name"]}"\n'
                ctfile.write(cup)
                rctfile.write(cup)

                for course in _cup_config["courses"]:
                    _course_config = _cup_config["courses"][course]
                    ctfile.write(get_ctfile_text(_course_config))
                    rctfile.write(get_rctfile_text(_course_config))

        for i, _course_config in enumerate(ctconfig["tracks_list"]):  # undefined cup section
            if i % 4 == 0:
                cup = f'\nC "TL{i//4}"\n'
                ctfile.write(cup)
                rctfile.write(cup)

            ctfile.write(get_ctfile_text(_course_config))
            rctfile.write(get_rctfile_text(_course_config))

        for _ in range(1, 4-(i%4)):  # Complete cup if track are missing
            ctfile.write(f'  T T44; T44; 0x00; "_"; ""; "-"\n')
            rctfile.write(f'  T T44; T44; 0x00; "_"; ""; "-"\n')
