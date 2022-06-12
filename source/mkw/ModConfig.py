from pathlib import Path
from typing import Generator

from source.mkw import Tag, Color
from source.mkw.Cup import Cup
from source.mkw.Track import Track
import json


# representation of the configuration of a mod
class ModConfig:
    __slots__ = ("name", "nickname", "variant", "region", "tags_prefix", "tags_suffix",
                 "default_track", "_tracks", "version", "original_track_prefix", "swap_original_order",
                 "keep_original_track", "enable_random_cup", "tags_cups", "track_formatting")

    def __init__(self, name: str, nickname: str = None, version: str = None, variant: str = None,
                 tags_prefix: dict[Tag, Color] = None, tags_suffix: dict[Tag, Color] = None,
                 tags_cups: list[Tag] = None, region: dict[int] | int = None,
                 default_track: "Track | TrackGroup" = None, tracks: list["Track | TrackGroup"] = None,
                 original_track_prefix: bool = None, swap_original_order: bool = None,
                 keep_original_track: bool = None, enable_random_cup: bool = None,
                 track_formatting: dict[str, str] = None):

        self.name: str = name
        self.nickname: str = nickname if nickname is not None else name
        self.version: str = version if version is not None else "v1.0.0"
        self.variant: str = variant if variant is not None else "01"
        self.region: dict[int] | int = region if region is not None else 0

        self.tags_prefix: dict[Tag] = tags_prefix if tags_prefix is not None else {}
        self.tags_suffix: dict[Tag] = tags_suffix if tags_suffix is not None else {}
        self.tags_cups: list[Tag] = tags_cups if tags_cups is not None else []

        self.default_track: "Track | TrackGroup" = default_track if default_track is not None else None
        self._tracks: list["Track | TrackGroup"] = tracks if tracks is not None else []
        self.track_formatting: dict[str, str] = {
            "menu_name": "{{ getattr(track, 'name', '/') }}",
            "race_name": "{{ getattr(track, 'name', '/') }}",
            "file_name": "{{ getattr(track, 'sha1', '/') }}"
        } | (track_formatting if track_formatting is not None else {})

        self.original_track_prefix: bool = original_track_prefix if original_track_prefix is not None else True
        self.swap_original_order: bool = swap_original_order if swap_original_order is not None else True
        self.keep_original_track: bool = keep_original_track if keep_original_track is not None else True
        self.enable_random_cup: bool = enable_random_cup if enable_random_cup is not None else True

    def __repr__(self):
        return f"<ModConfig name={self.name} version={self.version}>"

    @classmethod
    def from_dict(cls, config_dict: dict) -> "ModConfig":
        """
        Create a ModConfig from a dict
        :param config_dict: dict containing the configuration
        :return: ModConfig
        """
        kwargs = {
            attr: config_dict.get(attr)
            for attr in cls.__slots__
            if attr not in ["name", "default_track", "_tracks", "tracks"]
            # these keys are treated after or are reserved
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

    def get_ordered_cups(self) -> Generator["Cup", None, None]:
        """
        Get all the cups with cup tags
        :return: cups with cup tags
        """
        # use self._tracks instead of self._get_tracks() because we want the TrackGroup
        # for track that have a tag in self.tags_cups
        for tag_cup in self.tags_cups:
            track_buffer: "Track | TrackGroup" = []
            current_tag_name, current_tag_count = tag_cup, 0

            # every four 4 tracks, create a cup
            for track in filter(lambda track: tag_cup in getattr(track, "tags", []), self._tracks):
                track_buffer.append(track)

                if len(track_buffer) > 4:
                    current_tag_count += 1
                    yield Cup(tracks=track_buffer, cup_id=f"{current_tag_name}-{current_tag_count}")
                    track_buffer = []

            # if there is still tracks in the buffer, create a cup with them and fill with default>
            if len(track_buffer) > 0:
                track_buffer.extend([self.default_track] * (4 - len(track_buffer)))
                yield Cup(tracks=track_buffer, cup_id=f"{current_tag_name}-{current_tag_count+1}")

    def get_unordered_cups(self) -> Generator["Cup", None, None]:
        """
        Get all the cups with no cup tags
        :return: cups with no cup tags
        """
        # for track that have don't have a tag in self.tags_cups
        track_buffer: "Track | TrackGroup" = []
        for track in filter(
            lambda track: not any(item in getattr(track, "tags", []) for item in self.tags_cups),
            self._tracks
        ):
            track_buffer.append(track)

            if len(track_buffer) > 4:
                yield Cup(tracks=track_buffer)
                track_buffer = []

        # if there is still tracks in the buffer, create a cup with them and fill with default
        if len(track_buffer) > 0:
            track_buffer.extend([self.default_track] * (4 - len(track_buffer)))
            yield Cup(tracks=track_buffer)

    def get_cups(self) -> Generator["Cup", None, None]:
        """
        Get all the cups
        :return: cups
        """
        yield from self.get_ordered_cups()
        yield from self.get_unordered_cups()

    def get_ctfile(self) -> str:
        """
        Return the ct_file generated from the ModConfig
        :return: ctfile content
        """
        lecode_flags = filter(lambda v: v is not None, [
            "N$SHOW" if self.keep_original_track else "N$NONE",
            "N$F_WII" if self.original_track_prefix else None,
            "N$SWAP" if self.swap_original_order else None
        ])

        ctfile = (
            f"#CT-CODE\n"  # magic number
            f"[RACING-TRACK-LIST]\n"  # start of the track section
            f"%LE-FLAGS=1\n"  # enable lecode mode
            f"%WIIMM-CUP={int(self.enable_random_cup)}\n"  # enable random cup
            f"N {' | '.join(lecode_flags)}\n"  # other flags to disable default tracks, ...
            f"\n"
        )

        for cup in self.get_cups():
            ctfile += cup.get_ctfile(mod_config=self)

        return ctfile
