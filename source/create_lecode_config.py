import json


def create_lecode_config(self):
    with open("./ct_config.json") as f:
        ctconfig = json.load(f)
    with open("./file/CTFILE.txt", "w") as ctfile:
        ctfile.write(
            "#CT-CODE\n" +
            "[RACING-TRACK-LIST]\n" +
            "%LE-FLAGS=1\n" +
            "%WIIMM-CUP=1\n" +
            "N N$SWAP | N$F_WII\n\n")

        for cup in ctconfig["cup"]:
            _cup_config = ctconfig["cup"][cup]
            if int(cup) >= 9:  # Course qui ne sont ni les originales, ni les courses aléatoires.
                ctfile.write(f'\nC "{_cup_config["name"]}"\n')

                for course in _cup_config["courses"]:
                    _course_config = _cup_config["courses"][course]
                    ctfile.write(f'T {_course_config["music"]}; ' +
                                 f'{_course_config["special"]}; ' +
                                 f'{"0x01" if _course_config["new"] else "0x00"}; ' +
                                 f'"{_course_config["name"]}"; ' +
                                 f'"{_course_config["name"]}"; ' +
                                 f'"-"\n')
