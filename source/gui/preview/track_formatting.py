import tkinter
from tkinter import ttk
import re

from source.mkw.MKWColor import MKWColor

ModConfig: any


class Window(tkinter.Toplevel):
    def __init__(self, mod_config: "ModConfig"):
        super().__init__()

        self.mod_config = mod_config

        self.entry_format_input = ttk.Entry(self, width=100)
        self.entry_format_input.grid(row=1, column=1, sticky="NEWS")
        self.entry_format_input.bind("<Return>", self.preview)

        self.track_preview = tkinter.Text(self, background="black", foreground=MKWColor("off").color_code)
        self.track_preview.grid(row=2, column=1, sticky="NEWS")

        for color in MKWColor.get_all_colors():
            self.track_preview.tag_configure(color.bmg, foreground=color.color_code)
        self.track_preview.tag_configure("error", background="red", foreground="white")

    def preview(self, event: tkinter.Event = None):
        """
        Preview all the tracks name with the track format
        :return:
        """
        self.track_preview.delete(1.0, tkinter.END)

        # insert all the tracks representation
        for track in self.mod_config.get_tracks():
            try:
                track_repr = track.repr_format(
                    self.mod_config, self.entry_format_input.get()
                )

                offset: int = 0  # the color tag is removed at every sub, so keep track of the offset
                tags: list[tuple[int | None, str | None]] = []  # list of all the position of the tags, with the offset

                def tag_format(match: re.Match):
                    """
                    Get the position of the tag and the corresponding color. Remove the tag from the string
                    """
                    nonlocal offset, tags

                    # add the position of the tag start
                    tags.append((match.span()[0] - offset, match.group("color_name")))
                    offset += len(match.group())  # add the tag len to the offset since it is removed
                    return ""  # remove the tag

                # insert into the text the track_repr without the tags
                self.track_preview.insert(
                    tkinter.END,
                    re.sub(r"\\c{(?P<color_name>.*?)}", tag_format, track_repr) + "\n"
                )

                # color every part of the track_repr with the position and color got in the re.sub
                for (pos_start, tag_start), (pos_end, tag_end) in zip(tags, tags[1:] + [(None, None)]):
                    self.track_preview.tag_add(
                        tag_start,
                        f"end-1c-1l+{pos_start}c",
                        "end-1c" + (f"-1l+{pos_end}c" if pos_end is not None else "")
                    )

            except Exception as exc:
                formatted_exc = str(exc).replace('\n', ' ')
                self.track_preview.insert(tkinter.END, f"< Error: {formatted_exc} >\n")
                self.track_preview.tag_add("error", "end-1c-1l", "end-1c")
