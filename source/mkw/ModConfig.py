from pathlib import Path
from typing import Generator

from source.mkw import Tag, Color
from source.mkw.Track import Track
import json


# representation of the configuration of a mod
class ModConfig:
    __slots__ = ("name", "nickname", "variant", "region", "tags_prefix", "tags_suffix",
                 "default_track", "_tracks", "version", "original_track_prefix", "swap_original_order",
                 "keep_original_track", "enable_random_cup", "tags_cups")

    def __init__(self, name: str, nickname: str = None, version: str = None, variant: str = None,
                 tags_prefix: dict[Tag, Color] = None, tags_suffix: dict[Tag, Color] = None,
                 tags_cups: list[Tag] = None, region: dict[int] | int = None,
                 default_track: "Track | TrackGroup" = None, tracks: list["Track | TrackGroup"] = None,
                 original_track_prefix: bool = None, swap_original_order: bool = None,
                 keep_original_track: bool = None, enable_random_cup: bool = None):

        self.name: str = name
        self.nickname: str = nickname if nickname is not None else name
        self.version: str = version if version is not None else "1.0.0"
        self.variant: str = variant if variant is not None else "01"
        self.region: dict[int] | int = region if region is not None else 0

        self.tags_prefix: dict[Tag] = tags_prefix if tags_prefix is not None else {}
        self.tags_suffix: dict[Tag] = tags_suffix if tags_suffix is not None else {}
        self.tags_cups: dict[Tag] = tags_cups if tags_cups is not None else {}

        self.default_track: "Track | TrackGroup" = default_track if default_track is not None else None
        self._tracks: list["Track | TrackGroup"] = tracks if tracks is not None else []

        self.original_track_prefix: bool = original_track_prefix if original_track_prefix is not None else True
        self.swap_original_order: bool = swap_original_order if swap_original_order is not None else True
        self.keep_original_track: bool = keep_original_track if keep_original_track is not None else True
        self.enable_random_cup: bool = enable_random_cup if enable_random_cup is not None else True

    @classmethod
    def from_dict(cls, config_dict: dict) -> "ModConfig":
        """
        Create a ModConfig from a dict
        :param config_dict: dict containing the configuration
        :return: ModConfig
        """

        kwargs = {
            attr: config_dict.get(attr)
            for attr in ["nickname", "version", "variant", "tags_prefix", "tags_suffix", "tags_cups",
                         "original_track_prefix", "swap_original_order", "keep_original_track", "enable_random_cup"]
        }

        return cls(
            name=config_dict["name"],

            **kwargs,

            default_track=Track.from_dict(config_dict.get("default_track", {})),
            tracks=[Track.from_dict(track) for track in config_dict.get("tracks", [])],
        )

    @classmethod
    def from_file(cls, config_file: str | Path) -> "ModConfig":
        """
        Create a ModConfig from a file
        :param config_file: file containing the configuration
        :return: ModConfig
        """
        if isinstance(config_file, str): config_file = Path(config_file)
        return cls.from_dict(json.loads(config_file.read_text(encoding="utf8")))

    def get_tracks(self) -> Generator["Track", None, None]:
        """
        Get all the track elements
        :return: track elements
        """
        for track in self._tracks:
            yield from track.get_tracks()

