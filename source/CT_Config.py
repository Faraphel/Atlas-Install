from .Cup import *
import math
from PIL import Image, ImageFont, ImageDraw
import os


def get_cup_icon(i):
    if os.path.exists(f"./file/cup_icon/{id}.png"):
        cup_icon = Image.open(f"./file/cup_icon/{id}.png").resize((128, 128))

    else:
        cup_icon = Image.new("RGBA", (128, 128))
        draw = ImageDraw.Draw(cup_icon)
        font = ImageFont.truetype("./file/SuperMario256.ttf", 90)
        draw.text((4 - 2, 4 - 2), "CT", (0, 0, 0), font=font)
        draw.text((4 + 2, 4 - 2), "CT", (0, 0, 0), font=font)
        draw.text((4 - 2, 4 + 2), "CT", (0, 0, 0), font=font)
        draw.text((4 + 2, 4 + 2), "CT", (0, 0, 0), font=font)
        draw.text((4, 4), "CT", (255, 165, 0), font=font)

        font = ImageFont.truetype("./file/SuperMario256.ttf", 60)
        draw.text((5 - 2, 80 - 2), "%03i" % (i - 10), (0, 0, 0), font=font)  # i-10 because first 8 cup are not
        draw.text((5 + 2, 80 - 2), "%03i" % (i - 10), (0, 0, 0), font=font)  # counted as new, random cup,
        draw.text((5 - 2, 80 + 2), "%03i" % (i - 10), (0, 0, 0), font=font)  # left and right arrow
        draw.text((5 + 2, 80 + 2), "%03i" % (i - 10), (0, 0, 0), font=font)

        draw.text((5, 80), "%03i" % (i - 10), (255, 165, 0), font=font)
        return cup_icon


class CT_Config:
    def __init__(self, version):
        self.version = version
        self.ordered_cups = []
        self.unordered_tracks = []
        self.all_version: set = {version}

    def add_ordered_cup(self, cup: Cup):
        self.ordered_cups.append(cup)
        for track in cup.tracks:
            self.all_version.add(track.since_version)

    def add_unordered_track(self, track: Track):
        self.unordered_tracks.append(track)
        self.all_version.add(track.since_version)

    def get_tracks(self):
        """
        :return: all tracks from the CT_Config
        """
        tracks = []
        for cup in self.ordered_cups:
            tracks.extend(*cup.get_tracks())
        tracks.extend(self.unordered_tracks)

        return tracks

    def search_tracks(self, **kwargs):
        tracks = self.get_tracks()
        for keyword, value in kwargs.items():
            filter(lambda track: getattr(track, keyword) == value, tracks)

    def get_total_tracks_count(self):
        return (len(self.ordered_cups) * 4) + len(self.unordered_tracks)

    def create_ctfile(self, directory="./file/"):
        with open(directory+"CTFILE.txt", "w", encoding="utf-8") as ctfile, \
             open(directory+"RCTFILE.txt", "w", encoding="utf-8") as rctfile:
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

    def get_cticon(self):
        """
        get all cup icon into a single image
        :return: ct_icon image
        """
        CT_ICON_WIDTH = 128
        icon_files = ["left", "right"]

        total_cup_count = math.ceil(self.get_total_tracks_count() / 4)
        ct_icon = Image.new("RGBA", (CT_ICON_WIDTH, CT_ICON_WIDTH * (total_cup_count + 2)))  # +2 because of left and right arrow

        icon_files.extend([cup.id for cup in self.ordered_cups])             # adding ordered cup id
        icon_files.extend(["_"] * ((len(self.unordered_tracks) // 4) + 1))   # creating unordered track icon

        for i, id in enumerate(icon_files):
            cup_icon = get_cup_icon(i)
            ct_icon.paste(cup_icon, (0, i * CT_ICON_WIDTH))

        return ct_icon  # ct_icon.save("./file/ct_icons.tpl.png")
