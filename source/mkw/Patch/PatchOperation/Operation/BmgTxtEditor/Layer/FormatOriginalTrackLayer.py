import re

from source.mkw.Patch.PatchOperation.Operation.BmgTxtEditor.Layer import *
from source.mkw.Track import Track
from source.wt import bmg

Patch: any


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

            if (id[0] == "T" and int(id[1]) <= 4) or (id[0] == "U" and int(id[1]) == 1): tag = "Wii"
            # If the cup is in the 4 originals tracks cups, use the wii tags
            # If the cup is in the originals arena cup, use the wii tags
            # TODO: tag can't be fetch this way in the JAP version
            else: tag, name = name.split(" ", 1)

            patched_name = Track(
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
