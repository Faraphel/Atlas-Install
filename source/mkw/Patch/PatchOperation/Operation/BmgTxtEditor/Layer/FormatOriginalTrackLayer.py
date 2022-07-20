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
        originals_track = bmg.cat_data(decoded_content, filters={"TRACKS+ARENAS": None})
        new_bmg_lines: list[str] = []

        for line in originals_track.split("\n"):
            if (match := re.match(r"^ {2}(?P<id>.*?)\t= (?P<value>.*)$", line, re.DOTALL)) is None:
                # check if the line match a bmg definition, else ignore
                # bmg definition is : 2 spaces, a bmg id, a tab, an equal sign, a space and the bmg text
                continue

            id = match.group("id")
            name = match.group("value")

            if (id[0] == "T" and int(id[1]) <= 4) or (id[0] == "U" and int(id[1]) == 1): tag = "Wii"
            # If the cup is in the 4 originals tracks cups, use the wii tags
            # If the cup is in the originals arena cup, use the wii tags
            else: tag, name = name.split(" ", 1)

            patched_name = Track(
                name=name,
                tags=[tag]
            ).repr_format(
                patch.mod_config,
                self.template
            )

            new_bmg_lines.append(f"  {id}\t={patched_name}")

        return decoded_content + "\n" + ("\n".join(new_bmg_lines)) + "\n"
        # add every new line to the end of the decoded_bmg, old bmg_id will be overwritten.
