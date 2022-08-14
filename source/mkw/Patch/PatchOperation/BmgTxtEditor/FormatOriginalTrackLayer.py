import re
from typing import TYPE_CHECKING

from source.mkw.Patch.PatchOperation.BmgTxtEditor import AbstractLayer
from source.mkw.Track.CustomTrack import CustomTrack
from source.wt import bmg

if TYPE_CHECKING:
    from source.mkw.Patch import Patch


class FormatOriginalTrackLayer(AbstractLayer):
    """
    Represent a layer that patch a bmg with all the originals track formatted
    """

    mode = "format-original-track"

    def __init__(self, template: str):
        self.template = template

    def patch_bmg(self, patch: "Patch", decoded_content: str) -> str:
        original_tracks = bmg.cat_data(decoded_content, filters=["TRACKS+ARENAS"])

        def replacement(match: re.Match) -> str:
            """
            Get the replacement for the bmg line
            :param match: the matched bmg line
            :return: the patched bmg line
            """
            id = match.group("id")
            name = match.group("value")

            retro_tags = {
                "GCN": "GCN",
                "GC": "GCN",  # japanese for GameCube
                "DS": "DS",
                "SNES": "SNES",
                "SFC": "SNES",  # japanese for SNES
                "N64": "N64",
                "64": "N64",  # japanese for N64
                "GBA": "GBA",
            }
            for game_tag, tag in retro_tags.items():
                if name.startswith(game_tag):
                    name = name.removeprefix(game_tag).strip()
                    break
            else: tag = "Wii"

            patched_name = CustomTrack(
                name=name,
                tags=[tag]
            ).repr_format(
                patch.mod_config,
                self.template
            )

            return f"  {id}\t= {patched_name}"

        patched_original_tracks = re.sub(
            r" {2}(?P<id>.*?)\t= (?P<value>.*)",
            replacement,
            original_tracks
        )

        return f"{decoded_content}\n{patched_original_tracks}\n"
