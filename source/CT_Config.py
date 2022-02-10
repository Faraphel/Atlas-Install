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
                 tag_retro: str = "Retro", default_track: dict = None, pack_path: str = "",
                 file_process: dict = None, file_structure: dict = None, default_sort: str = "",
                 cup: list = None, tracks_list: list = None, add_original_track_prefix: bool = True,
                 swap_original_order: bool = True, keep_original_track: bool = True,
                 enable_random_cup: bool = True, arenas: list = None,
                 *args, **kwargs):

        self.version = version
        self.name = name
        self.nickname = nickname if nickname else name
        self.game_variant = game_variant  # this is the "60" part in RMCP60 for example
        self.region = region
        self.cheat_region = cheat_region

        self.add_original_track_prefix = add_original_track_prefix
        self.swap_original_order = swap_original_order
        self.keep_original_track = keep_original_track  # display issue, bad bmg.
        self.enable_random_cup = enable_random_cup

        self.ordered_cups = []
        self.unordered_tracks = []
        self.arenas = []

        self.default_track = default_track

        self.pack_path = pack_path
        self.sort_track_attr = default_sort

        self.file_process = file_process
        self.file_structure = file_structure

        self.filter_track_selection = lambda track: True
        self.filter_track_highlight = lambda track: False
        self.filter_track_random_new = lambda track: getattr(track, "new", False)

        self.sort_track_attr = default_sort

        self.default_track = Track().load_from_json(default_track if default_track else {})
        Cup.default_track = self.default_track

        for id, cup_json in enumerate(cup if cup else []):
            # tracks with defined order
            cup = Cup(id=id)
            cup.load_from_json(cup_json)
            self.ordered_cups.append(cup)

        for track_json in tracks_list if tracks_list else []:
            # unordered tracks
            track = get_trackdata_from_json(track_json)
            self.unordered_tracks.extend([track] * track.weight)

        for arena_json in arenas if arenas else []:
            # arena
            arena_json["is_arena"] = True
            arena = get_trackdata_from_json(arena_json)
            self.arenas.append(arena)

        if pack_path:
            with open(f"{pack_path}/file_process.json", encoding="utf8") as fp_file:
                self.file_process = json.load(fp_file)
            with open(f"{pack_path}/file_structure.json", encoding="utf8") as fs_file:
                self.file_structure = json.load(fs_file)

            fileprocess_placement = self.file_process.get('placement', {})

            dir = fileprocess_placement.get('cup_icon_dir', "/ct_icons/")
            Cup.icon_dir = f"{self.pack_path}/file/{dir}/"

            wu8_dirname = fileprocess_placement.get("track_dir", "/Track-WU8/")
            Track._wu8_dir = f"{self.pack_path}/file/{wu8_dirname}/"

        Track._szs_dir = "./file/Track/"
        Track.tag_retro = tag_retro if tag_retro else {}
        Track.prefix_list = prefix_list if prefix_list else []
        Track.suffix_list = suffix_list if suffix_list else []
        Track.tags_color = tags_color if tags_color else {}

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

            lecode_flags = []
            if not self.keep_original_track: lecode_flags.append("N$NONE")
            else:
                lecode_flags.append("N$SHOW")
                if self.add_original_track_prefix: lecode_flags.append("N$F_WII")
                if self.swap_original_order: lecode_flags.append("N$SWAP")

            header = (
                "#CT-CODE\n"
                "[RACING-TRACK-LIST]\n"
                "%LE-FLAGS=1\n"
                f"%WIIMM-CUP={int(self.enable_random_cup)}\n"
                f"N {' | '.join(lecode_flags)}\n"
                "\n"
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

            if self.arenas:
                ctfile.write("\n"); rctfile.write("\n")

                for arena in self.arenas:
                    ctfile.write(arena.get_ctfile(race=False, **kwargs))
                    rctfile.write(arena.get_ctfile(race=True, **kwargs))

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

        default_cups = ["left", "right"]

        if self.keep_original_track:
            if self.swap_original_order:
                default_cups.extend(
                    ["mushroom", "shell", "flower", "banana",
                     "star", "leaf", "special", "lightning"]
                )
            else:
                default_cups.extend(
                    ["mushroom", "flower", "star", "special",
                     "shell", "banana", "leaf", "lightning"]
                )
        if self.enable_random_cup: default_cups.append("random")

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
        self.__init__(pack_path=pack_path, **ctconfig_json)

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

    def get_tracks_and_arenas(self):
        for track in self.get_tracks(): yield track
        for arena in self.arenas: yield arena
