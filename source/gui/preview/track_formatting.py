import tkinter
from tkinter import ttk
import re

from source.mkw.MKWColor import MKWColor
from source.gui.preview import AbstractPreviewWindow


ModConfig: any


class Window(AbstractPreviewWindow):

    name = "track_formatting"

    def __init__(self, mod_config: "ModConfig", template_variable: tkinter.StringVar = None):
        super().__init__(mod_config, template_variable)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grab_set()

        if template_variable is None: template_variable = tkinter.StringVar()
        self.mod_config = mod_config

        self.entry_template_input = ttk.Entry(self, width=100, textvariable=template_variable)
        self.entry_template_input.grid(row=1, column=1, columnspan=2, sticky="NEWS")
        self.entry_template_input.bind("<Return>", self.preview)

        self.text_track_preview = tkinter.Text(
            self, background="black", foreground=MKWColor("off").color_code, state=tkinter.DISABLED
        )
        self.text_track_preview.grid(row=2, column=1, sticky="NEWS")

        self.scrollbar_track_preview = ttk.Scrollbar(self, command=self.text_track_preview.yview)
        self.scrollbar_track_preview.grid(row=2, column=2, sticky="NEWS")

        self.text_track_preview.configure(yscrollcommand=self.scrollbar_track_preview.set)

        for color in MKWColor.get_all_colors():
            self.text_track_preview.tag_configure(color.bmg, foreground=color.color_code)
        self.text_track_preview.tag_configure("error", background="red", foreground="white")

    def preview(self, event: tkinter.Event = None):
        """
        Preview all the tracks name with the track format
        :return:
        """
        self.text_track_preview.configure(state=tkinter.NORMAL)
        self.text_track_preview.delete(1.0, tkinter.END)

        # insert all the tracks representation
        for track in self.mod_config.get_tracks():
            try:
                track_repr = track.repr_format(
                    self.mod_config, self.entry_template_input.get()
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
                self.text_track_preview.insert(
                    tkinter.END,
                    re.sub(r"\\c{(?P<color_name>.*?)}", tag_format, track_repr) + "\n"
                )

                # color every part of the track_repr with the position and color got in the re.sub
                for (pos_start, tag_start), (pos_end, tag_end) in zip(tags, tags[1:] + [(None, None)]):
                    self.text_track_preview.tag_add(
                        tag_start,
                        f"end-1c-1l+{pos_start}c",
                        "end-1c" + (f"-1l+{pos_end}c" if pos_end is not None else "")
                    )

            except Exception as exc:
                formatted_exc = str(exc).replace('\n', ' ')
                self.text_track_preview.insert(tkinter.END, f"< Error: {formatted_exc} >\n")
                self.text_track_preview.tag_add("error", "end-1c-1l", "end-1c")

        self.text_track_preview.configure(state=tkinter.DISABLED)

