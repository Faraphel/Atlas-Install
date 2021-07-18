from source.Cup import Cup

def create_ctfile(self, directory="./file/"):
    """
    :param directory: create CTFILE.txt and RCTFILE.txt in this directory
    :return: None
    """
    with open(directory + "CTFILE.txt", "w", encoding="utf-8") as ctfile, \
            open(directory + "RCTFILE.txt", "w", encoding="utf-8") as rctfile:
        header = (
            "#CT-CODE\n"
            "[RACING-TRACK-LIST]\n"
            "%LE-FLAGS=1\n"
            "%WIIMM-CUP=1\n"
            "N N$SWAP | N$F_WII\n\n")
        ctfile.write(header); rctfile.write(header)

        # generate cup for undefined track
        unordered_cups = []
        for i, track in enumerate(self.unordered_tracks):
            if i % 4 == 0:
                _actual_cup = Cup(name=f"TL{i // 4}")
                unordered_cups.append(_actual_cup)
            _actual_cup.tracks[i % 4] = track

        # all cups
        for cup in self.ordered_cups + unordered_cups:
            ctfile.write(cup.get_ctfile_cup(race=False))
            rctfile.write(cup.get_ctfile_cup(race=True))