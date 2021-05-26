import json


def create_lecode_config(self):
    with open("./ct_config.json") as f:
        ctconfig = json.load(f)
    with open("./file/CTFILE.txt", "w") as ctfile, open("./file/RCTFILE.txt", "w") as rctfile:

        header = "#CT-CODE\n" +\
                 "[RACING-TRACK-LIST]\n" +\
                 "%LE-FLAGS=1\n" +\
                 "%WIIMM-CUP=1\n" +\
                 "N N$SWAP | N$F_WII\n\n"
        ctfile.write(header)
        rctfile.write(header)

        for cup in ctconfig["cup"]:
            _cup_config = ctconfig["cup"][cup]
            if int(cup) >= 9:  # Course qui ne sont ni les originales, ni les courses aléatoires.
                cup = f'\nC "{_cup_config["name"]}"\n'
                ctfile.write(cup)
                rctfile.write(cup)

                for course in _cup_config["courses"]:
                    _course_config = _cup_config["courses"][course]
                    star = ""
                    if "score" in _course_config:
                        if _course_config["score"] > 0:
                            star = "★"*_course_config["score"]+"☆"*(3-_course_config["score"])+" "

                    ctfile.write(f'  T {_course_config["music"]}; ' +
                                 f'{_course_config["special"]}; ' +
                                 f'{"0x01" if _course_config["new"] else "0x00"}; ' +
                                 f'"{_course_config["name"]}"; ' +
                                 f'"{star}{_course_config["name"]}"; ' +
                                 f'"-"\n')

                    rctfile.write(f'  T {_course_config["music"]}; ' +
                                  f'{_course_config["special"]}; ' +
                                  f'{"0x01" if _course_config["new"] else "0x00"}; ' +
                                  f'"-"; ' +
                                  f'"{star}{_course_config["name"]}\\n{_course_config["author"]}"; ' +
                                  f'"-"\n')