from PIL import Image
import math
import json
import os

from source.Cup import Cup
from source.Track import Track, get_trackdata_from_json


class CT_Config:
    def __init__(self, version: str = None, name: str = None, nickname: str = None,
                 game_variant: str = "01", region: int = None, cheat_region: int = None,
                 tags_color: dict = None, prefix_list: list = None, suffix_list: list = None,
                 tag_retro: str = "Retro", default_track: Track = None, pack_path: str = "",
                 file_process: dict = None, file_structure: dict = None, default_sort: str = ""):

        self.version = version
        self.name = name
        self.nickname = nickname if nickname else name
        self.game_variant = game_variant  # this is the "60" part in RMCP60 for example
        self.region = region
        self.cheat_region = cheat_region

        self.ordered_cups = []
        self.unordered_tracks = []

        self.tags_color = tags_color if tags_color else {}
        self.prefix_list = prefix_list if tags_color else []
        self.suffix_list = suffix_list if tags_color else []
        self.tag_retro = tag_retro
        self.default_track = default_track

        self.pack_path = pack_path
        self.sort_track_attr = default_sort

        self.file_process = file_process
        self.file_structure = file_structure

        self.filter_track_selection = lambda track: True
        self.filter_track_highlight = lambda track: False
        self.filter_track_random_new = lambda track: getattr(track, "new", False)

    def add_ordered_cup(self, cup: Cup) -> None:
        """
        add a cup to the config
        :param cup: a Cup object to add as an ordered cup
        """
        self.ordered_cups.append(cup)

    def add_unordered_track(self, track: Track) -> None:
        """
        add a single track to the config
        :param track: a Track object to add as an unordered tracks
        """
        self.unordered_tracks.append(track)

    def unordered_tracks_to_cup(self):
        track_in_cup: int = 4

        track_selection = list(filter(self.filter_track_selection, self.unordered_tracks))
        track_selection.sort(key=lambda track: getattr(track, self.sort_track_attr, 0))

        for cup_id, track_id in enumerate(range(0, len(track_selection), track_in_cup), start=1):
            cup = Cup(id=cup_id, name=f"CT{cup_id}")
            for index, track in enumerate(track_selection[track_id:track_id + track_in_cup]):
                cup.tracks[index] = track
            yield cup

    def create_ctfile(self, directory: str = "./file/") -> None:
        """
        create a ctfile configuration in a directory
        :param directory: create CTFILE.txt and RCTFILE.txt in this directory
        """
        with open(directory + "CTFILE.txt", "w", encoding="utf-8") as ctfile, \
                open(directory + "RCTFILE.txt", "w", encoding="utf-8") as rctfile:
            header = (
                "#CT-CODE\n"
                "[RACING-TRACK-LIST]\n"
                "%LE-FLAGS=1\n"
                "%WIIMM-CUP=1\n"
                "N N$SWAP | N$F_WII\n\n"
            )
            ctfile.write(header); rctfile.write(header)

            # all cups
            kwargs = {
                "filter_highlight": self.filter_track_highlight,
                "filter_random_new": self.filter_track_random_new,
                "ct_config": self
            }

            for cup in self.get_all_cups():
                ctfile.write(cup.get_ctfile(race=False, **kwargs))
                rctfile.write(cup.get_ctfile(race=True, **kwargs))

    def get_tracks(self):
        for data in self.unordered_tracks + self.ordered_cups:
            for track in data.get_tracks(): yield track

    def search_tracks(self, **condition):
        for track in self.get_tracks():
            for property, (possibility, filter_func) in condition.items():
                if not filter_func: filter_func = lambda a, b: a == b
                if not filter_func(getattr(track, property, None), possibility):
                    break
            else:
                yield track

    def get_cup_count(self) -> int:
        return math.ceil(len(self.unordered_tracks) / 4) + len(self.ordered_cups)

    def get_all_cups(self):
        for cup in self.ordered_cups: yield cup
        for cup in self.unordered_tracks_to_cup(): yield cup

    def get_cticon(self) -> Image:
        """
        get all cup icon into a single image
        :return: ct_icon image
        """
        CT_ICON_WIDTH = 128

        default_cups = [
            "left", "right",

            "mushroom", "shell", "flower", "banana",
            "star", "leaf", "special", "lightning",

            "random"
        ]

        total_cup_count = self.get_cup_count() + len(default_cups)  # +10 because left, right, start at 0, 8 normal cup
        ct_icon = Image.new("RGBA", (CT_ICON_WIDTH, CT_ICON_WIDTH * (total_cup_count + 2)))
        # +2 because of left and right arrow

        def icon_cups_generator():
            for id, name in enumerate(default_cups): yield Cup(name=name, id=-id)  # default cup have a negative id
            for cup in self.get_all_cups(): yield cup

        for index, cup in enumerate(icon_cups_generator()):
            # index is a number, id can be string or number ("left", 0, 12, ...)
            ct_icon.paste(cup.get_icon(), (0, index * CT_ICON_WIDTH))

        return ct_icon

    def load_ctconfig_file(self, ctconfig_file: str = "./ct_config.json"):
        """
        load a ctconfig from a json file
        :param ctconfig_file: path to the ctconfig file
        """
        with open(ctconfig_file, encoding="utf-8") as f:
            ctconfig_json = json.load(f)
        self.load_ctconfig_json(ctconfig_json, pack_path=os.path.dirname(ctconfig_file))

        return self

    def load_ctconfig_json(self, ctconfig_json: dict, pack_path: str):
        """
        load ctconfig from a dictionnary
        :param pack_path: path to the pack (parent dir of the ct_config.json)
        :param ctconfig_json: json of the ctconfig to load
        """
        self.ordered_cups = []
        self.unordered_tracks = []
        self.all_tracks = []

        self.pack_path = pack_path

        with open(f"{pack_path}/file_process.json", encoding="utf8") as fp_file:
            self.file_process = json.load(fp_file)
        with open(f"{pack_path}/file_structure.json", encoding="utf8") as fs_file:
            self.file_structure = json.load(fs_file)

        dir = self.file_process['placement'].get('cup_icon_dir') if 'placement' in self.file_process else None
        if not dir: dir = "/ct_icons/"
        Cup.icon_dir = f"{self.pack_path}/file/{dir}/"

        # default track
        self.default_track = Track()
        if "default_track" in ctconfig_json: self.default_track.load_from_json(ctconfig_json["default_track"])
        Cup.default_track = self.default_track

        for id, cup_json in enumerate(ctconfig_json["cup"] if "cup" in ctconfig_json else []):
            # tracks with defined order
            cup = Cup(id=id)
            cup.load_from_json(cup_json)
            self.ordered_cups.append(cup)

        for track_json in ctconfig_json["tracks_list"] if "tracks_list" in ctconfig_json else []:
            # unordered tracks
            track = get_trackdata_from_json(track_json)
            self.unordered_tracks.append(track)

        self.version = ctconfig_json.get("version")

        if "name" in ctconfig_json: self.name = ctconfig_json["name"]
        if "game_variant" in ctconfig_json: self.game_variant = ctconfig_json["game_variant"]
        if "default_sort" in ctconfig_json: self.sort_track_attr = ctconfig_json["default_sort"]
        self.nickname = ctconfig_json["nickname"] if "nickname" in ctconfig_json else self.name

        for param in ["region", "cheat_region", "tags_color", "prefix_list", "suffix_list", "tag_retro"]:
            setattr(self, param, ctconfig_json.get(param))

        wu8_dirname = self.file_process["track_dir"] if "track_dir" in self.file_process else "/Track-WU8/"
        Track._wu8_dir = f"{self.pack_path}/file/{wu8_dirname}/"
        Track._szs_dir = "./file/Track/"
        Track.tag_retro = self.tag_retro
        Track.prefix_list = self.prefix_list
        Track.suffix_list = self.suffix_list
        Track.tags_color = self.tags_color

        return self

    def get_tracks_count(self) -> int:
        return sum(1 for _ in self.get_tracks())

    def get_all_track_possibilities(self) -> list:
        possibilities = set()
        for track in self.get_tracks():
            for key in track.__dict__.keys():
                if key.startswith("_"): continue  # if attr start with a _, the attribute is supposed to be hidden
                possibilities.add(key)

        return sorted(possibilities)
