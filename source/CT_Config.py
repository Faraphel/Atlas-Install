from PIL import Image, ImageDraw, ImageFont
import math
import json
import os

from source.Cup import Cup
from source.Track import Track, HiddenTrackAttr


class CT_Config:
    def __init__(self, version: str = None, name: str = None, nickname: str = None,
                 game_variant: str = "01", gui=None, region: int = None, cheat_region: int = None,
                 tags_color: dict = {}, prefix_list: list = [], suffix_list: list = [],
                 tag_retro: str = "Retro", default_track: Track = None, pack_path: str = "",
                 file_process: dict = None, file_structure: dict = None):

        self.version = version
        self.name = name
        self.nickname = nickname if nickname else name
        self.game_variant = game_variant  # this is the "60" part in RMCP60 for example
        self.region = region
        self.cheat_region = cheat_region

        self.ordered_cups = []
        self.unordered_tracks = []
        self.all_tracks = []
        self.all_version = {version}
        self.gui = gui
        self.tags_color = tags_color
        self.prefix_list = prefix_list
        self.suffix_list = suffix_list
        self.tag_retro = tag_retro
        self.default_track = default_track

        self.pack_path = pack_path

        self.file_process = file_process
        self.file_structure = file_structure

    def add_ordered_cup(self, cup: Cup) -> None:
        """
        add a cup to the config
        :param cup: a Cup object to add as an ordered cup
        """
        self.ordered_cups.append(cup)
        for track in cup.tracks:
            self.all_version.add(track.since_version)
            self.all_tracks.append(track)

    def add_unordered_track(self, track: Track) -> None:
        """
        add a single track to the config
        :param track: a Track object to add as an unordered tracks
        """
        self.unordered_tracks.append(track)
        self.all_version.add(track.since_version)
        self.all_tracks.append(track)

    def create_ctfile(self, directory: str = "./file/", highlight_version: str = None, sort_track_by: str = None) -> None:
        """
        create a ctfile configuration in a directory
        :param sort_track_by: by which property will track be sorted
        :param highlight_version: highlight a specific version in light blue
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

            # generate cup for undefined track
            unordered_cups = []

            star_value = []
            if not self.gui.boolvar_use_1star_track.get(): star_value.append(1)
            if not self.gui.boolvar_use_2star_track.get(): star_value.append(2)
            if not self.gui.boolvar_use_3star_track.get(): star_value.append(3)

            track_list = self.search_tracks(not_value=True, values_list=True,
                                            only_unordered_track=True, score=star_value)
            if sort_track_by:
                track_list.sort(key=lambda track: getattr(track, sort_track_by, None))

            for i, track in enumerate(track_list):
                if i % 4 == 0:
                    _actual_cup = Cup(name=f"TL{i // 4}", default_track=self.default_track)
                    unordered_cups.append(_actual_cup)
                _actual_cup.tracks[i % 4] = track

            # all cups
            for cup in self.ordered_cups + unordered_cups:
                kwargs = {"highlight_version": highlight_version, "ct_config": self}
                ctfile.write(cup.get_ctfile_cup(race=False, **kwargs))
                rctfile.write(cup.get_ctfile_cup(race=True, **kwargs))

    def get_cup_icon(self, cup_id: [str, int], font_path: str = "./assets/SuperMario256.ttf") -> Image:
        """
        :param cup_id: id of the cup
        :param font_path: path to the font used to generate icon
        :return: cup icon
        """

        dir = self.file_process['placement'].get('cup_icon_dir')
        if not dir: dir = "/ct_icons/"
        cup_icon_dir = f"{self.pack_path}/file/{dir}/"

        if os.path.exists(f"{cup_icon_dir}/{cup_id}.png"):
            cup_icon = Image.open(f"{cup_icon_dir}/{cup_id}.png").resize((128, 128))

        else:
            cup_icon = Image.new("RGBA", (128, 128))
            draw = ImageDraw.Draw(cup_icon)
            font = ImageFont.truetype(font_path, 90)
            draw.text((4, 4), "CT", (255, 165, 0), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
            font = ImageFont.truetype(font_path, 60)
            draw.text((5, 80), "%03i" % cup_id, (255, 165, 0), font=font, stroke_width=2, stroke_fill=(0, 0, 0))

        return cup_icon

    def get_cticon(self) -> Image:
        """
        get all cup icon into a single image
        :return: ct_icon image
        """
        CT_ICON_WIDTH = 128
        icon_files = ["left", "right"]

        total_cup_count = math.ceil(len(self.all_tracks) // 4) + 10  # +10 because left, right, start at 0, 8 normal cup
        ct_icon = Image.new("RGBA", (CT_ICON_WIDTH, CT_ICON_WIDTH * (total_cup_count + 2)))
        # +2 because of left and right arrow

        icon_files.extend(range(total_cup_count))

        for index, cup_id in enumerate(icon_files):
            # index is a number, id can be string or number ("left", 0, 12, ...)
            cup_icon = self.get_cup_icon(cup_id)
            ct_icon.paste(cup_icon, (0, index * CT_ICON_WIDTH))

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

        # default track
        self.default_track = Track(track_wu8_dir=f"{self.pack_path}/file/Track-WU8/")
        if "default_track" in ctconfig_json: self.default_track.load_from_json(ctconfig_json["default_track"])

        for cup_json in ctconfig_json["cup"] if "cup" in ctconfig_json else []:  # tracks with defined order
            cup = Cup(default_track=self.default_track)
            cup.load_from_json(cup_json)
            self.ordered_cups.append(cup)
            self.all_tracks.extend(cup.tracks)

        for track_json in ctconfig_json["tracks_list"] if "tracks_list" in ctconfig_json else []:  # unordered tracks
            track = Track(track_wu8_dir=f"{self.pack_path}/file/Track-WU8/")
            track.load_from_json(track_json)
            self.unordered_tracks.append(track)
            self.all_tracks.append(track)

        self.version = ctconfig_json.get("version")

        if "name" in ctconfig_json: self.name = ctconfig_json["name"]
        self.nickname = ctconfig_json["nickname"] if "nickname" in ctconfig_json else self.name
        if "game_variant" in ctconfig_json: self.game_variant = ctconfig_json["game_variant"]

        for param in ["region", "cheat_region", "tags_color", "prefix_list", "suffix_list", "tag_retro"]:
            setattr(self, param, ctconfig_json.get(param))

        with open(f"{pack_path}/file_process.json", encoding="utf8") as fp_file:
            self.file_process = json.load(fp_file)
        with open(f"{pack_path}/file_structure.json", encoding="utf8") as fs_file:
            self.file_structure = json.load(fs_file)

        return self

    def search_tracks(self, values_list=False, not_value=False, only_unordered_track=False, **kwargs) -> list:
        """
        :param only_unordered_track: only search in unordered track
        :param values_list: search track with a value list instead of a single value
        :param not_value: search track that does not have value
        :param kwargs: any track property = any value
        :return: track list respecting condition
        """
        track = self.all_tracks.copy() if not only_unordered_track else self.unordered_tracks.copy()

        if values_list:
            if not_value: filter_func = lambda track: getattr(track, keyword) not in value
            else: filter_func = lambda track: getattr(track, keyword) in value
        else:
            if not_value: filter_func = lambda track: getattr(track, keyword) != value
            else: filter_func = lambda track: getattr(track, keyword) == value

        for keyword, value in kwargs.items():
            track = list(filter(filter_func, track))
        return track

    def get_all_track_possibilities(self) -> dict:
        possibilities = {}
        for track in self.all_tracks:
            for key, value in track.__dict__.items():
                if key in HiddenTrackAttr: continue
                if not key in possibilities: possibilities[key] = []

                if type(value) == list:
                    for value2 in value: possibilities[key].append(value2)
                else: possibilities[key].append(value)

        for k, v in possibilities.items():
            possibilities[k] = list(sorted(set(filter(None, v))))  # remove duplicate

        return possibilities
