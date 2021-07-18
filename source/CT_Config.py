from PIL import Image, ImageDraw, ImageFont
import math
import json
import os

from .Cup import Cup
from .Track import Track


def get_cup_icon(i: int, cup_id: str = "_",
                 font_path: str = "./file/SuperMario256.ttf", cup_icon_dir: str = "./file/cup_icon"):
    """
    :param i: cup number
    :param cup_icon_dir: directory to cup icon
    :param font_path: path to the font used to generate icon
    :param cup_id: id of the cup
    :return: cup icon
    """
    if os.path.exists(f"{cup_icon_dir}/{cup_id}.png"):
        cup_icon = Image.open(f"{cup_icon_dir}/{cup_id}.png").resize((128, 128))

    else:
        cup_icon = Image.new("RGBA", (128, 128))
        draw = ImageDraw.Draw(cup_icon)
        font = ImageFont.truetype(font_path, 90)
        draw.text((4 - 2, 4 - 2), "CT", (0, 0, 0), font=font)
        draw.text((4 + 2, 4 - 2), "CT", (0, 0, 0), font=font)
        draw.text((4 - 2, 4 + 2), "CT", (0, 0, 0), font=font)
        draw.text((4 + 2, 4 + 2), "CT", (0, 0, 0), font=font)
        draw.text((4, 4), "CT", (255, 165, 0), font=font)

        font = ImageFont.truetype(font_path, 60)
        draw.text((5 - 2, 80 - 2), "%03i" % i, (0, 0, 0), font=font)
        draw.text((5 + 2, 80 - 2), "%03i" % i, (0, 0, 0), font=font)
        draw.text((5 - 2, 80 + 2), "%03i" % i, (0, 0, 0), font=font)
        draw.text((5 + 2, 80 + 2), "%03i" % i, (0, 0, 0), font=font)

        draw.text((5, 80), "%03i" % i, (255, 165, 0), font=font)
    return cup_icon


class CT_Config:
    def __init__(self, version: str = None):
        self.version = version
        self.ordered_cups = []
        self.unordered_tracks = []
        self.all_tracks = []
        self.all_version = {version}

    def add_ordered_cup(self, cup: Cup):
        """
        :param cup: a Cup object to add as an ordered cup
        :return: ?
        """
        self.ordered_cups.append(cup)
        for track in cup.tracks:
            self.all_version.add(track.since_version)
            self.all_tracks.append(track)

    def add_unordered_track(self, track: Track):
        """
        :param track: a Track object to add as an unordered tracks
        :return: ?
        """
        self.unordered_tracks.append(track)
        self.all_version.add(track.since_version)
        self.all_tracks.append(track)

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
            ctfile.write(header);
            rctfile.write(header)

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

        total_cup_count = len(self.ordered_cups) + math.ceil(len(self.unordered_tracks) / 4)
        ct_icon = Image.new("RGBA", (
        CT_ICON_WIDTH, CT_ICON_WIDTH * (total_cup_count + 2)))  # +2 because of left and right arrow

        icon_files.extend([str(i) for i, cup in enumerate(self.ordered_cups)])  # adding ordered cup id
        icon_files.extend(["_"] * ((len(self.unordered_tracks) // 4) + 1))  # creating unordered track icon

        for i, id in enumerate(icon_files):
            cup_icon = get_cup_icon(i, id)
            ct_icon.paste(cup_icon, (0, i * CT_ICON_WIDTH))

        return ct_icon

    def load_ctconfig_file(self, ctconfig_file: str = "./ct_config.json"):
        """
        :param ctconfig_file: path to the ctconfig file
        :return: ?
        """
        with open(ctconfig_file, encoding="utf-8") as f:
            ctconfig_json = json.load(f)
        self.load_ctconfig_json(ctconfig_json)

    def load_ctconfig_json(self, ctconfig_json: dict):
        """
        :param ctconfig_json: json of the ctconfig to load
        :return: ?
        """
        self.ordered_cups = []
        self.unordered_tracks = []
        self.all_tracks = []

        for cup_json in ctconfig_json["cup"].values():  # tracks with defined order
            cup = Cup()
            cup.load_from_json(cup_json)
            if not cup.locked:  # locked cup are not useful (they are original track or random track)
                self.ordered_cups.append(cup)
                self.all_tracks.extend(cup.tracks)

        for track_json in ctconfig_json["tracks_list"]:  # unordered tracks
            track = Track()
            track.load_from_json(track_json)
            self.unordered_tracks.append(track)
            self.all_tracks.append(track)

        self.version = ctconfig_json["version"]

        self.all_version = set()
        for track in self.all_tracks:
            self.all_version.add(track.since_version)
        self.all_version = sorted(self.all_version)

    def search_tracks(self, values_list=False, not_value=False, **kwargs):
        """
        :param values_list: search track with a value list instead of a single value
        :param not_value: search track that does not have value
        :param kwargs: any track property = any value
        :return: track list respecting condition
        """
        track = self.all_tracks.copy()

        if values_list:
            if not_value:
                filter_func = lambda track: getattr(track, keyword) not in value
            else:
                filter_func = lambda track: getattr(track, keyword) in value
        else:
            if not_value:
                filter_func = lambda track: getattr(track, keyword) != value
            else:
                filter_func = lambda track: getattr(track, keyword) == value

        for keyword, value in kwargs.items():
            track = list(filter(filter_func, track))
        return track